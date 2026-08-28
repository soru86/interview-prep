/**
 * Problem 26: Longest Common Prefix
 * Main Concept: String Traversal
 *
 * Finds the longest common prefix string among an array of strings.
 * Uses vertical scanning: compare characters column by column.
 * Time: O(S) where S is the sum of all characters, Space: O(1).
 */
public class LongestCommonPrefix {

    public static String longestCommonPrefix(String[] strs) {
        if (strs == null || strs.length == 0) {
            return "";
        }

        // Use the first string as reference
        String prefix = strs[0];

        for (int i = 1; i < strs.length; i++) {
            // Shrink prefix until it matches the start of strs[i]
            while (!strs[i].startsWith(prefix)) {
                prefix = prefix.substring(0, prefix.length() - 1);
                if (prefix.isEmpty()) {
                    return "";
                }
            }
        }

        return prefix;
    }

    public static void main(String[] args) {
        String[][] testCases = {
                {"flower", "flow", "flight"},         // "fl"
                {"dog", "racecar", "car"},             // ""
                {"interspecies", "interstellar", "interstate"}, // "inters"
                {"alone"},                             // "alone"
                {"", "b"},                             // ""
                {"abc", "abc", "abc"}                  // "abc"
        };

        for (String[] test : testCases) {
            String result = longestCommonPrefix(test);
            System.out.printf("  [%s] → \"%s\"%n", String.join(", ", test), result);
        }
    }
}
