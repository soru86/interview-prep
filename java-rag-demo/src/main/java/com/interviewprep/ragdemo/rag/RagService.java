package com.interviewprep.ragdemo.rag;

import com.interviewprep.ragdemo.config.AppProperties;
import com.interviewprep.ragdemo.memory.ConversationMemoryService;
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingMatch;
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingStore;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class RagService {

    private static final String SYSTEM_PROMPT = """
            You are a careful research assistant answering questions about Middle East war updates \
            from 28 February 2026 through 12 July 2026.

            Rules:
            1. Ground every factual claim in the RETRIEVED CONTEXT and/or LONG-TERM MEMORY below.
            2. Cite specific dates and section cues when available (e.g., "On 17 June 2026...").
            3. If the context is insufficient or below relevance, say you do not know based on the corpus.
            4. Do not invent casualties, treaty clauses, or events not present in the context.
            5. Keep answers clear and concise unless the user asks for detail.
            """;

    private final AppProperties props;
    private final EmbeddingModel embeddingModel;
    private final EmbeddingStore<TextSegment> docsStore;
    private final ConversationMemoryService memoryService;

    public RagService(
            AppProperties props,
            EmbeddingModel embeddingModel,
            @Qualifier("docsEmbeddingStore") EmbeddingStore<TextSegment> docsStore,
            ConversationMemoryService memoryService
    ) {
        this.props = props;
        this.embeddingModel = embeddingModel;
        this.docsStore = docsStore;
        this.memoryService = memoryService;
    }

    public RagContext buildContext(String sessionId, String question) {
        Embedding queryEmbedding = embeddingModel.embed(question).content();
        EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
                .queryEmbedding(queryEmbedding)
                .maxResults(props.rag().topK())
                .minScore(props.rag().minScore())
                .build();

        List<EmbeddingMatch<TextSegment>> matches = docsStore.search(request).matches();
        List<RetrievedChunk> chunks = matches.stream()
                .map(m -> new RetrievedChunk(
                        m.embedded().text(),
                        m.score(),
                        m.embedded().metadata() == null ? "" : String.valueOf(m.embedded().metadata().toMap())
                ))
                .collect(Collectors.toList());

        List<String> longTerm = memoryService.retrieveLongTerm(sessionId, question);
        List<ChatMessage> messages = assembleMessages(question, chunks, longTerm, sessionId);
        return new RagContext(messages, chunks, longTerm);
    }

    private List<ChatMessage> assembleMessages(
            String question,
            List<RetrievedChunk> chunks,
            List<String> longTerm,
            String sessionId
    ) {
        StringBuilder contextBlock = new StringBuilder();
        contextBlock.append("RETRIEVED CONTEXT:\n");
        if (chunks.isEmpty()) {
            contextBlock.append("(no chunks above min-score)\n");
        } else {
            for (int i = 0; i < chunks.size(); i++) {
                RetrievedChunk c = chunks.get(i);
                contextBlock.append("--- chunk ").append(i + 1)
                        .append(" (score=").append(String.format("%.3f", c.score())).append(") ---\n")
                        .append(c.text()).append("\n");
            }
        }

        contextBlock.append("\nLONG-TERM MEMORY:\n");
        if (longTerm.isEmpty()) {
            contextBlock.append("(none)\n");
        } else {
            for (int i = 0; i < longTerm.size(); i++) {
                contextBlock.append("- ").append(longTerm.get(i)).append("\n");
            }
        }

        List<ChatMessage> messages = new ArrayList<>();
        messages.add(SystemMessage.from(SYSTEM_PROMPT + "\n\n" + contextBlock));
        for (ChatMessage prior : memoryService.shortTermMessages(sessionId)) {
            if (prior instanceof UserMessage || prior instanceof AiMessage) {
                messages.add(prior);
            }
        }
        messages.add(UserMessage.from(question));
        return messages;
    }

    public record RetrievedChunk(String text, double score, String metadata) {}

    public record RagContext(
            List<ChatMessage> messages,
            List<RetrievedChunk> chunks,
            List<String> longTermMemories
    ) {}
}
