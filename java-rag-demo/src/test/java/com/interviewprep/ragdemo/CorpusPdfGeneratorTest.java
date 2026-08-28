package com.interviewprep.ragdemo;

import com.interviewprep.ragdemo.pdf.CorpusPdfGenerator;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertTrue;

class CorpusPdfGeneratorTest {

    @TempDir
    Path tempDir;

    @Test
    void generatesNonEmptyPdf() throws Exception {
        Path out = tempDir.resolve("corpus.pdf");
        CorpusPdfGenerator.generate(out);
        assertTrue(Files.exists(out));
        assertTrue(Files.size(out) > 1000);
        assertTrue(Files.readAllBytes(out).length > 4);
        byte[] header = Files.readAllBytes(out);
        assertTrue(header[0] == '%' && header[1] == 'P' && header[2] == 'D' && header[3] == 'F');
    }
}
