import { Router } from 'express';
import { authenticate } from '../middleware/auth/authenticate';
import { validate } from '../middleware/validation/validate';
import { asyncHandler } from '../middleware/errors/asyncHandler';
import { idempotencyMiddleware } from '../middleware/request/idempotency';
import { createOrder, getOrder, listOrders } from '../services/orderStore';
import { getCustomer } from '../services/customerStore';
import { AppError } from '../utils/AppError';
import { createOrderSchema, idParamSchema } from './schemas';

const router = Router();

router.use(authenticate);

router.get(
  '/',
  asyncHandler(async (_req, res) => {
    res.json({ data: listOrders() });
  }),
);

router.get(
  '/:id',
  validate({ params: idParamSchema }),
  asyncHandler(async (req, res) => {
    const order = getOrder(req.params.id);
    if (!order) throw new AppError('Order not found', 404, 'ORDER_NOT_FOUND');
    res.json({ data: order });
  }),
);

router.post(
  '/',
  idempotencyMiddleware,
  validate({ body: createOrderSchema }),
  asyncHandler(async (req, res) => {
    if (!getCustomer(req.body.customerId)) {
      throw new AppError('Customer not found', 404, 'CUSTOMER_NOT_FOUND');
    }
    const order = createOrder({
      ...req.body,
      createdBy: req.user!.id,
      idempotencyKey: req.idempotencyKey,
    });
    res.status(201).json({ data: order });
  }),
);

export default router;
