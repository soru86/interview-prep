import { Field, ID, ObjectType, registerEnumType } from '@nestjs/graphql';

export enum NotificationStatusGql {
  PENDING = 'PENDING',
  SENT = 'SENT',
  FAILED = 'FAILED',
}

registerEnumType(NotificationStatusGql, { name: 'NotificationStatus' });

@ObjectType()
export class OrderInsight {
  @Field(() => ID)
  orderId!: string;

  @Field()
  productSku!: string;

  @Field()
  productName!: string;

  @Field()
  quantity!: number;

  @Field(() => NotificationStatusGql)
  notificationStatus!: NotificationStatusGql;

  @Field({ nullable: true })
  notificationDetail?: string | null;

  @Field()
  inventoryRemaining!: number;
}

@ObjectType()
export class ActiveUser {
  @Field(() => ID)
  userId!: string;

  @Field()
  email!: string;

  @Field()
  loggedInAt!: string;

  @Field({ nullable: true })
  dateOfBirth?: string | null;
}

@ObjectType()
export class Dashboard {
  @Field(() => [OrderInsight])
  orderInsights!: OrderInsight[];

  @Field(() => [ActiveUser])
  activeUsers!: ActiveUser[];
}
