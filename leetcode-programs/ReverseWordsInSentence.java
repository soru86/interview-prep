/**
 * Problem 27: Reverse Words in Sentence
 * Main Concept: String Manipulation
 *
 * Reverses the order of words in a given sentence.
 * Handles multiple spaces between words.
 * Time: O(n), Space: O(n).
 */
public class ReverseWordsInSentence {

    // Approach 1: Using split and StringBuilder
    public static String reverseWords(String s) {
        String[] words = s.trim().split("\\s+");
        StringBuilder sb = new StringBuilder();

        for (int i = words.length - 1; i >= 0; i--) {
            sb.append(words[i]);
            if (i > 0) {
                sb.append(" ");
            }
        }

        return sb.toString();
    }

    // Approach 2: Manual (two-pointer, in-place style with char array)
    public static String reverseWordsManual(String s) {
        char[] chars = s.trim().toCharArray();
        int n = chars.length;

        // Step 1: Reverse entire string
        reverse(chars, 0, n - 1);

        // Step 2: Reverse each word
        int start = 0;
        for (int end = 0; end <= n; end++) {
            if (end == n || chars[end] == ' ') {
                reverse(chars, start, end - 1);
                start = end + 1;
            }
        }

        // Step 3: Clean up extra spaces
        StringBuilder sb = new StringBuilder();
        boolean prevSpace = false;
        for (char c : chars) {
            if (c == ' ') {
                if (!prevSpace && sb.length() > 0) {
                    sb.append(' ');
                }
                prevSpace = true;
            } else {
                sb.append(c);
                prevSpace = false;
            }
        }

        return sb.toString().trim();
    }

    private static void reverse(char[] arr, int left, int right) {
        while (left < right) {
            char temp = arr[left];
            arr[left] = arr[right];
            arr[right] = temp;
            left++;
            right--;
        }
    }

    public static void main(String[] args) {
        String[] testCases = {
                "the sky is blue",
                "  hello world  ",
                "a good   example",
                "Java is awesome",
                "single"
        };

        System.out.println("=== Using split + StringBuilder ===");
        for (String test : testCases) {
            System.out.printf("  \"%s\" → \"%s\"%n", test, reverseWords(test));
        }

        System.out.println("\n=== Using manual reverse ===");
        for (String test : testCases) {
            System.out.printf("  \"%s\" → \"%s\"%n", test, reverseWordsManual(test));
        }
    }
}
