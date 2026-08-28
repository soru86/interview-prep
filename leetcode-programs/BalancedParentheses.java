import java.util.ArrayDeque;
import java.util.Deque;

/**
 * Problem 25: Balanced Parentheses
 * Main Concept: Stack
 *
 * Checks if a string of parentheses (), {}, [] is balanced.
 * Uses a stack to match opening and closing brackets.
 * Time: O(n), Space: O(n).
 */
public class BalancedParentheses {

    public static boolean isBalanced(String s) {
        Deque<Character> stack = new ArrayDeque<>();

        for (char c : s.toCharArray()) {
            if (c == '(' || c == '{' || c == '[') {
                stack.push(c);
            } else if (c == ')' || c == '}' || c == ']') {
                if (stack.isEmpty()) {
                    return false;
                }
                char top = stack.pop();
                if (!isMatchingPair(top, c)) {
                    return false;
                }
            }
        }

        return stack.isEmpty();
    }

    private static boolean isMatchingPair(char open, char close) {
        return (open == '(' && close == ')')
                || (open == '{' && close == '}')
                || (open == '[' && close == ']');
    }

    public static void main(String[] args) {
        String[] testCases = {
                "()",           // true
                "()[]{}",       // true
                "(]",           // false
                "([)]",         // false
                "{[]}",         // true
                "",             // true (empty is balanced)
                "((()))",       // true
                "({[()]})",     // true
                "(((",          // false
                ")("            // false
        };

        for (String test : testCases) {
            System.out.printf("  \"%s\" → %s%n", test, isBalanced(test));
        }
    }
}
