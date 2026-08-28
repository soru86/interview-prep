# GraphQL Microservices Aggregation Demo

NestJS microservices + Kafka + Consul + mTLS + GraphQL API gateway + Expo mobile dashboard.

## Quick start

```bash
cp .env.example .env
npm install
npm run certs:generate
npm run docker:up
# wait ~30s for postgres/kafka/consul
npm run build:mesh
npm run dev
# in another terminal (after services are up ~20s):
npm run seed
cd mobile && npm install && npx expo start
```

## Ports

| Service | Port |
|---------|------|
| register | 3001 |
| login | 3002 |
| profile | 3003 |
| order | 3004 |
| notification | 3005 |
| catalog | 3006 |
| api-gateway (GraphQL) | 4000 |
| Consul UI | 8500 |
| Kafka UI | 8080 |

## GraphQL aggregation

One query fans out to order, notification, catalog, login, and profile services:

```graphql
query {
  dashboard {
    orderInsights {
      orderId
      productName
      notificationStatus
      inventoryRemaining
    }
    activeUsers {
      email
      loggedInAt
      dateOfBirth
    }
  }
}
```

Headers: `Authorization: Bearer <access_token>` from `POST https://localhost:3002/auth/login`

Playground: `https://localhost:4000/graphql` (accept self-signed cert in browser)

## Demo credentials

- `alice@demo.com` / `password123`
- `bob@demo.com` / `password123`

## Security features

- **Refresh tokens**: `POST /auth/refresh` with rotation
- **Consul**: services self-register; gateway resolves URLs dynamically
- **mTLS**: service-to-service HTTPS with client certs (`MTLS_ENABLED=false` to disable)

## Mobile

Set `EXPO_PUBLIC_GATEWAY_URL=https://<your-lan-ip>:4000/graphql` in `mobile/.env`
