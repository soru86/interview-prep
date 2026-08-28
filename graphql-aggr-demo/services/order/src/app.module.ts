import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConsulRegistry } from '@graphql-aggr/service-mesh';
import { OrderEntity } from './entities/order.entity';
import { HealthController } from './health.controller';
import { KafkaModule } from './kafka/kafka.module';
import { OrdersController } from './orders/orders.controller';
import { OrdersService } from './orders/orders.service';

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
        database: config.get('DATABASE', 'order_db'),
        entities: [OrderEntity],
        synchronize: true,
      }),
    }),
    TypeOrmModule.forFeature([OrderEntity]),
    KafkaModule,
  ],
  controllers: [HealthController, OrdersController],
  providers: [OrdersService, ConsulRegistry],
})
export class AppModule {}
