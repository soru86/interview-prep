package com.interviewprep.ragdemov2.chat;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ThinkTagStreamSplitterTest {

    @Test
    void separatesThinkingFromAnswerInSingleToken() {
        ThinkTagStreamSplitter splitter = new ThinkTagStreamSplitter();
        ThinkTagStreamSplitter.Part part = splitter.process("<think>reasoning here</think>The answer.");
        assertEquals("reasoning here", part.thinking());
        assertEquals("The answer.", part.answer());
    }

    @Test
    void handlesTagsSplitAcrossTokens() {
        ThinkTagStreamSplitter splitter = new ThinkTagStreamSplitter();
        StringBuilder thinking = new StringBuilder();
        StringBuilder answer = new StringBuilder();

        for (String token : List.of("<th", "ink>rea", "soning</t", "hink>ans", "wer")) {
            ThinkTagStreamSplitter.Part part = splitter.process(token);
            thinking.append(part.thinking());
            answer.append(part.answer());
        }
        ThinkTagStreamSplitter.Part rest = splitter.flush();
        thinking.append(rest.thinking());
        answer.append(rest.answer());

        assertEquals("reasoning", thinking.toString());
        assertEquals("answer", answer.toString());
    }

    @Test
    void passesThroughPlainTextWithoutTags() {
        ThinkTagStreamSplitter splitter = new ThinkTagStreamSplitter();
        ThinkTagStreamSplitter.Part part = splitter.process("plain answer text");
        ThinkTagStreamSplitter.Part rest = splitter.flush();
        assertEquals("", part.thinking() + rest.thinking());
        assertEquals("plain answer text", part.answer() + rest.answer());
    }

    @Test
    void flushEmitsUnterminatedThinking() {
        ThinkTagStreamSplitter splitter = new ThinkTagStreamSplitter();
        ThinkTagStreamSplitter.Part part = splitter.process("<think>never closed");
        ThinkTagStreamSplitter.Part rest = splitter.flush();
        assertEquals("never closed", part.thinking() + rest.thinking());
        assertEquals("", part.answer() + rest.answer());
    }

    @Test
    void holdsBackPartialTagButEmitsWhenNotATag() {
        ThinkTagStreamSplitter splitter = new ThinkTagStreamSplitter();
        StringBuilder answer = new StringBuilder();
        answer.append(splitter.process("a < b").answer());
        answer.append(splitter.process(" and c").answer());
        answer.append(splitter.flush().answer());
        assertEquals("a < b and c", answer.toString());
    }

    @Test
    void stripThinkTagsRemovesReasoningBlocks() {
        assertEquals("Answer.", ChatStreamingService.stripThinkTags("<think>blah\nblah</think>Answer."));
        assertEquals("Answer.", ChatStreamingService.stripThinkTags("Answer."));
        assertEquals("", ChatStreamingService.stripThinkTags(null));
    }
}
