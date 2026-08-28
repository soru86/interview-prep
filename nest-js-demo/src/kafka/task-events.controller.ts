import { Controller, Logger } from '@nestjs/common';
import { EventPattern, Payload } from '@nestjs/microservices';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { TaskAudit } from './task-audit.entity';
import { TASK_CREATED_EVENT } from './kafka.constants';

export interface TaskCreatedPayload {
  taskId: string;
  title: string;
  ownerId: string;
  createdAt: string;
}

@Controller()
export class TaskEventsController {
  private readonly logger = new Logger(TaskEventsController.name);

  constructor(
    @InjectRepository(TaskAudit)
    private readonly auditRepository: Repository<TaskAudit>,
  ) {}

  @EventPattern(TASK_CREATED_EVENT)
  async handleTaskCreated(@Payload() payload: TaskCreatedPayload) {
    this.logger.log(
      JSON.stringify({
        layer: 'kafka-consumer',
        event: TASK_CREATED_EVENT,
        taskId: payload.taskId,
      }),
    );

    const audit = this.auditRepository.create({
      taskId: payload.taskId,
      eventType: TASK_CREATED_EVENT,
      payload: JSON.stringify(payload),
    });
    await this.auditRepository.save(audit);
  }
}
