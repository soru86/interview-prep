import java.util.Arrays;
import java.util.Comparator;
import java.util.stream.IntStream;

/**
 * Problem 20: Sort array using streams
 * Main Concept: Java Streams
 *
 * Demonstrates sorting arrays using Java Stream API for both
 * primitive arrays and object arrays.
 */
public class SortArrayUsingStreams {

    public static void main(String[] args) {
        // 1. Sort int array in ascending order
        int[] nums = {5, 3, 8, 1, 9, 2, 7};
        int[] sortedAsc = IntStream.of(nums).sorted().toArray();
        System.out.println("Original     : " + Arrays.toString(nums));
        System.out.println("Sorted (asc) : " + Arrays.toString(sortedAsc));

        // 2. Sort int array in descending order
        int[] sortedDesc = IntStream.of(nums)
                .boxed()
                .sorted(Comparator.reverseOrder())
                .mapToInt(Integer::intValue)
                .toArray();
        System.out.println("Sorted (desc): " + Arrays.toString(sortedDesc));

        // 3. Sort String array
        String[] words = {"banana", "apple", "cherry", "date"};
        String[] sortedWords = Arrays.stream(words).sorted().toArray(String[]::new);
        System.out.println("\nOriginal     : " + Arrays.toString(words));
        System.out.println("Sorted       : " + Arrays.toString(sortedWords));

        // 4. Sort by string length
        String[] sortedByLen = Arrays.stream(words)
                .sorted(Comparator.comparingInt(String::length))
                .toArray(String[]::new);
        System.out.println("Sorted by len: " + Arrays.toString(sortedByLen));

        // 5. Sort with custom comparator (even numbers first, then odd)
        int[] mixed = {7, 2, 5, 4, 1, 8, 3, 6};
        int[] evenFirst = IntStream.of(mixed)
                .boxed()
                .sorted(Comparator.<Integer, Integer>comparing(n -> n % 2).thenComparing(n -> n))
                .mapToInt(Integer::intValue)
                .toArray();
        System.out.println("\nOriginal         : " + Arrays.toString(mixed));
        System.out.println("Even first sorted: " + Arrays.toString(evenFirst));
    }
}
