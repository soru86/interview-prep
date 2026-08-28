import { createParamDecorator, ExecutionContext } from '@nestjs/common';
import { GqlExecutionContext } from '@nestjs/graphql';
import { User } from '../../users/user.entity';

export const CurrentUser = createParamDecorator(
  (_data: unknown, ctx: ExecutionContext): User => {
    if (ctx.getType() === 'http') {
      return ctx.switchToHttp().getRequest().user as User;
    }
    const gqlCtx = GqlExecutionContext.create(ctx);
    return gqlCtx.getContext().req.user as User;
  },
);
