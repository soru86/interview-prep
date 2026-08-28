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
    getKafkaConfig(
      config,
      'notification-service',
      config.get('KAFKA_CONSUMER_GROUP', 'notification-service-group'),
    ),
  );
  await app.startAllMicroservices();

  const port = Number(config.get('PORT', 3005));
  await listenHttps(app, port, 'notification-service');
  console.log(`notification-service listening on port ${port}`);
}

void bootstrap();
