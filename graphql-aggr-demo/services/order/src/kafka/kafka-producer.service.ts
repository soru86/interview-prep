import { Inject, Injectable, OnModuleInit } from '@nestjs/common';
import { ClientKafka } from '@nestjs/microservices';
import { firstValueFrom } from 'rxjs';

@Injectable()
export class KafkaProducerService implements OnModuleInit {
  constructor(@Inject('KAFKA_CLIENT') private readonly client: ClientKafka) {}

  async onModuleInit(): Promise<void> {
    await this.client.connect();
  }

  emitOrderCreated(payload: {
    orderId: string;
    userId: string;
    productSku: string;
    quantity: number;
  }) {
    return firstValueFrom(this.client.emit('order.created', payload));
  }
}
