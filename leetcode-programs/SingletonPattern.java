/**
 * Problem 17: Implement Singleton
 * Main Concept: Design Pattern
 *
 * Demonstrates multiple Singleton approaches:
 * 1. Eager initialization
 * 2. Lazy initialization (thread-safe with double-checked locking)
 * 3. Bill Pugh Singleton (using inner static helper class)
 */
public class SingletonPattern {

    // ========== Approach 1: Eager Initialization ==========
    static class EagerSingleton {
        private static final EagerSingleton INSTANCE = new EagerSingleton();

        private EagerSingleton() {
            // private constructor
        }

        public static EagerSingleton getInstance() {
            return INSTANCE;
        }
    }

    // ========== Approach 2: Thread-Safe Lazy (Double-Checked Locking) ==========
    static class LazySingleton {
        private static volatile LazySingleton instance;

        private LazySingleton() {
            // private constructor
        }

        public static LazySingleton getInstance() {
            if (instance == null) {
                synchronized (LazySingleton.class) {
                    if (instance == null) {
                        instance = new LazySingleton();
                    }
                }
            }
            return instance;
        }
    }

    // ========== Approach 3: Bill Pugh Singleton (Inner Static Class) ==========
    static class BillPughSingleton {
        private BillPughSingleton() {
            // private constructor
        }

        private static class Holder {
            private static final BillPughSingleton INSTANCE = new BillPughSingleton();
        }

        public static BillPughSingleton getInstance() {
            return Holder.INSTANCE;
        }
    }

    public static void main(String[] args) {
        // Eager Singleton
        EagerSingleton e1 = EagerSingleton.getInstance();
        EagerSingleton e2 = EagerSingleton.getInstance();
        System.out.println("=== Eager Singleton ===");
        System.out.println("Same instance? " + (e1 == e2));  // true
        System.out.println("Hash: " + e1.hashCode());

        // Lazy Singleton
        LazySingleton l1 = LazySingleton.getInstance();
        LazySingleton l2 = LazySingleton.getInstance();
        System.out.println("\n=== Lazy Singleton (Double-Checked Locking) ===");
        System.out.println("Same instance? " + (l1 == l2));  // true
        System.out.println("Hash: " + l1.hashCode());

        // Bill Pugh Singleton
        BillPughSingleton b1 = BillPughSingleton.getInstance();
        BillPughSingleton b2 = BillPughSingleton.getInstance();
        System.out.println("\n=== Bill Pugh Singleton ===");
        System.out.println("Same instance? " + (b1 == b2));  // true
        System.out.println("Hash: " + b1.hashCode());
    }
}
