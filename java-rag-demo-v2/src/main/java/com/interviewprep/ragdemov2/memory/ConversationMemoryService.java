package com.interviewprep.ragdemov2.memory;

import com.interviewprep.ragdemov2.config.AppProperties;
import dev.langchain4j.data.document.Metadata;
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.memory.ChatMemory;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingMatch;
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingStore;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * Dual memory:
 * - Short-term: per-session in-memory message window (recent turns verbatim).
 * - Long-term: turn summaries embedded into a dedicated Qdrant collection,
 *   retrieved semantically and filtered by sessionId.
 */
@Service
public class ConversationMemoryService {

    private final AppProperties props;
    private final EmbeddingModel embeddingModel;
    private final EmbeddingStore<TextSegment> memoryStore;
    private final Map<String, ChatMemory> shortTermBySession = new ConcurrentHashMap<>();

    public ConversationMemoryService(
            AppProperties props,
            EmbeddingModel embeddingModel,
            @Qualifier("memoryEmbeddingStore") EmbeddingStore<TextSegment> memoryStore
    ) {
        this.props = props;
        this.embeddingModel = embeddingModel;
        this.memoryStore = memoryStore;
    }

    public ChatMemory shortTerm(String sessionId) {
        return shortTermBySession.computeIfAbsent(
                sessionId,
                id -> MessageWindowChatMemory.withMaxMessages(props.memory().shortTermMaxMessages())
        );
    }

    public List<ChatMessage> shortTermMessages(String sessionId) {
        return shortTerm(sessionId).messages();
    }

    public void appendTurn(String sessionId, String userText, String assistantText) {
        ChatMemory memory = shortTerm(sessionId);
        memory.add(UserMessage.from(userText));
        memory.add(AiMessage.from(assistantText));
        storeLongTerm(sessionId, userText, assistantText);
    }

    public void storeLongTerm(String sessionId, String userText, String assistantText) {
        String summary = "User asked: " + truncate(userText, 400)
                + " | Assistant answered: " + truncate(assistantText, 600);
        Metadata metadata = new Metadata();
        metadata.put("sessionId", sessionId);
        metadata.put("timestamp", Instant.now().toString());
        metadata.put("type", "long_term_memory");
        metadata.put("memoryId", UUID.randomUUID().toString());

        TextSegment segment = TextSegment.from(summary, metadata);
        Embedding embedding = embeddingModel.embed(segment).content();
        memoryStore.add(embedding, segment);
    }

    public List<String> retrieveLongTerm(String sessionId, String query) {
        Embedding queryEmbedding = embeddingModel.embed(query).content();
        EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
                .queryEmbedding(queryEmbedding)
                .maxResults(props.memory().longTermTopK())
                .minScore(props.memory().longTermMinScore())
                .build();

        List<EmbeddingMatch<TextSegment>> matches = memoryStore.search(request).matches();
        return matches.stream()
                .filter(m -> sessionId.equals(m.embedded().metadata().getString("sessionId")))
                .map(m -> m.embedded().text())
                .collect(Collectors.toList());
    }

    private static String truncate(String text, int max) {
        if (text == null) {
            return "";
        }
        String cleaned = text.replaceAll("\\s+", " ").trim();
        return cleaned.length() <= max ? cleaned : cleaned.substring(0, max) + "...";
    }
}
