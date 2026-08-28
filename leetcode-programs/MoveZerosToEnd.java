import java.util.Arrays;

/**
 * Problem 15: Move all zeros to end
 * Main Concept: Array manipulation
 *
 * Moves all zeros to the end of the array while maintaining
 * the relative order of non-zero elements. Done in-place.
 * Time: O(n), Space: O(1).
 */
public class MoveZerosToEnd {

    public static void moveZeros(int[] nums) {
        int insertPos = 0; // position to place next non-zero element

        // Move all non-zero elements forward
        for (int i = 0; i < nums.length; i++) {
            if (nums[i] != 0) {
                nums[insertPos] = nums[i];
                insertPos++;
            }
        }

        // Fill remaining positions with zeros
        while (insertPos < nums.length) {
            nums[insertPos] = 0;
            insertPos++;
        }
    }

    public static void main(String[] args) {
        int[] arr1 = {0, 1, 0, 3, 12};
        System.out.println("Original: " + Arrays.toString(arr1));
        moveZeros(arr1);
        System.out.println("Result  : " + Arrays.toString(arr1));
        // Expected: [1, 3, 12, 0, 0]

        int[] arr2 = {0, 0, 0, 1};
        System.out.println("\nOriginal: " + Arrays.toString(arr2));
        moveZeros(arr2);
        System.out.println("Result  : " + Arrays.toString(arr2));
        // Expected: [1, 0, 0, 0]

        int[] arr3 = {1, 2, 3};
        System.out.println("\nOriginal: " + Arrays.toString(arr3));
        moveZeros(arr3);
        System.out.println("Result  : " + Arrays.toString(arr3));
        // Expected: [1, 2, 3]

        int[] arr4 = {0};
        System.out.println("\nOriginal: " + Arrays.toString(arr4));
        moveZeros(arr4);
        System.out.println("Result  : " + Arrays.toString(arr4));
        // Expected: [0]
    }
}
