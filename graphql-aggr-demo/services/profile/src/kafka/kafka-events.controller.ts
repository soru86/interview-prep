import { Controller } from '@nestjs/common';
import { EventPattern, Payload } from '@nestjs/microservices';
import { ProfilesService } from '../profiles/profiles.service';

@Controller()
export class KafkaEventsController {
  constructor(private readonly profiles: ProfilesService) {}

  @EventPattern('user.registered')
  async onUserRegistered(@Payload() data: { userId: string; email: string }) {
    await this.profiles.createFromRegistration(data.userId, data.email);
  }
}
