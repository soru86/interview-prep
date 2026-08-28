import { randomUUID } from 'node:crypto';

export interface Order {
  id: string;
  customerId: string;
  sku: string;
  quantity: number;
  amountCents: number;
  createdBy: string;
  createdAt: string;
  idempotencyKey?: string;
}

const orders = new Map<string, Order>();
const byIdempotency = new Map<string, string>();

export function listOrders(): Order[] {
  return [...orders.values()];
}

export function getOrder(id: string): Order | undefined {
  return orders.get(id);
}

export function findByIdempotencyKey(key: string): Order | undefined {
  const id = byIdempotency.get(key);
  return id ? orders.get(id) : undefined;
}

export function createOrder(
  input: Omit<Order, 'id' | 'createdAt'> & { idempotencyKey?: string },
): Order {
  if (input.idempotencyKey) {
    const existing = findByIdempotencyKey(input.idempotencyKey);
    if (existing) return existing;
  }

  const order: Order = {
    id: randomUUID(),
    customerId: input.customerId,
    sku: input.sku,
    quantity: input.quantity,
    amountCents: input.amountCents,
    createdBy: input.createdBy,
    createdAt: new Date().toISOString(),
    idempotencyKey: input.idempotencyKey,
  };
  orders.set(order.id, order);
  if (order.idempotencyKey) {
    byIdempotency.set(order.idempotencyKey, order.id);
  }
  return order;
}
