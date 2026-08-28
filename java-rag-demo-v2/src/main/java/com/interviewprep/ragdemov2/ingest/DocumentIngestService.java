package com.interviewprep.ragdemov2.ingest;

import com.interviewprep.ragdemov2.config.AppProperties;
import com.interviewprep.ragdemov2.pdf.CorpusPdfGenerator;
import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.Metadata;
import dev.langchain4j.data.document.parser.apache.pdfbox.ApachePdfBoxDocumentParser;
import dev.langchain4j.data.document.splitter.DocumentSplitters;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import io.qdrant.client.QdrantClient;
import io.qdrant.client.grpc.Collections.CollectionInfo;
import io.qdrant.client.grpc.Collections.Distance;
import io.qdrant.client.grpc.Collections.VectorParams;
import io.qdrant.client.grpc.Collections.VectorsConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Service;

import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.ExecutionException;

@Service
@Order(1)
public class DocumentIngestService implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(DocumentIngestService.class);

    private final AppProperties props;
    private final QdrantClient qdrantClient;
    private final EmbeddingModel embeddingModel;
    private final EmbeddingStore<TextSegment> docsStore;

    /** Actual dimension reported by the live embedding model; resolved once at startup. */
    private volatile int verifiedDimensions = -1;

    public DocumentIngestService(
            AppProperties props,
            QdrantClient qdrantClient,
            EmbeddingModel embeddingModel,
            @Qualifier("docsEmbeddingStore") EmbeddingStore<TextSegment> docsStore
    ) {
        this.props = props;
        this.qdrantClient = qdrantClient;
        this.embeddingModel = embeddingModel;
        this.docsStore = docsStore;
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
        int dims = verifyEmbeddingDimensions();
        ensureCompatibleCollection(props.qdrant().docsCollection(), dims);
        ensureCompatibleCollection(props.qdrant().memoryCollection(), dims);
        if (props.rag().autoIngest()) {
            ingestCorpus();
        }
    }

    /**
     * Probes the live embedding model instead of trusting the configured dimension blindly.
     * Fails fast if the configured value does not match what the model actually returns
     * (e.g. after switching embedding models without updating config).
     */
    public int verifyEmbeddingDimensions() {
        if (verifiedDimensions > 0) {
            return verifiedDimensions;
        }
        int actual = embeddingModel.embed("dimension probe").content().dimension();
        int configured = props.ollama().embeddingDimensions();
        if (actual != configured) {
            throw new IllegalStateException(
                    "Embedding model '" + props.ollama().embeddingModel() + "' returns " + actual
                            + "-dim vectors but OLLAMA_EMBEDDING_DIMENSIONS is " + configured
                            + ". Update the config (and re-ingest) so Qdrant collections match the model."
            );
        }
        log.info("Verified embedding model '{}' outputs {}-dim vectors", props.ollama().embeddingModel(), actual);
        verifiedDimensions = actual;
        return actual;
    }

    public IngestResult ingestCorpus() throws Exception {
        int dims = verifyEmbeddingDimensions();
        Path corpus = resolveCorpusPath();
        // Always recreate both collections so vector size matches the active embedding model
        recreateCollection(props.qdrant().docsCollection(), dims);
        recreateCollection(props.qdrant().memoryCollection(), dims);

        Document document;
        try (InputStream in = Files.newInputStream(corpus)) {
            document = new ApachePdfBoxDocumentParser().parse(in);
        }

        Metadata base = document.metadata() == null ? new Metadata() : document.metadata().copy();
        base.put("source", corpus.getFileName().toString());
        base.put("corpus", "middle-east-war-updates-2026");
        base.put("date_range", "2026-02-28_to_2026-07-13");
        document = Document.from(document.text(), base);

        EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
                .documentSplitter(DocumentSplitters.recursive(
                        props.rag().chunkSize(),
                        props.rag().chunkOverlap()
                ))
                .textSegmentTransformer(segment -> {
                    Metadata md = segment.metadata() == null ? new Metadata() : segment.metadata().copy();
                    md.put("section_hint", inferSectionHint(segment.text()));
                    return TextSegment.from(segment.text(), md);
                })
                .embeddingModel(embeddingModel)
                .embeddingStore(docsStore)
                .build();

        ingestor.ingest(document);
        int chunks = estimateChunks(document);
        log.info("Ingested {} chunks from {} into {}-dim collections", chunks, corpus.toAbsolutePath(), dims);
        return new IngestResult(corpus.toAbsolutePath().toString(), chunks);
    }

    private Path resolveCorpusPath() throws Exception {
        Path configured = Path.of(props.rag().corpusPath());
        if (Files.exists(configured)) {
            return configured.toAbsolutePath().normalize();
        }
        log.info("Corpus PDF missing at {}; generating it", configured.toAbsolutePath());
        Files.createDirectories(configured.getParent());
        CorpusPdfGenerator.generate(configured);
        return configured.toAbsolutePath().normalize();
    }

    private int estimateChunks(Document document) {
        return DocumentSplitters.recursive(props.rag().chunkSize(), props.rag().chunkOverlap())
                .split(document)
                .size();
    }

    static String inferSectionHint(String text) {
        String lower = text.toLowerCase();
        if (lower.contains("february") || lower.contains("28 february") || lower.contains("march 2026")) {
            return "feb-mar-2026-opening";
        }
        if (lower.contains("april 2026") || lower.contains("7 april") || lower.contains("blockade")) {
            return "apr-2026-ceasefire-hormuz";
        }
        if (lower.contains("may 2026") || lower.contains("31 may") || lower.contains("convoy")) {
            return "may-2026-lebanon-deep-push";
        }
        if (lower.contains("june 2026") || lower.contains("17 june") || lower.contains("mou")) {
            return "jun-2026-mou-framework";
        }
        if (lower.contains("july 2026") || lower.contains("7 july") || lower.contains("13 july")
                || lower.contains("ceasefire is over") || lower.contains("doha")) {
            return "jul-2026-escalation";
        }
        return "general";
    }

    public void ensureCompatibleCollection(String name, int dims) throws ExecutionException, InterruptedException {
        Boolean exists = qdrantClient.collectionExistsAsync(name).get();
        if (Boolean.FALSE.equals(exists)) {
            createCollection(name, dims);
            log.info("Created Qdrant collection '{}' ({} dims)", name, dims);
            return;
        }

        long existingDims = readCollectionDimensions(name);
        if (existingDims != dims) {
            log.warn("Qdrant collection '{}' has {} dims but model outputs {}; recreating", name, existingDims, dims);
            recreateCollection(name, dims);
        }
    }

    private long readCollectionDimensions(String name) throws ExecutionException, InterruptedException {
        CollectionInfo info = qdrantClient.getCollectionInfoAsync(name).get();
        VectorsConfig vectorsConfig = info.getConfig().getParams().getVectorsConfig();
        if (vectorsConfig.hasParams()) {
            return vectorsConfig.getParams().getSize();
        }
        if (vectorsConfig.hasParamsMap() && !vectorsConfig.getParamsMap().getMapMap().isEmpty()) {
            return vectorsConfig.getParamsMap().getMapMap().values().iterator().next().getSize();
        }
        return -1;
    }

    private void recreateCollection(String name, int dims) throws ExecutionException, InterruptedException {
        Boolean exists = qdrantClient.collectionExistsAsync(name).get();
        if (Boolean.TRUE.equals(exists)) {
            qdrantClient.deleteCollectionAsync(name).get();
            log.info("Deleted Qdrant collection '{}' for recreate", name);
        }
        createCollection(name, dims);
        log.info("Recreated Qdrant collection '{}' ({} dims)", name, dims);
    }

    private void createCollection(String name, int dims) throws ExecutionException, InterruptedException {
        qdrantClient.createCollectionAsync(
                name,
                VectorParams.newBuilder()
                        .setSize(dims)
                        .setDistance(Distance.Cosine)
                        .build()
        ).get();
    }

    public record IngestResult(String corpusPath, int chunkCount) {}
}
