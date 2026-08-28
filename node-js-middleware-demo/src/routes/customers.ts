import { Router } from 'express';
import { authenticate } from '../middleware/auth/authenticate';
import { requireRoles } from '../middleware/auth/roles';
import { validate } from '../middleware/validation/validate';
import { asyncHandler } from '../middleware/errors/asyncHandler';
import { responseMaskMiddleware } from '../middleware/privacy/responseMask';
import { createCustomer, getCustomer, listCustomers } from '../services/customerStore';
import { AppError } from '../utils/AppError';
import { createCustomerSchema, idParamSchema } from './schemas';

const router = Router();

router.use(authenticate, responseMaskMiddleware);

router.get(
  '/',
  asyncHandler(async (_req, res) => {
    const data = listCustomers();
    res.setHeader('Cache-Control', 'private, max-age=30');
    res.json({ data, etagHint: true });
  }),
);

router.get(
  '/:id',
  validate({ params: idParamSchema }),
  asyncHandler(async (req, res) => {
    const customer = getCustomer(req.params.id);
    if (!customer) throw new AppError('Customer not found', 404, 'CUSTOMER_NOT_FOUND');
    res.json({ data: customer });
  }),
);

router.post(
  '/',
  requireRoles('admin', 'user'),
  validate({ body: createCustomerSchema }),
  asyncHandler(async (req, res) => {
    const customer = createCustomer(req.body);
    res.status(201).json({ data: customer });
  }),
);

export default router;
