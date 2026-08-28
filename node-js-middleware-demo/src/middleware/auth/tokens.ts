import jwt from 'jsonwebtoken';
import { env } from '../../config/env';
import type { SafeUser } from '../../services/userStore';

export function signAccessToken(user: SafeUser): string {
  return jwt.sign(
    { email: user.email, role: user.role, name: user.name },
    env.JWT_SECRET,
    {
      subject: user.id,
      expiresIn: env.JWT_EXPIRES_IN as jwt.SignOptions['expiresIn'],
    },
  );
}
