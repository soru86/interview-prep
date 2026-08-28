package com.interviewprep.ragdemo.chat;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.interviewprep.ragdemo.memory.ConversationMemoryService;
import com.interviewprep.ragdemo.rag.RagService;
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.chat.response.StreamingChatResponseHandler;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;

@Service
public class ChatStreamingService {

    private static final Logger log = LoggerFactory.getLogger(ChatStreamingService.class);

    private final StreamingChatModel streamingModel;
    private final RagService ragService;
    private final ConversationMemoryService memoryService;
    private final ObjectMapper objectMapper;

    public ChatStreamingService(
            StreamingChatModel streamingModel,
            RagService ragService,
            ConversationMemoryService memoryService,
            ObjectMapper objectMapper
    ) {
        this.streamingModel = streamingModel;
        this.ragService = ragService;
        this.memoryService = memoryService;
        this.objectMapper = objectMapper;
    }

    public SseEmitter streamChat(String sessionId, String message) {
        String sid = (sessionId == null || sessionId.isBlank())
                ? UUID.randomUUID().toString()
                : sessionId.trim();

        SseEmitter emitter = new SseEmitter(180_000L);
        AtomicReference<StringBuilder> full = new AtomicReference<>(new StringBuilder());

        try {
            sendEvent(emitter, "session", Map.of("sessionId", sid));
            RagService.RagContext context = ragService.buildContext(sid, message);
            sendEvent(emitter, "sources", Map.of(
                    "chunks", context.chunks().stream()
                            .map(c -> Map.of(
                                    "score", c.score(),
                                    "preview", truncate(c.text(), 220),
                                    "metadata", c.metadata()
                            ))
                            .toList(),
                    "longTermMemories", context.longTermMemories()
            ));

            List<ChatMessage> messages = context.messages();
            streamingModel.chat(messages, new StreamingChatResponseHandler() {
                @Override
                public void onPartialResponse(String token) {
                    full.get().append(token);
                    try {
                        sendEvent(emitter, "token", Map.of("content", token));
                    } catch (IOException e) {
                        emitter.completeWithError(e);
                    }
                }

                @Override
                public void onCompleteResponse(ChatResponse response) {
                    try {
                        String answer = full.get().toString();
                        if (answer.isBlank() && response != null && response.aiMessage() != null) {
                            answer = response.aiMessage().text();
                        }
                        memoryService.appendTurn(sid, message, answer);
                        sendEvent(emitter, "done", Map.of(
                                "sessionId", sid,
                                "length", answer.length()
                        ));
                        emitter.complete();
                    } catch (Exception e) {
                        log.error("Failed to finalize chat stream", e);
                        emitter.completeWithError(e);
                    }
                }

                @Override
                public void onError(Throwable error) {
                    log.error("Streaming chat failed", error);
                    try {
                        sendEvent(emitter, "error", Map.of(
                                "message", error.getMessage() == null ? "stream error" : error.getMessage()
                        ));
                    } catch (IOException ignored) {
                        // ignore secondary send failures
                    }
                    emitter.completeWithError(error);
                }
            });
        } catch (Exception e) {
            log.error("Chat setup failed", e);
            emitter.completeWithError(e);
        }

        return emitter;
    }

    private void sendEvent(SseEmitter emitter, String name, Object payload) throws IOException {
        String json = objectMapper.writeValueAsString(payload);
        emitter.send(SseEmitter.event().name(name).data(json, MediaType.APPLICATION_JSON));
    }

    private static String truncate(String text, int max) {
        if (text == null) {
            return "";
        }
        String cleaned = text.replaceAll("\\s+", " ").trim();
        return cleaned.length() <= max ? cleaned : cleaned.substring(0, max) + "...";
    }
}
