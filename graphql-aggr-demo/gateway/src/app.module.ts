import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { HttpModule } from '@nestjs/axios';
import { ConsulRegistry } from '@graphql-aggr/service-mesh';
import { AuthModule } from './auth/auth.module';
import { GraphqlModule } from './graphql/graphql.module';
import { HealthController } from './health.controller';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true, envFilePath: ['.env', '../.env'] }),
    HttpModule,
    AuthModule,
    GraphqlModule,
  ],
  controllers: [HealthController],
  providers: [ConsulRegistry],
})
export class AppModule {}
