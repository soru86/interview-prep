import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/**
 * Problem 21: Two Sum
 * Main Concept: HashMap
 *
 * Given an array of integers and a target, return indices of two numbers
 * that add up to the target. Uses a HashMap for O(n) lookup.
 * Time: O(n), Space: O(n).
 */
public class TwoSum {

    public static int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> map = new HashMap<>(); // value → index

        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (map.containsKey(complement)) {
                return new int[]{map.get(complement), i};
            }
            map.put(nums[i], i);
        }

        return new int[]{}; // no solution found
    }

    public static void main(String[] args) {
        int[] nums1 = {2, 7, 11, 15};
        int target1 = 9;
        System.out.println("Array: " + Arrays.toString(nums1) + ", Target: " + target1);
        System.out.println("Indices: " + Arrays.toString(twoSum(nums1, target1)));
        // Expected: [0, 1]

        int[] nums2 = {3, 2, 4};
        int target2 = 6;
        System.out.println("\nArray: " + Arrays.toString(nums2) + ", Target: " + target2);
        System.out.println("Indices: " + Arrays.toString(twoSum(nums2, target2)));
        // Expected: [1, 2]

        int[] nums3 = {3, 3};
        int target3 = 6;
        System.out.println("\nArray: " + Arrays.toString(nums3) + ", Target: " + target3);
        System.out.println("Indices: " + Arrays.toString(twoSum(nums3, target3)));
        // Expected: [0, 1]
    }
}
