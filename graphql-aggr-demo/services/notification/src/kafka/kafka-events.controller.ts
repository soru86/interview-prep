import { Controller } from '@nestjs/common';
import { EventPattern, Payload } from '@nestjs/microservices';
import { NotificationsService } from '../notifications/notifications.service';

@Controller()
export class KafkaEventsController {
  constructor(private readonly notifications: NotificationsService) {}

  @EventPattern('order.created')
  async onOrderCreated(@Payload() data: { orderId: string }) {
    await this.notifications.processOrder(data.orderId);
  }
}
