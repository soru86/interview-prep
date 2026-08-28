package com.interviewprep.ragdemov2.chat;

/**
 * Splits a DeepSeek R1 token stream into "thinking" text (inside {@code <think>...</think>})
 * and answer text (everything else). Tags may arrive split across multiple stream tokens,
 * so a partial-tag suffix is held back until enough characters arrive to disambiguate.
 * Not thread-safe; use one instance per stream.
 */
public final class ThinkTagStreamSplitter {

    private static final String OPEN = "<think>";
    private static final String CLOSE = "</think>";

    private final StringBuilder pending = new StringBuilder();
    private boolean insideThink;

    public record Part(String thinking, String answer) {
        public boolean isEmpty() {
            return thinking.isEmpty() && answer.isEmpty();
        }
    }

    public Part process(String token) {
        pending.append(token);
        StringBuilder thinking = new StringBuilder();
        StringBuilder answer = new StringBuilder();

        while (true) {
            String tag = insideThink ? CLOSE : OPEN;
            int idx = pending.indexOf(tag);
            if (idx >= 0) {
                String before = pending.substring(0, idx);
                (insideThink ? thinking : answer).append(before);
                pending.delete(0, idx + tag.length());
                insideThink = !insideThink;
                continue;
            }

            int holdBack = partialTagSuffixLength(pending, tag);
            String emit = pending.substring(0, pending.length() - holdBack);
            (insideThink ? thinking : answer).append(emit);
            pending.delete(0, pending.length() - holdBack);
            return new Part(thinking.toString(), answer.toString());
        }
    }

    /** Emits whatever is still held back (e.g. an unterminated partial tag) at end of stream. */
    public Part flush() {
        String rest = pending.toString();
        pending.setLength(0);
        return insideThink ? new Part(rest, "") : new Part("", rest);
    }

    private static int partialTagSuffixLength(CharSequence text, String tag) {
        int max = Math.min(text.length(), tag.length() - 1);
        for (int len = max; len > 0; len--) {
            boolean match = true;
            for (int i = 0; i < len; i++) {
                if (text.charAt(text.length() - len + i) != tag.charAt(i)) {
                    match = false;
                    break;
                }
            }
            if (match) {
                return len;
            }
        }
        return 0;
    }
}
