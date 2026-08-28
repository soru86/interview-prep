import { Body, Controller, Post, UseGuards } from '@nestjs/common';
import { IsEmail, IsString, MinLength } from 'class-validator';
import { MtlsInternalGuard } from '@graphql-aggr/service-mesh';
import { UsersService } from './users.service';
import { KafkaProducerService } from '../kafka/kafka-producer.service';

class RegisterDto {
  @IsEmail()
  email!: string;

  @IsString()
  @MinLength(6)
  password!: string;
}

class VerifyDto {
  @IsEmail()
  email!: string;

  @IsString()
  password!: string;
}

@Controller()
export class UsersController {
  constructor(
    private readonly usersService: UsersService,
    private readonly kafka: KafkaProducerService,
  ) {}

  @Post(['users', 'auth/register'])
  async register(@Body() dto: RegisterDto) {
    const user = await this.usersService.register(dto.email, dto.password);
    await this.kafka.emitUserRegistered({ userId: user.id, email: user.email });
    return { id: user.id, email: user.email, createdAt: user.createdAt };
  }

  @Post('internal/users/verify')
  @UseGuards(MtlsInternalGuard)
  async verify(@Body() dto: VerifyDto) {
    const user = await this.usersService.verify(dto.email, dto.password);
    return { id: user.id, email: user.email };
  }
}
