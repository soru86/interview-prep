import { Injectable, Logger, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { ClientKafka } from '@nestjs/microservices';
import { Inject } from '@nestjs/common';
import { Repository } from 'typeorm';
import { Task, TaskStatus } from './task.entity';
import { CreateTaskDto } from './dto/create-task.dto';
import { UpdateTaskDto } from './dto/update-task.dto';
import { User, UserRole } from '../users/user.entity';
import {
  KAFKA_CLIENT,
  TASK_CREATED_EVENT,
} from '../kafka/kafka.constants';
import { TaskCreatedPayload } from '../kafka/task-events.controller';

@Injectable()
export class TasksService {
  private readonly logger = new Logger(TasksService.name);

  constructor(
    @InjectRepository(Task)
    private readonly tasksRepository: Repository<Task>,
    @Inject(KAFKA_CLIENT)
    private readonly kafkaClient: ClientKafka,
  ) {}

  async onModuleInit() {
    await this.kafkaClient.connect();
  }

  findAll(user: User): Promise<Task[]> {
    if (user.role === UserRole.ADMIN) {
      return this.tasksRepository.find({ order: { createdAt: 'DESC' } });
    }
    return this.tasksRepository.find({
      where: { ownerId: user.id },
      order: { createdAt: 'DESC' },
    });
  }

  async findOne(id: string, user: User): Promise<Task> {
    const task = await this.tasksRepository.findOne({ where: { id } });
    if (!task) {
      throw new NotFoundException(`Task ${id} not found`);
    }
    if (user.role !== UserRole.ADMIN && task.ownerId !== user.id) {
      throw new NotFoundException(`Task ${id} not found`);
    }
    return task;
  }

  async create(dto: CreateTaskDto, user: User): Promise<Task> {
    const task = this.tasksRepository.create({
      ...dto,
      ownerId: user.id,
      status: dto.status ?? TaskStatus.PENDING,
    });
    const saved = await this.tasksRepository.save(task);

    const payload: TaskCreatedPayload = {
      taskId: saved.id,
      title: saved.title,
      ownerId: saved.ownerId,
      createdAt: saved.createdAt.toISOString(),
    };

    this.kafkaClient.emit(TASK_CREATED_EVENT, payload);
    this.logger.log(
      JSON.stringify({ layer: 'service', event: 'emitted', payload }),
    );

    return saved;
  }

  async update(id: string, dto: UpdateTaskDto, user: User): Promise<Task> {
    const task = await this.findOne(id, user);
    Object.assign(task, dto);
    return this.tasksRepository.save(task);
  }

  async remove(id: string, user: User): Promise<void> {
    const task = await this.findOne(id, user);
    await this.tasksRepository.remove(task);
  }
}
