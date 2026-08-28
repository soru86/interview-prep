import fs from "fs";
import path from "path";
import Database from "better-sqlite3";
import bcrypt from "bcryptjs";

const root = path.join(__dirname, "..");
const dataDir = path.join(root, "data");
const dbPath = path.join(dataDir, "demo.db");

if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

if (fs.existsSync(dbPath)) {
  fs.unlinkSync(dbPath);
}

const db = new Database(dbPath);
db.pragma("journal_mode = WAL");
db.pragma("foreign_keys = ON");

const schema = fs.readFileSync(path.join(__dirname, "schema.sql"), "utf-8");
db.exec(schema);

const passwordHash = bcrypt.hashSync("password123", 10);

const insertUser = db.prepare(
  "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)"
);
insertUser.run("demo@example.com", passwordHash, "Demo User");
insertUser.run("admin@example.com", passwordHash, "Admin User");

const seed = fs.readFileSync(path.join(__dirname, "seed.sql"), "utf-8");
db.exec(seed);

const insertTask = db.prepare(
  "INSERT INTO tasks (user_id, title, completed) VALUES (?, ?, ?)"
);
const demoTasks = [
  ["Explore parallel routes", 1],
  ["Try intercepting modal", 0],
  ["Read Server Actions docs", 1],
  ["Enable React Compiler", 0],
  ["Add nested Suspense", 0],
  ["Validate forms with Zod", 1],
  ["Test JWT middleware", 0],
  ["Check unstable_cache", 0],
  ["Use useOptimistic", 0],
  ["Optimize images", 1],
] as const;

for (const [title, completed] of demoTasks) {
  insertTask.run(1, title, completed);
}

db.close();
console.log(`Database initialized at ${dbPath}`);
console.log("Demo login: demo@example.com / password123");
