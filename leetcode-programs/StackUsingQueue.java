import java.util.LinkedList;
import java.util.Queue;

/**
 * Problem 29: Stack using Queue
 * Main Concept: Data Structure Design
 *
 * Implements a LIFO stack using two queues.
 * Push is O(n) — after adding the new element, all previous elements
 * are dequeued and re-enqueued behind it, so the newest is always at front.
 * Pop and top are O(1).
 */
public class StackUsingQueue {

    static class MyStack {
        private Queue<Integer> q1;
        private Queue<Integer> q2;

        public MyStack() {
            q1 = new LinkedList<>();
            q2 = new LinkedList<>();
        }

        // Push: O(n) — makes the new element the front of q1
        public void push(int x) {
            q2.offer(x);
            // Move all elements from q1 to q2 (behind the new element)
            while (!q1.isEmpty()) {
                q2.offer(q1.poll());
            }
            // Swap q1 and q2
            Queue<Integer> temp = q1;
            q1 = q2;
            q2 = temp;
        }

        // Pop: O(1)
        public int pop() {
            if (q1.isEmpty()) {
                throw new RuntimeException("Stack is empty");
            }
            return q1.poll();
        }

        // Top: O(1)
        public int top() {
            if (q1.isEmpty()) {
                throw new RuntimeException("Stack is empty");
            }
            return q1.peek();
        }

        // isEmpty: O(1)
        public boolean isEmpty() {
            return q1.isEmpty();
        }

        public int size() {
            return q1.size();
        }
    }

    public static void main(String[] args) {
        MyStack stack = new MyStack();

        stack.push(1);
        stack.push(2);
        stack.push(3);
        System.out.println("Pushed: 1, 2, 3");

        System.out.println("Top   : " + stack.top());   // 3
        System.out.println("Pop   : " + stack.pop());    // 3
        System.out.println("Pop   : " + stack.pop());    // 2
        System.out.println("Top   : " + stack.top());    // 1
        System.out.println("Empty?: " + stack.isEmpty()); // false

        stack.push(4);
        System.out.println("\nPushed: 4");
        System.out.println("Top   : " + stack.top());    // 4
        System.out.println("Pop   : " + stack.pop());    // 4
        System.out.println("Pop   : " + stack.pop());    // 1
        System.out.println("Empty?: " + stack.isEmpty()); // true
    }
}
