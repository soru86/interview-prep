import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { TypeOrmModule } from '@nestjs/typeorm';
import { TaskAudit } from './task-audit.entity';
import { TaskEventsController } from './task-events.controller';
import { KAFKA_CLIENT } from './kafka.constants';

@Module({
  imports: [
    TypeOrmModule.forFeature([TaskAudit]),
    ClientsModule.registerAsync([
      {
        name: KAFKA_CLIENT,
        imports: [ConfigModule],
        inject: [ConfigService],
        useFactory: (config: ConfigService) => ({
          transport: Transport.KAFKA,
          options: {
            client: {
              clientId: config.get('KAFKA_CLIENT_ID', 'task-api'),
              brokers: config
                .get('KAFKA_BROKERS', 'localhost:9092')
                .split(','),
            },
            consumer: {
              groupId: config.get('KAFKA_CONSUMER_GROUP', 'task-consumer'),
            },
          },
        }),
      },
    ]),
  ],
  controllers: [TaskEventsController],
  exports: [ClientsModule],
})
export class KafkaModule {}
