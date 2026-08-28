package com.interviewprep.ragdemo.pdf;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.common.PDRectangle;
import org.apache.pdfbox.pdmodel.font.PDType1Font;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/**
 * Generates the Middle East war-updates corpus PDF used for RAG ingestion.
 * Uses PDFBox 2.x to stay compatible with langchain4j-document-parser-apache-pdfbox.
 * Run: mvn -q exec:java -Dexec.mainClass=com.interviewprep.ragdemo.pdf.CorpusPdfGenerator
 */
public final class CorpusPdfGenerator {

    private static final float MARGIN = 50f;
    private static final float LEADING = 14f;
    private static final float FONT_SIZE = 11f;
    private static final float TITLE_SIZE = 18f;
    private static final float HEADING_SIZE = 13f;

    private CorpusPdfGenerator() {}

    public static void main(String[] args) throws IOException {
        Path out = Path.of(args.length > 0 ? args[0] : "data/corpus/middle-east-war-updates-2026.pdf");
        Files.createDirectories(out.getParent());
        generate(out);
        System.out.println("Wrote corpus PDF to " + out.toAbsolutePath());
    }

    public static void generate(Path output) throws IOException {
        try (PDDocument doc = new PDDocument()) {
            PDType1Font regular = PDType1Font.HELVETICA;
            PDType1Font bold = PDType1Font.HELVETICA_BOLD;

            List<Section> sections = buildSections();
            for (Section section : sections) {
                writeSection(doc, section, regular, bold);
            }
            doc.save(output.toFile());
        }
    }

    private static List<Section> buildSections() {
        List<Section> sections = new ArrayList<>();

        sections.add(new Section(
                "Middle East War Updates: 28 February 2026 – 12 July 2026",
                List.of(
                        "Educational laboratory corpus for a Retrieval-Augmented Generation (RAG) demo.",
                        "This document summarizes publicly reported war, diplomacy, and maritime developments "
                                + "across the Middle East from 28 February 2026 through 12 July 2026.",
                        "Primary theaters covered: Iran–United States–Israel conflict; Lebanon–Hezbollah front; "
                                + "Strait of Hormuz shipping disruption; and related Gulf-state impacts.",
                        "Disclaimer: Compiled for software demonstration and interview-prep purposes. "
                                + "It is not an official government briefing. Dates and events are drawn from "
                                + "open-source reporting (including AP timeline summaries and contemporaneous coverage). "
                                + "Where reporting conflicts, both claims are noted.",
                        "How to use this corpus: Ask the RAG chat about specific dates, ceasefire deals, "
                                + "Hormuz status, Lebanon framework talks, or nuclear/sanctions terms."
                )
        ));

        sections.add(new Section(
                "1. Overview of the Conflict Arc",
                List.of(
                        "On 28 February 2026, joint United States and Israeli strikes on Iran killed Supreme Leader "
                                + "Ayatollah Ali Khamenei and other senior officials, precipitating a multi-front war. "
                                + "Iran retaliated against Israel and Gulf targets and asserted control over the "
                                + "Strait of Hormuz, a chokepoint that previously carried roughly one-fifth of globally "
                                + "traded oil and natural gas.",
                        "Within days, Hezbollah in Lebanon entered the war with rocket fire into northern Israel. "
                                + "Israel responded with air and ground operations that evolved into a sustained "
                                + "occupation of large areas of southern Lebanon.",
                        "From early April through mid-June, diplomacy produced fragile ceasefires, failed or partial "
                                + "Hormuz reopenings, a U.S. naval blockade of Iranian ports, and intermittent "
                                + "Israel–Lebanon talks in Washington.",
                        "On 17 June 2026, the U.S. and Iran signed an interim memorandum of understanding (MoU) "
                                + "establishing a roughly 60-day negotiation window covering uranium stockpile dilution, "
                                + "sanctions relief, and shipping. Parallel Israel–Lebanon framework talks advanced "
                                + "later in June. Renewed Hormuz incidents and U.S.–Iran strikes in early July "
                                + "threatened to unravel the interim deal as of 12 July 2026."
                )
        ));

        sections.add(new Section(
                "2. February–March 2026: Opening Strikes and Regional Expansion",
                List.of(
                        "28 February 2026 — Opening day. CENTCOM and partner forces began airstrikes against Iran. "
                                + "U.S. warships launched Tomahawk missiles; B-2, B-1, and B-52 aircraft struck "
                                + "fortified ballistic-missile facilities. Israeli and U.S. attacks killed Khamenei "
                                + "and other top officials. Iran launched ballistic missiles toward Israel and several "
                                + "Gulf states; a missile strike was reported against the U.S. Navy Fifth Fleet "
                                + "headquarters area in Bahrain. Iranian forces asserted control over the Strait of Hormuz.",
                        "2 March 2026 — Hezbollah front opens. Projectiles launched from Lebanon toward Israel "
                                + "triggered sirens in Haifa and the Upper Galilee. Hezbollah claimed responsibility "
                                + "for attacking an IDF base in Haifa in response to Khamenei’s killing. Israel vowed "
                                + "to neutralize the threat and began retaliatory air operations across Lebanon, "
                                + "including Beirut’s southern suburbs (Dahieh) and the Beqaa Valley.",
                        "Early–mid March 2026 — Israeli ground operations in southern Lebanon expanded. The IDF "
                                + "reported strikes on dozens of targets and operations around towns including Haris, "
                                + "Nabatieh al-Fawqa, and Mayfadoun, with displacement of large civilian populations. "
                                + "Reports cited killings of Hezbollah intelligence and Palestinian Islamic Jihad "
                                + "figures in Lebanon.",
                        "8 March 2026 — Iran names Mojtaba Khamenei, a son of the late supreme leader, as the new "
                                + "supreme leader. He had not been seen publicly and was believed to be in hiding after "
                                + "reportedly being injured in the opening strikes.",
                        "Late March 2026 — Fighting continued on Iranian, Israeli, Lebanese, and maritime fronts. "
                                + "Oil markets remained volatile as Hormuz transit stayed tightly controlled or blocked "
                                + "for many commercial tankers. Gulf states hosting U.S. forces faced intermittent "
                                + "missile and drone alerts."
                )
        ));

        sections.add(new Section(
                "3. April 2026: First Ceasefire Window and Hormuz Diplomacy",
                List.of(
                        "7 April 2026 — A tenuous two-week ceasefire deal was reached between the United States and "
                                + "Iran. Israel was not included in those discussions, and Israeli operations related "
                                + "to Lebanon continued to be a political flashpoint.",
                        "12 April 2026 — U.S. and Iranian negotiators held historic face-to-face talks in Islamabad, "
                                + "Pakistan, for several hours without reaching a final agreement. Pakistan played an "
                                + "early mediation role alongside later Qatari facilitation.",
                        "13 April 2026 — U.S. President Donald Trump announced a blockade of Iranian ports intended "
                                + "to pressure Tehran to relinquish its grip on the Strait of Hormuz.",
                        "14 April 2026 — Lebanon and Israel held their first direct diplomatic talks in decades in "
                                + "Washington, D.C., under U.S. auspices, focused on de-escalation and security "
                                + "arrangements in southern Lebanon.",
                        "17 April 2026 — Iran stated that it had reopened the Strait of Hormuz to shipping. The "
                                + "reopening did not hold; subsequent days saw renewed restrictions and security "
                                + "incidents that again constrained commercial traffic.",
                        "21 April 2026 — Trump said the United States was indefinitely extending the ceasefire with "
                                + "Iran, even as local violations and proxy-front fighting continued to be reported.",
                        "Late April 2026 — Diplomatic tracks remained open but fragile. Energy markets tracked "
                                + "daily Hormuz transit counts; shipping insurers and operators demanded war-risk "
                                + "premiums and approved routing."
                )
        ));

        sections.add(new Section(
                "4. May 2026: Escort Attempts and Deepening Lebanon War",
                List.of(
                        "3 May 2026 — Trump announced a U.S. effort to guide commercial ships through the Strait of "
                                + "Hormuz. Like the mid-April reopening claim, the escort initiative did not produce "
                                + "a durable free-navigation regime.",
                        "Throughout May 2026 — Cross-border fire between Hezbollah and Israel continued. Israeli "
                                + "ground forces pushed deeper into southern Lebanon while airstrikes hit suspected "
                                + "Hezbollah infrastructure. Humanitarian reporting described large-scale displacement "
                                + "from southern Lebanon and severe disruption of civilian services.",
                        "31 May 2026 — Israel’s ground invasion of Lebanon reached its deepest incursion in more "
                                + "than a quarter-century, according to contemporaneous reporting, as Hezbollah "
                                + "continued rocket and missile fire into northern Israel.",
                        "Late May context — Parallel U.S.–Iran talks remained intermittent. Issues on the table "
                                + "included Hormuz freedom of navigation, Iran’s highly enriched uranium stockpile, "
                                + "sanctions relief, and the status of fighting involving Hezbollah in Lebanon."
                )
        ));

        sections.add(new Section(
                "5. June 2026: Interim MoU, Lebanon Framework, and Renewed Strikes",
                List.of(
                        "3 June 2026 — Israel and Lebanon said they agreed to renew a fragile ceasefire and create "
                                + "security zones intended to exclude Hezbollah. Fighting resumed quickly after the "
                                + "announcement, underscoring the gap between political frameworks and battlefield "
                                + "realities.",
                        "Around 3 June 2026 — Reporting also described intense U.S.–Iran exchanges; one account "
                                + "cited Iranian missiles and drones striking Kuwait International Airport, killing "
                                + "at least one person and wounding more than sixty others during a major escalation "
                                + "wave.",
                        "7 June 2026 — Iran fired at Israel in the first such bombardment since the early-April "
                                + "ceasefire took effect. Israel returned fire. The episode marked a clear breakdown "
                                + "of the April pause on the Iran–Israel kinetic channel.",
                        "14 June 2026 — Trump said an interim deal with Iran had been reached and would be signed "
                                + "within days. Iranian officials insisted any durable settlement must also end "
                                + "fighting in Lebanon. Pakistani mediation language referenced termination of "
                                + "military operations across fronts, including Lebanon—language Israel disputed "
                                + "in practice by maintaining southern Lebanon deployments.",
                        "17 June 2026 — Trump signed an agreement / MoU with Iran. Publicly described elements "
                                + "included: Tehran diluting its stockpile of highly enriched uranium; waiver of "
                                + "certain U.S.-backed sanctions allowing freer Iranian oil sales; reopening pathways "
                                + "for Strait of Hormuz shipping; and a roughly 60-day negotiation window toward a "
                                + "final settlement on nuclear limits, sanctions, and frozen assets.",
                        "22 June 2026 — U.S. Vice President JD Vance said new talks with senior Iranian officials "
                                + "in Switzerland created a “good foundation for a successful final deal.”",
                        "26 June 2026 — Israel and Lebanon announced a U.S.-backed framework agreement described as "
                                + "a first step toward peace, following intensive Washington talks. The framework "
                                + "did not immediately end all Israeli operations or Hezbollah fire; implementation "
                                + "and verification remained contested.",
                        "Late June 2026 — Technical talks were expected to address Hormuz governance, sanctions "
                                + "relief sequencing, and Iran’s nuclear program. Delays were attributed in part to "
                                + "continued fighting and occupation dynamics in southern Lebanon."
                )
        ));

        sections.add(new Section(
                "6. July 2026 (1–12 July): MoU Stress Test and Renewed Escalation",
                List.of(
                        "1 July 2026 — Host Qatar said U.S. and Iranian negotiators met separately with Qatari and "
                                + "Pakistani mediators and that “positive progress” had been made toward a final deal.",
                        "2 July 2026 — Iran’s joint military command warned that all oil tankers moving through the "
                                + "Strait of Hormuz must use Iranian-approved routes or face a “forceful response,” "
                                + "signaling continued Iranian assertion of maritime control despite interim diplomacy.",
                        "4 July 2026 — Iran began a days-long state funeral for the late supreme leader, Khamenei. "
                                + "Talks with the United States on a final war/nuclear settlement were expected to "
                                + "resume after funeral ceremonies concluded (around 11 July in some schedules).",
                        "7 July 2026 — Iran was accused of striking three ships in the Strait of Hormuz after "
                                + "traffic had slowly increased—reportedly the most ships in a single day since late "
                                + "April. The United States responded by striking dozens of targets in Iran and "
                                + "reinstating sanctions on Iranian oil sales. Tehran’s lead negotiator declared that "
                                + "“the era of bullying and extortion is over.”",
                        "8 July 2026 — Trump declared the ceasefire “over” but said negotiations could continue, "
                                + "raising market and diplomatic fears of a full return to multi-front war.",
                        "9–10 July 2026 — The United States launched further airstrikes against Iran. Iran "
                                + "responded by targeting U.S.-allied Middle East countries; sirens sounded repeatedly "
                                + "in Bahrain (Fifth Fleet headquarters) and missiles were reported toward Kuwait and "
                                + "Qatar. U.S. officials said strikes aimed to degrade Iran’s ability to threaten "
                                + "freedom of navigation in Hormuz. Some U.S. strikes reportedly hit bridges in Iran, "
                                + "including routes connected to Mashhad funeral processions.",
                        "10 July 2026 — Despite kinetic exchanges, a U.S. official told Al Jazeera that Washington "
                                + "remained committed to negotiations and that technical talks for a lasting peace "
                                + "deal would continue. Core agenda items remained: Strait of Hormuz future rules, "
                                + "Iran’s frozen assets, long-term sanctions relief, and Tehran’s nuclear program.",
                        "Lebanon status as of early–mid July 2026 — Israel occupied roughly one-fifth of Lebanon "
                                + "according to multiple reports, with near-daily attacks since early March. "
                                + "Casualty and displacement figures cited in open reporting included thousands killed "
                                + "and more than one million displaced. Hezbollah rejected some proposed pilot "
                                + "withdrawal zones in U.S.-brokered frameworks.",
                        "12 July 2026 — End of this corpus window. The interim June MoU remained under severe "
                                + "stress after early-July Hormuz incidents and mutual U.S.–Iran strikes. Final-deal "
                                + "talks were uncertain in timing; funeral-related delays and ceasefire-violation "
                                + "accusations (especially regarding Lebanon and Hormuz) dominated diplomatic messaging. "
                                + "Global oil prices and shipping insurance rates remained highly sensitive to each "
                                + "day’s Hormuz transit and strike reports."
                )
        ));

        sections.add(new Section(
                "7. Cross-Cutting Themes for RAG Retrieval",
                List.of(
                        "Strait of Hormuz: Closed/controlled from 28 February; brief reopenings claimed mid-April "
                                + "and escort attempts in May; MoU sought freer navigation from mid-June; July "
                                + "ship strikes and Iranian route mandates reasserted coercive control.",
                        "Ceasefires and MoUs: April 7 two-week U.S.–Iran pause (Israel excluded); April 21 "
                                + "indefinite extension claim; June 17 interim MoU with ~60-day talks; July 8 "
                                + "Trump “ceasefire over” statement amid continued negotiation rhetoric.",
                        "Lebanon track: Hezbollah entry 2 March; deep Israeli ground war by 31 May; June 3 and "
                                + "June 26 ceasefire/framework announcements; occupation and verification disputes "
                                + "persisting into July.",
                        "Nuclear and sanctions: June 17 terms referenced uranium dilution and sanctions waivers; "
                                + "July 7 U.S. reinstatement of oil-sale sanctions after Hormuz ship attacks; final "
                                + "nuclear limits and frozen-asset release remained negotiation agenda items.",
                        "Actors: United States, Israel, Iran (new supreme leader Mojtaba Khamenei), Hezbollah, "
                                + "Lebanon government negotiators, Qatar and Pakistan as mediators, Gulf host states "
                                + "(Bahrain, Kuwait, Qatar, UAE) affected by missile/drone spillover."
                )
        ));

        sections.add(new Section(
                "8. Suggested Question Types for the Demo Chat",
                List.of(
                        "What happened on 28 February 2026 that started the war?",
                        "When did Hezbollah enter the conflict, and how did Israel respond?",
                        "Summarize the April 2026 ceasefire and Hormuz developments.",
                        "What did the 17 June 2026 U.S.–Iran MoU include?",
                        "Describe Israel–Lebanon diplomatic frameworks in June 2026.",
                        "Why did the ceasefire come under stress in early July 2026?",
                        "What is the status of the Strait of Hormuz across February–July 2026?",
                        "Who mediated U.S.–Iran talks in July 2026 according to this corpus?"
                )
        ));

        sections.add(new Section(
                "9. Source Notes",
                List.of(
                        "Primary narrative spine adapted from Associated Press public timeline reporting on the "
                                + "Iran war and related talks (including dated entries from 28 February through "
                                + "8 July 2026 and follow-on AP/Al Jazeera coverage of 9–10 July exchanges).",
                        "Additional detail on opening strikes, Lebanon operations, and MoU language drawn from "
                                + "open encyclopedic timelines of the 2026 Iran war and contemporaneous agency "
                                + "summaries (e.g., Anadolu Agency 108-day overview).",
                        "Users of this RAG lab should treat answers as grounded only in this PDF unless new "
                                + "documents are ingested. Prefer citing dates and section headings when answering."
                )
        ));

        return sections;
    }

    private static void writeSection(
            PDDocument doc,
            Section section,
            PDType1Font regular,
            PDType1Font bold
    ) throws IOException {
        PDPage page = new PDPage(PDRectangle.LETTER);
        doc.addPage(page);
        float width = page.getMediaBox().getWidth() - 2 * MARGIN;
        float y = page.getMediaBox().getHeight() - MARGIN;

        PDPageContentStream cs = new PDPageContentStream(doc, page);
        y = drawWrapped(cs, bold, HEADING_SIZE, section.title(), MARGIN, y, width, true);
        y -= 8;

        for (String paragraph : section.paragraphs()) {
            List<String> lines = wrap(regular, FONT_SIZE, paragraph, width);
            for (String line : lines) {
                if (y < MARGIN + LEADING) {
                    cs.close();
                    page = new PDPage(PDRectangle.LETTER);
                    doc.addPage(page);
                    cs = new PDPageContentStream(doc, page);
                    y = page.getMediaBox().getHeight() - MARGIN;
                }
                cs.beginText();
                cs.setFont(regular, FONT_SIZE);
                cs.newLineAtOffset(MARGIN, y);
                cs.showText(sanitize(line));
                cs.endText();
                y -= LEADING;
            }
            y -= 8;
        }
        cs.close();
    }

    private static float drawWrapped(
            PDPageContentStream cs,
            PDType1Font font,
            float fontSize,
            String text,
            float x,
            float y,
            float width,
            boolean heading
    ) throws IOException {
        List<String> lines = wrap(font, fontSize, text, width);
        for (String line : lines) {
            cs.beginText();
            cs.setFont(font, fontSize);
            cs.newLineAtOffset(x, y);
            cs.showText(sanitize(line));
            cs.endText();
            y -= heading ? LEADING + 2 : LEADING;
        }
        return y;
    }

    private static List<String> wrap(PDType1Font font, float fontSize, String text, float maxWidth)
            throws IOException {
        List<String> lines = new ArrayList<>();
        String[] words = text.split("\\s+");
        StringBuilder current = new StringBuilder();
        for (String word : words) {
            String candidate = current.isEmpty() ? word : current + " " + word;
            float w = font.getStringWidth(sanitize(candidate)) / 1000 * fontSize;
            if (w > maxWidth && !current.isEmpty()) {
                lines.add(current.toString());
                current = new StringBuilder(word);
            } else {
                current = new StringBuilder(candidate);
            }
        }
        if (!current.isEmpty()) {
            lines.add(current.toString());
        }
        return lines;
    }

    private static String sanitize(String text) {
        return text
                .replace('\u2019', '\'')
                .replace('\u2018', '\'')
                .replace('\u201c', '"')
                .replace('\u201d', '"')
                .replace('\u2013', '-')
                .replace('\u2014', '-')
                .replace("\u2026", "...")
                .replaceAll("[^\\x20-\\x7E]", "?");
    }

    private record Section(String title, List<String> paragraphs) {}
}
