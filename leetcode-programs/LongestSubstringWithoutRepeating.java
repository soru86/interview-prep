import java.util.HashSet;
import java.util.Set;

/**
 * Problem 19: Longest substring without repeating characters
 * Main Concept: Sliding Window
 *
 * Uses a sliding window approach with a HashSet to track characters
 * in the current window.
 * Time: O(n), Space: O(min(n, alphabet_size)).
 */
public class LongestSubstringWithoutRepeating {

    public static int lengthOfLongestSubstring(String s) {
        Set<Character> window = new HashSet<>();
        int left = 0;
        int maxLen = 0;

        for (int right = 0; right < s.length(); right++) {
            char c = s.charAt(right);

            // Shrink window from left until no duplicate
            while (window.contains(c)) {
                window.remove(s.charAt(left));
                left++;
            }

            window.add(c);
            maxLen = Math.max(maxLen, right - left + 1);
        }

        return maxLen;
    }

    public static void main(String[] args) {
        String[] testCases = {"abcabcbb", "bbbbb", "pwwkew", "", "abcdef", "dvdf"};
        int[] expected = {3, 1, 3, 0, 6, 3};

        for (int i = 0; i < testCases.length; i++) {
            int result = lengthOfLongestSubstring(testCases[i]);
            String status = result == expected[i] ? "✓" : "✗";
            System.out.printf("%s  \"%s\" → %d (expected %d)%n",
                    status, testCases[i], result, expected[i]);
        }
    }
}
