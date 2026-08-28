import { ConfigService } from '@nestjs/config';
import { Transport } from '@nestjs/microservices';
import { KafkaOptions } from '@nestjs/microservices/interfaces/microservice-configuration.interface';

export const getKafkaConfig = (
  configService: ConfigService,
  clientId: string,
  groupId: string,
): KafkaOptions => ({
  transport: Transport.KAFKA,
  options: {
    client: {
      clientId,
      brokers: configService.get('KAFKA_BROKERS', 'localhost:9092').split(','),
    },
    consumer: {
      groupId,
    },
  },
});
