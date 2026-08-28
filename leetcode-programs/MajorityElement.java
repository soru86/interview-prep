import java.util.Arrays;

/**
 * Problem 28: Majority Element
 * Main Concept: Boyer-Moore Voting Algorithm
 *
 * Finds the element that appears more than n/2 times in the array.
 * Boyer-Moore achieves this in O(n) time and O(1) space.
 */
public class MajorityElement {

    public static int majorityElement(int[] nums) {
        // Phase 1: Find a candidate
        int candidate = nums[0];
        int count = 1;

        for (int i = 1; i < nums.length; i++) {
            if (count == 0) {
                candidate = nums[i];
                count = 1;
            } else if (nums[i] == candidate) {
                count++;
            } else {
                count--;
            }
        }

        // Phase 2: Verify the candidate (optional if majority is guaranteed)
        int occurrences = 0;
        for (int num : nums) {
            if (num == candidate) {
                occurrences++;
            }
        }

        if (occurrences > nums.length / 2) {
            return candidate;
        }

        throw new IllegalArgumentException("No majority element exists");
    }

    public static void main(String[] args) {
        int[] arr1 = {3, 2, 3};
        System.out.println("Array: " + Arrays.toString(arr1));
        System.out.println("Majority element: " + majorityElement(arr1));
        // Expected: 3

        int[] arr2 = {2, 2, 1, 1, 1, 2, 2};
        System.out.println("\nArray: " + Arrays.toString(arr2));
        System.out.println("Majority element: " + majorityElement(arr2));
        // Expected: 2

        int[] arr3 = {1};
        System.out.println("\nArray: " + Arrays.toString(arr3));
        System.out.println("Majority element: " + majorityElement(arr3));
        // Expected: 1

        int[] arr4 = {6, 5, 5};
        System.out.println("\nArray: " + Arrays.toString(arr4));
        System.out.println("Majority element: " + majorityElement(arr4));
        // Expected: 5
    }
}
