import { Controller, Get, Query } from '@nestjs/common';
import { NotificationsService } from './notifications.service';

@Controller('attempts')
export class NotificationsController {
  constructor(private readonly notifications: NotificationsService) {}

  @Get()
  findAll() {
    return this.notifications.findAll();
  }

  @Get('by-order-ids')
  byOrderIds(@Query('ids') ids?: string) {
    const orderIds = ids?.split(',').filter(Boolean) ?? [];
    return this.notifications.findByOrderIds(orderIds);
  }
}
