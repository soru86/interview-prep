package com.interviewprep.ragdemo.ingest;

import com.interviewprep.ragdemo.config.AppProperties;
import com.interviewprep.ragdemo.pdf.CorpusPdfGenerator;
import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.Metadata;
import dev.langchain4j.data.document.parser.apache.pdfbox.ApachePdfBoxDocumentParser;
import dev.langchain4j.data.document.splitter.DocumentSplitters;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.store.embedding.IngestionResult;
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
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.concurrent.ExecutionException;

@Service
@Order(1)
public class DocumentIngestService implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(DocumentIngestService.class);

    private final AppProperties props;
    private final QdrantClient qdrantClient;
    private final EmbeddingModel embeddingModel;
    private final EmbeddingStore<TextSegment> docsStore;

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
        ensureCompatibleCollection(props.qdrant().docsCollection());
        ensureCompatibleCollection(props.qdrant().memoryCollection());
        if (props.rag().autoIngest()) {
            ingestCorpus();
        }
    }

    public IngestResult ingestCorpus() throws Exception {
        Path corpus = resolveCorpusPath();
        // Always recreate both collections so vector size matches the active embedding model
        recreateCollection(props.qdrant().docsCollection());
        recreateCollection(props.qdrant().memoryCollection());

        Document document;
        try (InputStream in = Files.newInputStream(corpus)) {
            document = new ApachePdfBoxDocumentParser().parse(in);
        }

        Metadata base = document.metadata() == null ? new Metadata() : document.metadata().copy();
        base.put("source", corpus.getFileName().toString());
        base.put("corpus", "middle-east-war-updates-2026");
        base.put("date_range", "2026-02-28_to_2026-07-12");
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

        IngestionResult ignored = ingestor.ingest(document);
        int chunks = estimateChunks(document);
        log.info(
                "Ingested {} chunks from {} into {}-dim collections (ingestion ok={})",
                chunks,
                corpus.toAbsolutePath(),
                props.google().embeddingDimensions(),
                ignored != null
        );
        return new IngestResult(corpus.toAbsolutePath().toString(), chunks);
    }

    private Path resolveCorpusPath() throws Exception {
        Path configured = Path.of(props.rag().corpusPath());
        if (Files.exists(configured)) {
            return configured.toAbsolutePath().normalize();
        }

        ClassPathResource classpathPdf = new ClassPathResource("corpus/middle-east-war-updates-2026.pdf");
        if (classpathPdf.exists()) {
            Path target = configured;
            Files.createDirectories(target.getParent());
            try (InputStream in = classpathPdf.getInputStream()) {
                Files.copy(in, target, StandardCopyOption.REPLACE_EXISTING);
            }
            log.info("Copied classpath corpus to {}", target.toAbsolutePath());
            return target.toAbsolutePath().normalize();
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
        if (lower.contains("may 2026") || lower.contains("31 may")) {
            return "may-2026-lebanon-deep-push";
        }
        if (lower.contains("june 2026") || lower.contains("17 june") || lower.contains("mou")) {
            return "jun-2026-mou-framework";
        }
        if (lower.contains("july 2026") || lower.contains("7 july") || lower.contains("ceasefire is over")) {
            return "jul-2026-escalation";
        }
        return "general";
    }

    /**
     * Creates the collection if missing, or recreates it when vector size does not match
     * the configured embedding dimensions (e.g. after switching OpenAI 1536 → Gemini 768).
     */
    public void ensureCompatibleCollection(String name) throws ExecutionException, InterruptedException {
        Boolean exists = qdrantClient.collectionExistsAsync(name).get();
        if (Boolean.FALSE.equals(exists)) {
            createCollection(name);
            log.info("Created Qdrant collection '{}' ({} dims)", name, props.google().embeddingDimensions());
            return;
        }

        long existingDims = readCollectionDimensions(name);
        int expected = props.google().embeddingDimensions();
        if (existingDims != expected) {
            log.warn(
                    "Qdrant collection '{}' has {} dims but app expects {}; recreating",
                    name,
                    existingDims,
                    expected
            );
            recreateCollection(name);
        }
    }

    private long readCollectionDimensions(String name) throws ExecutionException, InterruptedException {
        CollectionInfo info = qdrantClient.getCollectionInfoAsync(name).get();
        VectorsConfig vectorsConfig = info.getConfig().getParams().getVectorsConfig();
        if (vectorsConfig.hasParams()) {
            return vectorsConfig.getParams().getSize();
        }
        // Named vectors: take the first entry if present
        if (vectorsConfig.hasParamsMap() && !vectorsConfig.getParamsMap().getMapMap().isEmpty()) {
            return vectorsConfig.getParamsMap().getMapMap().values().iterator().next().getSize();
        }
        return -1;
    }

    private void recreateCollection(String name) throws ExecutionException, InterruptedException {
        Boolean exists = qdrantClient.collectionExistsAsync(name).get();
        if (Boolean.TRUE.equals(exists)) {
            qdrantClient.deleteCollectionAsync(name).get();
            log.info("Deleted Qdrant collection '{}' for recreate", name);
        }
        createCollection(name);
        log.info("Recreated Qdrant collection '{}' ({} dims)", name, props.google().embeddingDimensions());
    }

    private void createCollection(String name) throws ExecutionException, InterruptedException {
        qdrantClient.createCollectionAsync(
                name,
                VectorParams.newBuilder()
                        .setSize(props.google().embeddingDimensions())
                        .setDistance(Distance.Cosine)
                        .build()
        ).get();
    }

    public record IngestResult(String corpusPath, int chunkCount) {}
}
