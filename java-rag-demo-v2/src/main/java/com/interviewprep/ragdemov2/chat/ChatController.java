package com.interviewprep.ragdemov2.chat;

import com.interviewprep.ragdemov2.ingest.DocumentIngestService;
import jakarta.validation.constraints.NotBlank;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.Map;

@RestController
@RequestMapping("/api")
@Validated
@CrossOrigin
public class ChatController {

    private final ChatStreamingService chatStreamingService;
    private final DocumentIngestService documentIngestService;

    public ChatController(
            ChatStreamingService chatStreamingService,
            DocumentIngestService documentIngestService
    ) {
        this.chatStreamingService = chatStreamingService;
        this.documentIngestService = documentIngestService;
    }

    @PostMapping(value = "/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter chat(
            @RequestHeader(value = "X-Session-Id", required = false) String sessionId,
            @RequestBody @Validated ChatRequest request
    ) {
        return chatStreamingService.streamChat(sessionId, request.message());
    }

    @PostMapping("/ingest")
    public ResponseEntity<Map<String, Object>> ingest() throws Exception {
        DocumentIngestService.IngestResult result = documentIngestService.ingestCorpus();
        return ResponseEntity.ok(Map.of(
                "status", "ok",
                "corpusPath", result.corpusPath(),
                "chunkCount", result.chunkCount()
        ));
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "UP");
    }

    public record ChatRequest(@NotBlank String message) {}
}
