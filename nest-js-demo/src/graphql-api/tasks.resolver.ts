import { Args, Mutation, Query, Resolver } from '@nestjs/graphql';
import { UseGuards } from '@nestjs/common';
import { TasksService } from '../tasks/tasks.service';
import { TaskModel } from './models/task.model';
import { CreateTaskInput } from './dto/create-task.input';
import { JwtAuthGuard } from '../common/guards/jwt-auth.guard';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import { User } from '../users/user.entity';

@Resolver(() => TaskModel)
@UseGuards(JwtAuthGuard)
export class TasksResolver {
  constructor(private readonly tasksService: TasksService) {}

  @Query(() => [TaskModel], { name: 'tasks' })
  findAll(@CurrentUser() user: User) {
    return this.tasksService.findAll(user);
  }

  @Mutation(() => TaskModel)
  createTask(
    @Args('input') input: CreateTaskInput,
    @CurrentUser() user: User,
  ) {
    return this.tasksService.create(input, user);
  }
}
