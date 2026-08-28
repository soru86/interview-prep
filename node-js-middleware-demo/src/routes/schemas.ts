import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

export const createCustomerSchema = z.object({
  name: z.string().min(1).max(120),
  email: z.string().email(),
  phone: z.string().min(7).max(40),
  ssn: z.string().regex(/^\d{3}-\d{2}-\d{4}$/, 'SSN must be ###-##-####'),
  cardNumber: z.string().regex(/^\d{13,19}$/, 'Card number must be 13-19 digits'),
});

export const createOrderSchema = z.object({
  customerId: z.string().min(1),
  sku: z.string().min(1).max(64),
  quantity: z.number().int().positive().max(1000),
  amountCents: z.number().int().nonnegative(),
});

export const idParamSchema = z.object({
  id: z.string().min(1),
});
