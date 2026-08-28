import { config } from 'dotenv';
import * as bcrypt from 'bcrypt';
import { DataSource } from 'typeorm';
import { User, UserRole } from '../src/users/user.entity';
import { Task, TaskStatus } from '../src/tasks/task.entity';

config();

const dataSource = new DataSource({
  type: 'better-sqlite3',
  database: process.env.DATABASE_PATH ?? './data/app.sqlite',
  entities: [User, Task],
  synchronize: true,
});

async function seed() {
  await dataSource.initialize();
  const userRepo = dataSource.getRepository(User);
  const taskRepo = dataSource.getRepository(Task);

  const passwordHash = await bcrypt.hash('password123', 10);

  const admin = userRepo.create({
    id: 'a0000000-0000-4000-8000-000000000001',
    email: 'admin@demo.local',
    passwordHash,
    role: UserRole.ADMIN,
  });
  const user = userRepo.create({
    id: 'a0000000-0000-4000-8000-000000000002',
    email: 'user@demo.local',
    passwordHash,
    role: UserRole.USER,
  });

  await userRepo.save([admin, user]);

  const tasks = [
    taskRepo.create({
      id: 'b0000000-0000-4000-8000-000000000001',
      title: 'Review NestJS docs',
      description: 'Read middleware, guards, and interceptors chapters',
      status: TaskStatus.PENDING,
      ownerId: user.id,
    }),
    taskRepo.create({
      id: 'b0000000-0000-4000-8000-000000000002',
      title: 'Configure Kafka',
      description: 'Set up docker-compose and hybrid microservice',
      status: TaskStatus.PENDING,
      ownerId: user.id,
    }),
    taskRepo.create({
      id: 'b0000000-0000-4000-8000-000000000003',
      title: 'Write unit tests',
      description: 'Add Jest sample for TasksService',
      status: TaskStatus.DONE,
      ownerId: admin.id,
    }),
  ];

  await taskRepo.save(tasks);
  await dataSource.destroy();
  console.log('Seed completed: admin@demo.local / user@demo.local (password: password123)');
}

seed().catch((err) => {
  console.error(err);
  process.exit(1);
});
