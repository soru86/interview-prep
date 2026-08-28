import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConsulRegistry } from '@graphql-aggr/service-mesh';
import { UserEntity } from './entities/user.entity';
import { HealthController } from './health.controller';
import { KafkaModule } from './kafka/kafka.module';
import { UsersController } from './users/users.controller';
import { UsersService } from './users/users.service';

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
        database: config.get('DATABASE', 'register_db'),
        entities: [UserEntity],
        synchronize: true,
      }),
    }),
    TypeOrmModule.forFeature([UserEntity]),
    KafkaModule,
  ],
  controllers: [HealthController, UsersController],
  providers: [UsersService, ConsulRegistry],
})
export class AppModule {}
