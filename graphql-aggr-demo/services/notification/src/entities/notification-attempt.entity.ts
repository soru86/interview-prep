import { Column, Entity, PrimaryGeneratedColumn } from 'typeorm';

export enum NotificationStatus {
  PENDING = 'PENDING',
  SENT = 'SENT',
  FAILED = 'FAILED',
}

@Entity('notification_attempts')
export class NotificationAttemptEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ name: 'order_id' })
  orderId!: string;

  @Column({ type: 'enum', enum: NotificationStatus })
  status!: NotificationStatus;

  @Column({ name: 'attempted_at', type: 'timestamptz' })
  attemptedAt!: Date;

  @Column({ nullable: true })
  detail!: string | null;
}
