package com.interviewprep.ragdemov2.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "app")
public record AppProperties(
        Ollama ollama,
        Qdrant qdrant,
        Rag rag,
        Memory memory
) {
    public record Ollama(
            String baseUrl,
            String chatModel,
            String embeddingModel,
            int embeddingDimensions,
            int timeoutSeconds,
            double temperature
    ) {}

    public record Qdrant(
            String host,
            int grpcPort,
            int httpPort,
            String docsCollection,
            String memoryCollection
    ) {}

    public record Rag(
            int topK,
            double minScore,
            int chunkSize,
            int chunkOverlap,
            boolean autoIngest,
            String corpusPath
    ) {}

    public record Memory(
            int shortTermMaxMessages,
            int longTermTopK,
            double longTermMinScore
    ) {}
}
