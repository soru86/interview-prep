import java.util.ArrayDeque;
import java.util.Deque;

/**
 * Problem 30: Queue using Stack
 * Main Concept: Data Structure Design
 *
 * Implements a FIFO queue using two stacks.
 * Uses amortized O(1) approach: elements are moved from inStack
 * to outStack only when outStack is empty.
 * Enqueue: O(1), Dequeue: amortized O(1).
 */
public class QueueUsingStack {

    static class MyQueue {
        private Deque<Integer> inStack;   // for enqueue
        private Deque<Integer> outStack;  // for dequeue

        public MyQueue() {
            inStack = new ArrayDeque<>();
            outStack = new ArrayDeque<>();
        }

        // Enqueue: O(1)
        public void enqueue(int x) {
            inStack.push(x);
        }

        // Dequeue: amortized O(1)
        public int dequeue() {
            if (outStack.isEmpty()) {
                if (inStack.isEmpty()) {
                    throw new RuntimeException("Queue is empty");
                }
                // Transfer all elements from inStack to outStack
                while (!inStack.isEmpty()) {
                    outStack.push(inStack.pop());
                }
            }
            return outStack.pop();
        }

        // Peek: amortized O(1)
        public int peek() {
            if (outStack.isEmpty()) {
                if (inStack.isEmpty()) {
                    throw new RuntimeException("Queue is empty");
                }
                while (!inStack.isEmpty()) {
                    outStack.push(inStack.pop());
                }
            }
            return outStack.peek();
        }

        // isEmpty: O(1)
        public boolean isEmpty() {
            return inStack.isEmpty() && outStack.isEmpty();
        }

        public int size() {
            return inStack.size() + outStack.size();
        }
    }

    public static void main(String[] args) {
        MyQueue queue = new MyQueue();

        queue.enqueue(1);
        queue.enqueue(2);
        queue.enqueue(3);
        System.out.println("Enqueued: 1, 2, 3");

        System.out.println("Peek    : " + queue.peek());     // 1
        System.out.println("Dequeue : " + queue.dequeue());   // 1
        System.out.println("Dequeue : " + queue.dequeue());   // 2

        queue.enqueue(4);
        System.out.println("\nEnqueued: 4");
        System.out.println("Peek    : " + queue.peek());     // 3
        System.out.println("Dequeue : " + queue.dequeue());   // 3
        System.out.println("Dequeue : " + queue.dequeue());   // 4
        System.out.println("Empty?  : " + queue.isEmpty());   // true
    }
}
