import passport from 'passport';
import { Strategy as LocalStrategy } from 'passport-local';
import { ExtractJwt, Strategy as JwtStrategy } from 'passport-jwt';
import { env } from '../../config/env';
import {
  findUserByEmail,
  findUserById,
  toSafeUser,
  verifyPassword,
} from '../../services/userStore';

/**
 * Passport strategy registration.
 *
 * - Local: email/password for interactive login
 * - JWT: Bearer tokens for APIs / SPAs
 *
 * OAuth/SAML strategies plug into the same `passport.authenticate('strategy')` shape.
 */
passport.use(
  new LocalStrategy(
    { usernameField: 'email', passwordField: 'password', session: true },
    async (email, password, done) => {
      try {
        const user = findUserByEmail(email);
        if (!user) return done(null, false, { message: 'Invalid credentials' });
        const ok = await verifyPassword(user, password);
        if (!ok) return done(null, false, { message: 'Invalid credentials' });
        return done(null, toSafeUser(user));
      } catch (err) {
        return done(err as Error);
      }
    },
  ),
);

passport.use(
  new JwtStrategy(
    {
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      secretOrKey: env.JWT_SECRET,
    },
    (payload: { sub?: string }, done) => {
      try {
        if (!payload.sub) return done(null, false);
        const user = findUserById(payload.sub);
        if (!user) return done(null, false);
        return done(null, toSafeUser(user));
      } catch (err) {
        return done(err as Error, false);
      }
    },
  ),
);

passport.serializeUser((user, done) => {
  done(null, (user as Express.User).id);
});

passport.deserializeUser((id: string, done) => {
  const user = findUserById(id);
  if (!user) return done(null, false);
  return done(null, toSafeUser(user));
});

/** Required Passport middleware — must run after session middleware. */
export const passportInitialize = passport.initialize();

/** Restores `req.user` from the session cookie for browser flows. */
export const passportSession = passport.session();

export { passport };
