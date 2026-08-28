import { Router } from 'express';
import { asyncHandler } from '../middleware/errors/asyncHandler';
import { AppError } from '../utils/AppError';
import { z } from 'zod';

const router = Router();

router.get(
  '/app-error',
  asyncHandler(async () => {
    throw new AppError('Demonstrating operational AppError', 400, 'DEMO_APP_ERROR');
  }),
);

router.get(
  '/unhandled',
  asyncHandler(async () => {
    throw new Error('Demonstrating unexpected failure');
  }),
);

router.post(
  '/validation',
  asyncHandler(async (req) => {
    z.object({ mustBeEmail: z.string().email() }).parse(req.body);
  }),
);

router.get(
  '/timeout',
  asyncHandler(async (_req, res) => {
    await new Promise((r) => setTimeout(r, 60_000));
    res.json({ ok: true });
  }),
);

export default router;
