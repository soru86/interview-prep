package com.interviewprep.ragdemo.config;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.googleai.GoogleAiEmbeddingModel;
import dev.langchain4j.model.googleai.GoogleAiGeminiStreamingChatModel;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.qdrant.QdrantEmbeddingStore;
import io.qdrant.client.QdrantClient;
import io.qdrant.client.QdrantGrpcClient;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.util.StringUtils;

@Configuration
public class AiConfig {

    @Bean
    QdrantClient qdrantClient(AppProperties props) {
        return new QdrantClient(
                QdrantGrpcClient.newBuilder(props.qdrant().host(), props.qdrant().grpcPort(), false)
                        .build()
        );
    }

    @Bean
    EmbeddingModel embeddingModel(AppProperties props) {
        requireApiKey(props);
        return GoogleAiEmbeddingModel.builder()
                .apiKey(props.google().apiKey())
                .modelName(props.google().embeddingModel())
                .taskType(GoogleAiEmbeddingModel.TaskType.RETRIEVAL_DOCUMENT)
                .outputDimensionality(props.google().embeddingDimensions())
                .build();
    }

    @Bean
    StreamingChatModel streamingChatModel(AppProperties props) {
        requireApiKey(props);
        return GoogleAiGeminiStreamingChatModel.builder()
                .apiKey(props.google().apiKey())
                .modelName(props.google().chatModel())
                .temperature(0.2)
                .build();
    }

    @Bean
    @Qualifier("docsEmbeddingStore")
    EmbeddingStore<TextSegment> docsEmbeddingStore(QdrantClient client, AppProperties props) {
        return QdrantEmbeddingStore.builder()
                .client(client)
                .collectionName(props.qdrant().docsCollection())
                .build();
    }

    @Bean
    @Qualifier("memoryEmbeddingStore")
    EmbeddingStore<TextSegment> memoryEmbeddingStore(QdrantClient client, AppProperties props) {
        return QdrantEmbeddingStore.builder()
                .client(client)
                .collectionName(props.qdrant().memoryCollection())
                .build();
    }

    private static void requireApiKey(AppProperties props) {
        if (!StringUtils.hasText(props.google().apiKey())) {
            throw new IllegalStateException(
                    "GOOGLE_AI_API_KEY is not set. Copy .env.example to .env or export GOOGLE_AI_API_KEY."
            );
        }
    }
}
