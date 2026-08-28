import java.util.Arrays;

/**
 * Problem 23: Merge Two Sorted Arrays
 * Main Concept: Two Pointers
 *
 * Merges two sorted arrays into one sorted array using two pointers.
 * Time: O(m + n), Space: O(m + n).
 */
public class MergeTwoSortedArrays {

    public static int[] merge(int[] arr1, int[] arr2) {
        int m = arr1.length;
        int n = arr2.length;
        int[] result = new int[m + n];

        int i = 0, j = 0, k = 0;

        // Compare and merge
        while (i < m && j < n) {
            if (arr1[i] <= arr2[j]) {
                result[k++] = arr1[i++];
            } else {
                result[k++] = arr2[j++];
            }
        }

        // Copy remaining elements from arr1
        while (i < m) {
            result[k++] = arr1[i++];
        }

        // Copy remaining elements from arr2
        while (j < n) {
            result[k++] = arr2[j++];
        }

        return result;
    }

    public static void main(String[] args) {
        int[] a1 = {1, 3, 5, 7};
        int[] b1 = {2, 4, 6, 8};
        System.out.println("Array 1: " + Arrays.toString(a1));
        System.out.println("Array 2: " + Arrays.toString(b1));
        System.out.println("Merged : " + Arrays.toString(merge(a1, b1)));
        // Expected: [1, 2, 3, 4, 5, 6, 7, 8]

        int[] a2 = {1, 2, 3};
        int[] b2 = {4, 5, 6, 7, 8};
        System.out.println("\nArray 1: " + Arrays.toString(a2));
        System.out.println("Array 2: " + Arrays.toString(b2));
        System.out.println("Merged : " + Arrays.toString(merge(a2, b2)));
        // Expected: [1, 2, 3, 4, 5, 6, 7, 8]

        int[] a3 = {};
        int[] b3 = {1, 2, 3};
        System.out.println("\nArray 1: " + Arrays.toString(a3));
        System.out.println("Array 2: " + Arrays.toString(b3));
        System.out.println("Merged : " + Arrays.toString(merge(a3, b3)));
        // Expected: [1, 2, 3]

        int[] a4 = {1, 1, 1};
        int[] b4 = {1, 1, 1};
        System.out.println("\nArray 1: " + Arrays.toString(a4));
        System.out.println("Array 2: " + Arrays.toString(b4));
        System.out.println("Merged : " + Arrays.toString(merge(a4, b4)));
        // Expected: [1, 1, 1, 1, 1, 1]
    }
}
