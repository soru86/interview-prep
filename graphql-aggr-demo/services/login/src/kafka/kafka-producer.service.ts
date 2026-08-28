import { Inject, Injectable, OnModuleInit } from '@nestjs/common';
import { ClientKafka } from '@nestjs/microservices';
import { firstValueFrom } from 'rxjs';

@Injectable()
export class KafkaProducerService implements OnModuleInit {
  constructor(@Inject('KAFKA_CLIENT') private readonly client: ClientKafka) {}

  async onModuleInit(): Promise<void> {
    await this.client.connect();
  }

  emitLoggedIn(payload: { userId: string; email: string }) {
    return firstValueFrom(this.client.emit('user.logged_in', payload));
  }

  emitLoggedOut(payload: { userId: string; email: string }) {
    return firstValueFrom(this.client.emit('user.logged_out', payload));
  }
}
