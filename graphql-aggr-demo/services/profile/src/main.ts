import { ValidationPipe } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { NestFactory } from '@nestjs/core';
import { NestExpressApplication } from '@nestjs/platform-express';
import { MicroserviceOptions } from '@nestjs/microservices';
import { getKafkaConfig, listenHttps } from '@graphql-aggr/service-mesh';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create<NestExpressApplication>(AppModule);
  const config = app.get(ConfigService);
  app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));
  app.enableCors({ origin: true, credentials: true });

  app.connectMicroservice<MicroserviceOptions>(
    getKafkaConfig(config, 'profile-service', config.get('KAFKA_CONSUMER_GROUP', 'profile-service-group')),
  );
  await app.startAllMicroservices();

  const port = Number(config.get('PORT', 3003));
  await listenHttps(app, port, 'profile-service');
  console.log(`profile-service listening on port ${port}`);
}

void bootstrap();
