import { randomUUID } from 'node:crypto';

export interface Customer {
  id: string;
  name: string;
  email: string;
  phone: string;
  ssn: string;
  cardNumber: string;
  createdAt: string;
}

const customers = new Map<string, Customer>();

customers.set('c-1', {
  id: 'c-1',
  name: 'Jordan Lee',
  email: 'jordan.lee@example.com',
  phone: '+1 (555) 010-4477',
  ssn: '123-45-6789',
  cardNumber: '4111111111111111',
  createdAt: new Date().toISOString(),
});

export function listCustomers(): Customer[] {
  return [...customers.values()];
}

export function getCustomer(id: string): Customer | undefined {
  return customers.get(id);
}

export function createCustomer(
  input: Omit<Customer, 'id' | 'createdAt'>,
): Customer {
  const customer: Customer = {
    ...input,
    id: randomUUID(),
    createdAt: new Date().toISOString(),
  };
  customers.set(customer.id, customer);
  return customer;
}
