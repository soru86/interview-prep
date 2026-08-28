import { Router } from 'express';
import { authenticateLocal, authenticate } from '../middleware/auth/authenticate';
import { signAccessToken } from '../middleware/auth/tokens';
import { loginRateLimitMiddleware } from '../middleware/security/rateLimit';
import { csrfTokenIssuer } from '../middleware/security/csrf';
import { validate } from '../middleware/validation/validate';
import { asyncHandler } from '../middleware/errors/asyncHandler';
import { loginSchema } from './schemas';

const router = Router();

/** Issue CSRF token for cookie-session browser clients. */
router.get('/csrf', csrfTokenIssuer, (_req, res) => {
  res.json({ csrfToken: res.getHeader('x-csrf-token') });
});

/**
 * Passport Local login:
 * - establishes express-session cookie
 * - returns JWT for API clients
 */
router.post(
  '/login',
  loginRateLimitMiddleware,
  validate({ body: loginSchema }),
  authenticateLocal,
  asyncHandler(async (req, res) => {
    const user = req.user!;
    const accessToken = signAccessToken(user);
    res.json({
      user,
      accessToken,
      tokenType: 'Bearer',
      session: true,
    });
  }),
);

router.post(
  '/logout',
  asyncHandler(async (req, res) => {
    await new Promise<void>((resolve, reject) => {
      req.logout((err) => (err ? reject(err) : resolve()));
    });
    req.session.destroy(() => {
      res.clearCookie('connect.sid');
      res.status(204).send();
    });
  }),
);

/** Works with session cookie OR Bearer JWT via combined authenticate middleware. */
router.get(
  '/me',
  authenticate,
  asyncHandler(async (req, res) => {
    res.json({ user: req.user });
  }),
);

export default router;
