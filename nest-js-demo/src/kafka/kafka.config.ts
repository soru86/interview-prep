import { ConfigService } from '@nestjs/config';
import { Transport } from '@nestjs/microservices';
import { KafkaOptions } from '@nestjs/microservices/interfaces/microservice-configuration.interface';

export const getKafkaConfig = (
  configService: ConfigService,
): KafkaOptions => ({
  transport: Transport.KAFKA,
  options: {
    client: {
      clientId: configService.get('KAFKA_CLIENT_ID', 'task-api'),
      brokers: configService
        .get('KAFKA_BROKERS', 'localhost:9092')
        .split(','),
    },
    consumer: {
      groupId: configService.get('KAFKA_CONSUMER_GROUP', 'task-consumer'),
    },
  },
});
