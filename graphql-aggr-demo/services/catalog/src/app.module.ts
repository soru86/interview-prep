import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConsulRegistry } from '@graphql-aggr/service-mesh';
import { ProductEntity } from './entities/product.entity';
import { HealthController } from './health.controller';
import { KafkaEventsController } from './kafka/kafka-events.controller';
import { ProductsController } from './products/products.controller';
import { ProductsService } from './products/products.service';

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
        database: config.get('DATABASE', 'catalog_db'),
        entities: [ProductEntity],
        synchronize: true,
      }),
    }),
    TypeOrmModule.forFeature([ProductEntity]),
  ],
  controllers: [HealthController, ProductsController, KafkaEventsController],
  providers: [ProductsService, ConsulRegistry],
})
export class AppModule {}
