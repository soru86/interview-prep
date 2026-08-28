import { ConsoleLogger, ValidationPipe } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { NestFactory } from '@nestjs/core';
import { MicroserviceOptions } from '@nestjs/microservices';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import helmet from 'helmet';
import { AppModule } from './app.module';
import { AllExceptionsFilter } from './common/filters/all-exceptions.filter';
import { LoggingInterceptor } from './common/interceptors/logging.interceptor';
import { getKafkaConfig } from './kafka/kafka.config';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    logger: new ConsoleLogger({
      json: true,
      colors: process.env.NODE_ENV !== 'production',
    }),
  });

  const configService = app.get(ConfigService);

  // CSP disabled so Swagger UI static assets/scripts load at /docs
  app.use(helmet({ contentSecurityPolicy: false }));
  app.enableCors({
    origin: `${configService.get('CORS_ORIGIN', true)}`,
    credentials: true,
  });

  app.setGlobalPrefix('api');

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }),
  );
  app.useGlobalInterceptors(new LoggingInterceptor());
  app.useGlobalFilters(new AllExceptionsFilter());

  const swaggerConfig = new DocumentBuilder()
    .setTitle('NestJS Demo API')
    .setDescription(
      'Task management demo showcasing NestJS 11 features: middleware, guards, interceptors, pipes, filters, JWT, Kafka, GraphQL, and Swagger.',
    )
    .setVersion('1.0')
    .addBearerAuth()
    .build();
  const document = SwaggerModule.createDocument(app, swaggerConfig);
  SwaggerModule.setup('docs', app, document);

  app.connectMicroservice<MicroserviceOptions>(getKafkaConfig(configService));
  await app.startAllMicroservices();

  const port = configService.get<number>('PORT', 3000);
  await app.listen(port);

  const logger = new ConsoleLogger('Bootstrap', {
    json: true,
    colors: process.env.NODE_ENV !== 'production',
  });
  logger.log(
    JSON.stringify({
      message: 'Application started',
      port,
      swagger: `http://localhost:${port}/docs`,
      graphql: `http://localhost:${port}/graphql`,
    }),
  );
}

void bootstrap();
