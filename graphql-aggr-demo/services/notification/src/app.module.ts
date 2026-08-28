import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConsulRegistry } from '@graphql-aggr/service-mesh';
import { NotificationAttemptEntity } from './entities/notification-attempt.entity';
import { HealthController } from './health.controller';
import { KafkaEventsController } from './kafka/kafka-events.controller';
import { NotificationsController } from './notifications/notifications.controller';
import { NotificationsService } from './notifications/notifications.service';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true, envFilePath: ['.env', '../../.env'] }),
    TypeOrmModule.forRootAsync({
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        type: 'postgres',
        host: config.get('POSTGRES_HOST', 'localhost'),
        port: Number(config.get('POSTGRES_PORT', 5432)),
        username: config.get('POSTGRES_USER', 'demo'),
        password: config.get('POSTGRES_PASSWORD', 'demo'),
        database: config.get('DATABASE', 'notification_db'),
        entities: [NotificationAttemptEntity],
        synchronize: true,
      }),
    }),
    TypeOrmModule.forFeature([NotificationAttemptEntity]),
  ],
  controllers: [HealthController, NotificationsController, KafkaEventsController],
  providers: [NotificationsService, ConsulRegistry],
})
export class AppModule {}
