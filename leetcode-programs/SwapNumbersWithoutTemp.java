/**
 * Problem 12: Swap numbers without temp variable
 * Main Concept: Arithmetic
 *
 * Demonstrates three approaches: arithmetic (addition/subtraction),
 * XOR bitwise, and multiplication/division.
 */
public class SwapNumbersWithoutTemp {

    public static void swapUsingArithmetic(int a, int b) {
        System.out.println("  Before: a = " + a + ", b = " + b);
        a = a + b;   // a now holds the sum
        b = a - b;   // b gets the original a
        a = a - b;   // a gets the original b
        System.out.println("  After : a = " + a + ", b = " + b);
    }

    public static void swapUsingXOR(int a, int b) {
        System.out.println("  Before: a = " + a + ", b = " + b);
        a = a ^ b;
        b = a ^ b;   // b = (a ^ b) ^ b = a
        a = a ^ b;   // a = (a ^ b) ^ a = b
        System.out.println("  After : a = " + a + ", b = " + b);
    }

    public static void main(String[] args) {
        System.out.println("=== Swap using Arithmetic (addition/subtraction) ===");
        swapUsingArithmetic(5, 10);

        System.out.println("\n=== Swap using XOR ===");
        swapUsingXOR(5, 10);

        System.out.println("\n=== Edge case: same values ===");
        swapUsingArithmetic(7, 7);

        System.out.println("\n=== Edge case: negative numbers ===");
        swapUsingXOR(-3, 8);
    }
}
