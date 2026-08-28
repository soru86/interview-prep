import { ExecutionContext, Injectable, Logger } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { GqlExecutionContext } from '@nestjs/graphql';

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  private readonly logger = new Logger(JwtAuthGuard.name);

  getRequest(context: ExecutionContext) {
    if (context.getType() === 'http') {
      return context.switchToHttp().getRequest();
    }
    const gqlCtx = GqlExecutionContext.create(context);
    return gqlCtx.getContext().req;
  }

  canActivate(context: ExecutionContext) {
    const req = this.getRequest(context);
    this.logger.log(
      JSON.stringify({
        layer: 'guard',
        guard: 'JwtAuthGuard',
        path: req.url ?? req.path,
      }),
    );
    return super.canActivate(context);
  }
}
