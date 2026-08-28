import { Field, ID, ObjectType, registerEnumType } from '@nestjs/graphql';
import { TaskStatus } from '../../tasks/task.entity';

registerEnumType(TaskStatus, { name: 'TaskStatus' });

@ObjectType()
export class TaskModel {
  @Field(() => ID)
  id: string;

  @Field()
  title: string;

  @Field({ nullable: true })
  description?: string;

  @Field(() => TaskStatus)
  status: TaskStatus;

  @Field()
  ownerId: string;

  @Field()
  createdAt: Date;

  @Field()
  updatedAt: Date;
}
