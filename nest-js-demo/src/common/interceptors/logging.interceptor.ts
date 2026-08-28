import {
  CallHandler,
  ExecutionContext,
  Injectable,
  Logger,
  NestInterceptor,
} from '@nestjs/common';
import { Observable, tap } from 'rxjs';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger(LoggingInterceptor.name);

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const req = context.switchToHttp().getRequest<{
      method: string;
      url: string;
      headers: Record<string, string>;
    }>();
    const requestId = req.headers['x-request-id'] ?? 'unknown';
    const started = Date.now();

    this.logger.log(
      JSON.stringify({
        layer: 'interceptor',
        phase: 'pre',
        requestId,
        handler: context.getHandler().name,
      }),
    );

    return next.handle().pipe(
      tap(() => {
        this.logger.log(
          JSON.stringify({
            layer: 'interceptor',
            phase: 'post',
            requestId,
            handler: context.getHandler().name,
            durationMs: Date.now() - started,
          }),
        );
      }),
    );
  }
}
