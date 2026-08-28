import java.util.Arrays;

/**
 * Problem 24: Rotate Array
 * Main Concept: Array Logic
 *
 * Rotates an array to the right by k steps.
 * Uses the reversal algorithm for O(n) time and O(1) space.
 */
public class RotateArray {

    public static void rotate(int[] nums, int k) {
        int n = nums.length;
        if (n == 0) return;

        k = k % n; // handle k > n
        if (k == 0) return;

        // Reverse the entire array
        reverse(nums, 0, n - 1);
        // Reverse the first k elements
        reverse(nums, 0, k - 1);
        // Reverse the remaining elements
        reverse(nums, k, n - 1);
    }

    private static void reverse(int[] arr, int start, int end) {
        while (start < end) {
            int temp = arr[start];
            arr[start] = arr[end];
            arr[end] = temp;
            start++;
            end--;
        }
    }

    public static void main(String[] args) {
        int[] arr1 = {1, 2, 3, 4, 5, 6, 7};
        System.out.println("Original : " + Arrays.toString(arr1));
        rotate(arr1, 3);
        System.out.println("Rotate 3 : " + Arrays.toString(arr1));
        // Expected: [5, 6, 7, 1, 2, 3, 4]

        int[] arr2 = {-1, -100, 3, 99};
        System.out.println("\nOriginal : " + Arrays.toString(arr2));
        rotate(arr2, 2);
        System.out.println("Rotate 2 : " + Arrays.toString(arr2));
        // Expected: [3, 99, -1, -100]

        int[] arr3 = {1, 2, 3};
        System.out.println("\nOriginal : " + Arrays.toString(arr3));
        rotate(arr3, 5); // k > n, effectively rotate by 2
        System.out.println("Rotate 5 : " + Arrays.toString(arr3));
        // Expected: [2, 3, 1]

        int[] arr4 = {1};
        System.out.println("\nOriginal : " + Arrays.toString(arr4));
        rotate(arr4, 10);
        System.out.println("Rotate 10: " + Arrays.toString(arr4));
        // Expected: [1]
    }
}
