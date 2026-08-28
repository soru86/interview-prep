import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.Set;

/**
 * Problem 11: Remove duplicates from array
 * Main Concept: HashSet
 *
 * Uses a LinkedHashSet to remove duplicates while preserving insertion order.
 */
public class RemoveDuplicatesFromArray {

    public static int[] removeDuplicates(int[] arr) {
        Set<Integer> seen = new LinkedHashSet<>();
        for (int num : arr) {
            seen.add(num);
        }
        return seen.stream().mapToInt(Integer::intValue).toArray();
    }

    public static void main(String[] args) {
        int[] arr = {1, 2, 3, 2, 4, 1, 5, 3, 6};

        System.out.println("Original array : " + Arrays.toString(arr));
        int[] result = removeDuplicates(arr);
        System.out.println("After removing duplicates: " + Arrays.toString(result));

        // Edge cases
        int[] empty = {};
        System.out.println("\nEmpty array    : " + Arrays.toString(removeDuplicates(empty)));

        int[] single = {7};
        System.out.println("Single element : " + Arrays.toString(removeDuplicates(single)));

        int[] allSame = {5, 5, 5, 5};
        System.out.println("All same       : " + Arrays.toString(removeDuplicates(allSame)));
    }
}
