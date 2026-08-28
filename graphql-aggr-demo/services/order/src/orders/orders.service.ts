import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { OrderEntity } from '../entities/order.entity';
import { KafkaProducerService } from '../kafka/kafka-producer.service';

@Injectable()
export class OrdersService {
  constructor(
    @InjectRepository(OrderEntity)
    private readonly orders: Repository<OrderEntity>,
    private readonly kafka: KafkaProducerService,
  ) {}

  findAll() {
    return this.orders.find({ order: { createdAt: 'DESC' } });
  }

  async create(userId: string, productSku: string, quantity: number) {
    const order = await this.orders.save(
      this.orders.create({ userId, productSku, quantity }),
    );
    await this.kafka.emitOrderCreated({
      orderId: order.id,
      userId: order.userId,
      productSku: order.productSku,
      quantity: order.quantity,
    });
    return order;
  }
}
