package com.interviewprep.ragdemov2.ingest;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class DocumentIngestServiceTest {

    @Test
    void infersSectionHintsFromChunkText() {
        assertEquals("feb-mar-2026-opening", DocumentIngestService.inferSectionHint("On 28 February Iran was struck"));
        assertEquals("jun-2026-mou-framework", DocumentIngestService.inferSectionHint("The 17 June MoU diluted uranium"));
        assertEquals("jul-2026-escalation", DocumentIngestService.inferSectionHint("On 7 July ships were struck"));
        assertEquals("jul-2026-escalation", DocumentIngestService.inferSectionHint("On 13 July talks moved to Doha"));
        assertEquals("general", DocumentIngestService.inferSectionHint("Unrelated text without dates"));
    }
}
