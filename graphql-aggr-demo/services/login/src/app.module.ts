import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { JwtModule } from '@nestjs/jwt';
import { TypeOrmModule } from '@nestjs/typeorm';
import { HttpModule } from '@nestjs/axios';
import { ConsulRegistry } from '@graphql-aggr/service-mesh';
import { RefreshTokenEntity } from './entities/refresh-token.entity';
import { SessionEntity } from './entities/session.entity';
import { AuthController, SessionsController } from './auth/auth.controller';
import { AuthService } from './auth/auth.service';
import { HealthController } from './health.controller';
import { KafkaModule } from './kafka/kafka.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true, envFilePath: ['.env', '../../.env'] }),
    HttpModule,
    JwtModule.register({}),
    TypeOrmModule.forRootAsync({
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        type: 'postgres',
        host: config.get('POSTGRES_HOST', 'localhost'),
        port: Number(config.get('POSTGRES_PORT', 5432)),
        username: config.get('POSTGRES_USER', 'demo'),
        password: config.get('POSTGRES_PASSWORD', 'demo'),
        database: config.get('DATABASE', 'login_db'),
        entities: [SessionEntity, RefreshTokenEntity],
        synchronize: true,
      }),
    }),
    TypeOrmModule.forFeature([SessionEntity, RefreshTokenEntity]),
    KafkaModule,
  ],
  controllers: [HealthController, AuthController, SessionsController],
  providers: [AuthService, ConsulRegistry],
})
export class AppModule {}
