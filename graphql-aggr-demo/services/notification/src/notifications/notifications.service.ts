import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { In, Repository } from 'typeorm';
import {
  NotificationAttemptEntity,
  NotificationStatus,
} from '../entities/notification-attempt.entity';

@Injectable()
export class NotificationsService {
  constructor(
    @InjectRepository(NotificationAttemptEntity)
    private readonly attempts: Repository<NotificationAttemptEntity>,
  ) {}

  findAll() {
    return this.attempts.find({ order: { attemptedAt: 'DESC' } });
  }

  findByOrderIds(orderIds: string[]) {
    if (!orderIds.length) return [];
    return this.attempts.find({ where: { orderId: In(orderIds) } });
  }

  async processOrder(orderId: string) {
    const hash = [...orderId].reduce((a, c) => a + c.charCodeAt(0), 0);
    const status =
      hash % 10 < 7
        ? NotificationStatus.SENT
        : hash % 2 === 0
          ? NotificationStatus.FAILED
          : NotificationStatus.PENDING;

    return this.attempts.save(
      this.attempts.create({
        orderId,
        status,
        attemptedAt: new Date(),
        detail:
          status === NotificationStatus.SENT
            ? 'Delivered via SMS gateway'
            : status === NotificationStatus.FAILED
              ? 'Provider timeout'
              : 'Queued for retry',
      }),
    );
  }
}
