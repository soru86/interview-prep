import bcrypt from 'bcryptjs';

export type Role = 'admin' | 'user' | 'service';

export interface UserRecord {
  id: string;
  email: string;
  passwordHash: string;
  name: string;
  role: Role;
}

export type SafeUser = Omit<UserRecord, 'passwordHash'>;

const users = new Map<string, UserRecord>();

function seed(): void {
  const seedUsers: Array<Omit<UserRecord, 'passwordHash'> & { password: string }> = [
    {
      id: 'u-admin',
      email: 'admin@demo.local',
      password: 'password123',
      name: 'Ada Admin',
      role: 'admin',
    },
    {
      id: 'u-user',
      email: 'user@demo.local',
      password: 'password123',
      name: 'Uma User',
      role: 'user',
    },
  ];

  for (const u of seedUsers) {
    users.set(u.id, {
      id: u.id,
      email: u.email,
      name: u.name,
      role: u.role,
      passwordHash: bcrypt.hashSync(u.password, 10),
    });
  }
}

seed();

export function toSafeUser(user: UserRecord): SafeUser {
  return { id: user.id, email: user.email, name: user.name, role: user.role };
}

export function findUserById(id: string): UserRecord | undefined {
  return users.get(id);
}

export function findUserByEmail(email: string): UserRecord | undefined {
  return [...users.values()].find((u) => u.email.toLowerCase() === email.toLowerCase());
}

export async function verifyPassword(user: UserRecord, password: string): Promise<boolean> {
  return bcrypt.compare(password, user.passwordHash);
}
