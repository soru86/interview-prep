import java.util.HashMap;
import java.util.Map;

/**
 * Problem 18: Implement LRU Cache
 * Main Concept: HashMap + Doubly Linked List (DLL)
 *
 * An LRU (Least Recently Used) cache that supports get and put in O(1) time.
 * - HashMap provides O(1) key lookup.
 * - Doubly Linked List maintains access order for O(1) eviction.
 */
public class LRUCacheImpl {

    // ========== Doubly Linked List Node ==========
    static class Node {
        int key, value;
        Node prev, next;

        Node(int key, int value) {
            this.key = key;
            this.value = value;
        }
    }

    // ========== LRU Cache ==========
    static class LRUCache {
        private final int capacity;
        private final Map<Integer, Node> cache;
        private final Node head; // dummy head (most recently used side)
        private final Node tail; // dummy tail (least recently used side)

        public LRUCache(int capacity) {
            this.capacity = capacity;
            this.cache = new HashMap<>();
            // Initialize dummy head and tail
            this.head = new Node(-1, -1);
            this.tail = new Node(-1, -1);
            head.next = tail;
            tail.prev = head;
        }

        public int get(int key) {
            if (!cache.containsKey(key)) {
                return -1;
            }
            Node node = cache.get(key);
            // Move to front (most recently used)
            removeNode(node);
            addToFront(node);
            return node.value;
        }

        public void put(int key, int value) {
            if (cache.containsKey(key)) {
                // Update existing key
                Node node = cache.get(key);
                node.value = value;
                removeNode(node);
                addToFront(node);
            } else {
                // Evict if at capacity
                if (cache.size() == capacity) {
                    Node lru = tail.prev;
                    removeNode(lru);
                    cache.remove(lru.key);
                }
                // Insert new node
                Node newNode = new Node(key, value);
                addToFront(newNode);
                cache.put(key, newNode);
            }
        }

        private void addToFront(Node node) {
            node.next = head.next;
            node.prev = head;
            head.next.prev = node;
            head.next = node;
        }

        private void removeNode(Node node) {
            node.prev.next = node.next;
            node.next.prev = node.prev;
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder("[");
            Node curr = head.next;
            while (curr != tail) {
                sb.append("(").append(curr.key).append(":").append(curr.value).append(")");
                curr = curr.next;
                if (curr != tail) sb.append(" → ");
            }
            sb.append("]");
            return sb.toString();
        }
    }

    public static void main(String[] args) {
        LRUCache lru = new LRUCache(3);

        lru.put(1, 10);
        lru.put(2, 20);
        lru.put(3, 30);
        System.out.println("After put(1,10), put(2,20), put(3,30): " + lru);

        System.out.println("get(2) = " + lru.get(2));  // 20, moves key 2 to front
        System.out.println("Cache state: " + lru);

        lru.put(4, 40); // Evicts key 1 (least recently used)
        System.out.println("\nAfter put(4,40) — key 1 evicted: " + lru);

        System.out.println("get(1) = " + lru.get(1));  // -1 (evicted)
        System.out.println("get(3) = " + lru.get(3));  // 30
        System.out.println("get(4) = " + lru.get(4));  // 40

        lru.put(5, 50); // Evicts key 2
        System.out.println("\nAfter put(5,50) — key 2 evicted: " + lru);
        System.out.println("get(2) = " + lru.get(2));  // -1 (evicted)
    }
}
