import * as https from 'https';
import axios from 'axios';

const agent = new https.Agent({ rejectUnauthorized: false });

const httpsPost = async (url: string, body: unknown) => {
  const { data } = await axios.post(url, body, { httpsAgent: agent });
  return data;
};

const httpsPatch = async (url: string, body: unknown) => {
  const { data } = await axios.patch(url, body, { httpsAgent: agent });
  return data;
};

const users = [
  { email: 'alice@demo.com', password: 'password123', dob: '1990-04-12' },
  { email: 'bob@demo.com', password: 'password123', dob: '1985-09-23' },
  { email: 'carol@demo.com', password: 'password123', dob: '1992-01-30' },
  { email: 'dave@demo.com', password: 'password123', dob: '1988-11-05' },
  { email: 'eve@demo.com', password: 'password123', dob: '1995-07-18' },
];

const products = [
  { sku: 'SKU-001', name: 'Wireless Headphones', inventory: 25 },
  { sku: 'SKU-002', name: 'Smart Watch', inventory: 18 },
  { sku: 'SKU-003', name: 'USB-C Hub', inventory: 40 },
  { sku: 'SKU-004', name: 'Mechanical Keyboard', inventory: 12 },
  { sku: 'SKU-005', name: '4K Monitor', inventory: 8 },
];

async function main() {
  const registerBase = 'https://localhost:3001';
  const loginBase = 'https://localhost:3002';
  const profileBase = 'https://localhost:3003';
  const orderBase = 'https://localhost:3004';
  const catalogBase = 'https://localhost:3006';

  console.log('Seeding catalog products...');
  for (const p of products) {
    await httpsPost(`${catalogBase}/products/seed`, {
      sku: p.sku,
      name: p.name,
      inventoryCount: p.inventory,
    });
  }

  const userIds: string[] = [];

  console.log('Registering users...');
  for (const u of users) {
    const created = await httpsPost(`${registerBase}/users`, {
      email: u.email,
      password: u.password,
    });
    userIds.push(created.id);
    await new Promise((r) => setTimeout(r, 500));
    await httpsPatch(`${profileBase}/profiles/${created.id}`, {
      dateOfBirth: u.dob,
    });
  }

  console.log('Logging in active users (alice, bob)...');
  for (const email of ['alice@demo.com', 'bob@demo.com']) {
    await httpsPost(`${loginBase}/auth/login`, {
      email,
      password: 'password123',
    });
  }

  console.log('Creating orders...');
  const orders = [
    { userId: userIds[0], productSku: 'SKU-001', quantity: 1 },
    { userId: userIds[0], productSku: 'SKU-002', quantity: 2 },
    { userId: userIds[1], productSku: 'SKU-003', quantity: 1 },
    { userId: userIds[2], productSku: 'SKU-004', quantity: 1 },
    { userId: userIds[3], productSku: 'SKU-005', quantity: 1 },
    { userId: userIds[4], productSku: 'SKU-001', quantity: 3 },
  ];

  for (const o of orders) {
    await httpsPost(`${orderBase}/orders`, o);
    await new Promise((r) => setTimeout(r, 800));
  }

  console.log('Seed complete. Wait a few seconds for Kafka consumers, then open the dashboard.');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
