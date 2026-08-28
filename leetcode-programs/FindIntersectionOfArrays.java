import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

/**
 * Problem 16: Find intersection of arrays
 * Main Concept: Set
 *
 * Finds elements common to both arrays using HashSet intersection.
 * Time: O(m + n), Space: O(min(m, n)).
 */
public class FindIntersectionOfArrays {

    public static int[] intersection(int[] nums1, int[] nums2) {
        Set<Integer> set1 = new HashSet<>();
        for (int num : nums1) {
            set1.add(num);
        }

        Set<Integer> resultSet = new HashSet<>();
        for (int num : nums2) {
            if (set1.contains(num)) {
                resultSet.add(num);
            }
        }

        return resultSet.stream().mapToInt(Integer::intValue).toArray();
    }

    public static void main(String[] args) {
        int[] a1 = {1, 2, 2, 1};
        int[] b1 = {2, 2};
        System.out.println("Array 1     : " + Arrays.toString(a1));
        System.out.println("Array 2     : " + Arrays.toString(b1));
        System.out.println("Intersection: " + Arrays.toString(intersection(a1, b1)));
        // Expected: [2]

        int[] a2 = {4, 9, 5};
        int[] b2 = {9, 4, 9, 8, 4};
        System.out.println("\nArray 1     : " + Arrays.toString(a2));
        System.out.println("Array 2     : " + Arrays.toString(b2));
        System.out.println("Intersection: " + Arrays.toString(intersection(a2, b2)));
        // Expected: [4, 9] (order may vary)

        int[] a3 = {1, 2, 3};
        int[] b3 = {4, 5, 6};
        System.out.println("\nArray 1     : " + Arrays.toString(a3));
        System.out.println("Array 2     : " + Arrays.toString(b3));
        System.out.println("Intersection: " + Arrays.toString(intersection(a3, b3)));
        // Expected: []
    }
}
