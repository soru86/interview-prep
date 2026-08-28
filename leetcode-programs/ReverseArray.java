import java.util.Arrays;

/**
 * Problem 14: Reverse an array
 * Main Concept: Two Pointers
 *
 * Reverses an array in-place using two pointers moving toward each other.
 * Time: O(n), Space: O(1).
 */
public class ReverseArray {

    public static void reverse(int[] arr) {
        int left = 0;
        int right = arr.length - 1;

        while (left < right) {
            // Swap elements at left and right
            int temp = arr[left];
            arr[left] = arr[right];
            arr[right] = temp;

            left++;
            right--;
        }
    }

    public static void main(String[] args) {
        int[] arr1 = {1, 2, 3, 4, 5};
        System.out.println("Original: " + Arrays.toString(arr1));
        reverse(arr1);
        System.out.println("Reversed: " + Arrays.toString(arr1));

        int[] arr2 = {10, 20, 30, 40};
        System.out.println("\nOriginal: " + Arrays.toString(arr2));
        reverse(arr2);
        System.out.println("Reversed: " + Arrays.toString(arr2));

        int[] single = {42};
        System.out.println("\nSingle element: " + Arrays.toString(single));
        reverse(single);
        System.out.println("Reversed      : " + Arrays.toString(single));

        int[] empty = {};
        System.out.println("\nEmpty array: " + Arrays.toString(empty));
        reverse(empty);
        System.out.println("Reversed   : " + Arrays.toString(empty));
    }
}
