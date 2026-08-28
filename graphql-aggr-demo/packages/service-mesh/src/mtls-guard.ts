import {
  CanActivate,
  ExecutionContext,
  Injectable,
  UnauthorizedException,
} from '@nestjs/common';
import { Request } from 'express';
import { isMtlsEnabled } from './mtls';

const ALLOWED_CLIENTS = new Set([
  'api-gateway',
  'gateway-client',
  'login-service',
  'register-service',
  'profile-service',
  'order-service',
  'notification-service',
  'catalog-service',
]);

@Injectable()
export class MtlsInternalGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    if (!isMtlsEnabled()) {
      return true;
    }

    const req = context.switchToHttp().getRequest<Request>();
    const socket = req.socket as { authorized?: boolean; getPeerCertificate?: () => { subject?: { CN?: string } } };
    if (!socket.authorized) {
      throw new UnauthorizedException('Client certificate required');
    }

    const peer = socket.getPeerCertificate?.();
    const cn = peer?.subject?.CN;
    if (!cn || !ALLOWED_CLIENTS.has(cn)) {
      throw new UnauthorizedException('Unauthorized client certificate');
    }
    return true;
  }
}
