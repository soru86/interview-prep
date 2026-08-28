package com.interviewprep.ragdemov2.config;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.ollama.OllamaEmbeddingModel;
import dev.langchain4j.model.ollama.OllamaStreamingChatModel;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.qdrant.QdrantEmbeddingStore;
import io.qdrant.client.QdrantClient;
import io.qdrant.client.QdrantGrpcClient;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;

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
        return OllamaEmbeddingModel.builder()
                .baseUrl(props.ollama().baseUrl())
                .modelName(props.ollama().embeddingModel())
                .timeout(Duration.ofSeconds(props.ollama().timeoutSeconds()))
                .build();
    }

    @Bean
    StreamingChatModel streamingChatModel(AppProperties props) {
        return OllamaStreamingChatModel.builder()
                .baseUrl(props.ollama().baseUrl())
                .modelName(props.ollama().chatModel())
                .temperature(props.ollama().temperature())
                .timeout(Duration.ofSeconds(props.ollama().timeoutSeconds()))
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
}
