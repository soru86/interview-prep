import type { Role, SafeUser } from '../services/userStore';

declare global {
  namespace Express {
    interface User extends SafeUser {}

    interface Request {
      requestId?: string;
      rawBodyPreview?: string;
      csrfToken?: () => string;
      idempotencyKey?: string;
      id?: string;
    }
  }
}

export {};

declare module 'express-session' {
  interface SessionData {
    passport?: { user?: string };
    csrfSecret?: string;
  }
}

export type AuthenticatedUser = SafeUser & { role: Role };
