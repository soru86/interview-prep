import { Controller } from '@nestjs/common';
import { EventPattern, Payload } from '@nestjs/microservices';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { SessionEntity } from '../entities/session.entity';

@Controller()
export class KafkaEventsController {
  constructor(
    @InjectRepository(SessionEntity)
    private readonly sessions: Repository<SessionEntity>,
  ) {}

  @EventPattern('user.logged_in')
  async onLoggedIn(@Payload() data: { userId: string; email: string }) {
    const existing = await this.sessions.find({ where: { userId: data.userId } });
    if (!existing.length) {
      await this.sessions.save(
        this.sessions.create({
          userId: data.userId,
          email: data.email,
          loggedInAt: new Date(),
          expiresAt: null,
        }),
      );
    }
  }

  @EventPattern('user.logged_out')
  async onLoggedOut(@Payload() data: { userId: string }) {
    const rows = await this.sessions.find({ where: { userId: data.userId } });
    if (rows.length) {
      await this.sessions.remove(rows);
    }
  }
}
