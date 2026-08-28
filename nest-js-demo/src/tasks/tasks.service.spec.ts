import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';
import { ClientKafka } from '@nestjs/microservices';
import { Repository } from 'typeorm';
import { TasksService } from './tasks.service';
import { Task, TaskStatus } from './task.entity';
import { User, UserRole } from '../users/user.entity';
import { KAFKA_CLIENT, TASK_CREATED_EVENT } from '../kafka/kafka.constants';

describe('TasksService', () => {
  let service: TasksService;
  let tasksRepository: jest.Mocked<Repository<Task>>;
  let kafkaClient: jest.Mocked<ClientKafka>;

  const user: User = {
    id: 'user-id',
    email: 'user@demo.local',
    passwordHash: 'hash',
    role: UserRole.USER,
    createdAt: new Date(),
    tasks: [],
  };

  beforeEach(async () => {
    tasksRepository = {
      create: jest.fn(),
      save: jest.fn(),
      find: jest.fn(),
      findOne: jest.fn(),
      remove: jest.fn(),
    } as unknown as jest.Mocked<Repository<Task>>;

    kafkaClient = {
      connect: jest.fn().mockResolvedValue(undefined),
      emit: jest.fn(),
    } as unknown as jest.Mocked<ClientKafka>;

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        TasksService,
        { provide: getRepositoryToken(Task), useValue: tasksRepository },
        { provide: KAFKA_CLIENT, useValue: kafkaClient },
      ],
    }).compile();

    service = module.get<TasksService>(TasksService);
  });

  it('creates a task and emits Kafka event', async () => {
    const dto = { title: 'Test task', description: 'Desc' };
    const created = {
      id: 'task-id',
      title: dto.title,
      description: dto.description,
      status: TaskStatus.PENDING,
      ownerId: user.id,
      createdAt: new Date(),
      updatedAt: new Date(),
    } as Task;

    tasksRepository.create.mockReturnValue(created);
    tasksRepository.save.mockResolvedValue(created);

    const result = await service.create(dto, user);

    expect(tasksRepository.create).toHaveBeenCalledWith({
      ...dto,
      ownerId: user.id,
      status: TaskStatus.PENDING,
    });
    expect(tasksRepository.save).toHaveBeenCalledWith(created);
    expect(kafkaClient.emit).toHaveBeenCalledWith(
      TASK_CREATED_EVENT,
      expect.objectContaining({
        taskId: created.id,
        title: created.title,
        ownerId: user.id,
      }),
    );
    expect(result).toEqual(created);
  });
});
