import java.util.Arrays;

/**
 * Problem 13: Find missing number in array
 * Main Concept: Math + Arrays
 *
 * Given an array containing n distinct numbers from 0 to n,
 * find the one number that is missing.
 * Uses the sum formula: n*(n+1)/2 minus the actual sum.
 */
public class FindMissingNumber {

    // Approach 1: Mathematical (sum formula)
    public static int findMissingUsingSumFormula(int[] nums) {
        int n = nums.length;
        long expectedSum = (long) n * (n + 1) / 2;
        long actualSum = 0;
        for (int num : nums) {
            actualSum += num;
        }
        return (int) (expectedSum - actualSum);
    }

    // Approach 2: XOR (avoids potential overflow)
    public static int findMissingUsingXOR(int[] nums) {
        int xor = nums.length; // start with n
        for (int i = 0; i < nums.length; i++) {
            xor ^= i ^ nums[i];
        }
        return xor;
    }

    public static void main(String[] args) {
        int[] arr1 = {3, 0, 1};           // missing 2
        int[] arr2 = {0, 1, 2, 4, 5};     // missing 3
        int[] arr3 = {9, 6, 4, 2, 3, 5, 7, 0, 1}; // missing 8
        int[] arr4 = {0};                  // missing 1

        System.out.println("=== Sum Formula Approach ===");
        System.out.println(Arrays.toString(arr1) + " → Missing: " + findMissingUsingSumFormula(arr1));
        System.out.println(Arrays.toString(arr2) + " → Missing: " + findMissingUsingSumFormula(arr2));
        System.out.println(Arrays.toString(arr3) + " → Missing: " + findMissingUsingSumFormula(arr3));
        System.out.println(Arrays.toString(arr4) + " → Missing: " + findMissingUsingSumFormula(arr4));

        System.out.println("\n=== XOR Approach ===");
        System.out.println(Arrays.toString(arr1) + " → Missing: " + findMissingUsingXOR(arr1));
        System.out.println(Arrays.toString(arr2) + " → Missing: " + findMissingUsingXOR(arr2));
        System.out.println(Arrays.toString(arr3) + " → Missing: " + findMissingUsingXOR(arr3));
        System.out.println(Arrays.toString(arr4) + " → Missing: " + findMissingUsingXOR(arr4));
    }
}
