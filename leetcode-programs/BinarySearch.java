/**
 * Problem 22: Binary Search
 * Main Concept: Divide & Conquer
 *
 * Searches for a target value in a sorted array.
 * Implements both iterative and recursive approaches.
 * Time: O(log n), Space: O(1) iterative / O(log n) recursive.
 */
public class BinarySearch {

    // Iterative approach
    public static int binarySearchIterative(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;

        while (left <= right) {
            int mid = left + (right - left) / 2;  // avoids integer overflow

            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        return -1; // not found
    }

    // Recursive approach
    public static int binarySearchRecursive(int[] arr, int target, int left, int right) {
        if (left > right) {
            return -1;
        }

        int mid = left + (right - left) / 2;

        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            return binarySearchRecursive(arr, target, mid + 1, right);
        } else {
            return binarySearchRecursive(arr, target, left, mid - 1);
        }
    }

    public static void main(String[] args) {
        int[] sortedArr = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};

        System.out.println("Array: [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]");

        // Iterative tests
        System.out.println("\n=== Iterative Binary Search ===");
        System.out.println("Search 23: index = " + binarySearchIterative(sortedArr, 23));  // 5
        System.out.println("Search 2 : index = " + binarySearchIterative(sortedArr, 2));   // 0
        System.out.println("Search 91: index = " + binarySearchIterative(sortedArr, 91));  // 9
        System.out.println("Search 50: index = " + binarySearchIterative(sortedArr, 50));  // -1

        // Recursive tests
        System.out.println("\n=== Recursive Binary Search ===");
        System.out.println("Search 23: index = " + binarySearchRecursive(sortedArr, 23, 0, sortedArr.length - 1));
        System.out.println("Search 2 : index = " + binarySearchRecursive(sortedArr, 2, 0, sortedArr.length - 1));
        System.out.println("Search 91: index = " + binarySearchRecursive(sortedArr, 91, 0, sortedArr.length - 1));
        System.out.println("Search 50: index = " + binarySearchRecursive(sortedArr, 50, 0, sortedArr.length - 1));
    }
}
