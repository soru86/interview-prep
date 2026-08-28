# Rate Limiter Demo

A Java 21 + Spring Boot microservice that returns the current GMT datetime and demonstrates five configurable rate-limiter algorithms using the **Strategy** and **Factory** patterns.

## Architecture

```
Client -> RateLimiterFilter -> RateLimiterStrategyFactory -> RateLimiterStrategy
                                      |
                                      +-> TimeController (GET /api/time)
```

- **Strategy pattern:** each algorithm implements `RateLimiterStrategy`
- **Factory pattern:** `RateLimiterStrategyFactory` selects the active strategy from configuration
- **Middleware:** `RateLimiterFilter` (`OncePerRequestFilter`) enforces limits before requests reach the controller

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/time` | Returns current datetime in GMT |
| GET | `/actuator/health` | Health check (excluded from rate limiting) |

**Success (200):**

```json
{
  "datetime": "2026-05-23T08:28:52.425555Z",
  "timezone": "GMT"
}
```

**Rate limited (429):**

```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded",
  "retryAfterSeconds": 60
}
```

Response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`.

## Rate limiter algorithms

| Type | Config keys | Description |
|------|-------------|-------------|
| `token-bucket` | `bucket-size`, `refill-rate`, `refill-interval` | Tokens refill at a fixed rate up to bucket capacity |
| `leaky-bucket` | `bucket-size`, `leak-rate`, `leak-interval` | Requests queue in a bucket and leak out at a fixed rate |
| `fixed-window` | `limit`, `window` | Count requests per fixed time window |
| `sliding-window-log` | `limit`, `window` | Store timestamps of each request; prune expired entries |
| `sliding-window-counter` | `limit`, `window`, `sub-windows` | Weighted count across current and previous sub-windows |

Switch algorithms by setting `rate-limiter.type` in `application.yml` and restarting the service.

## Configuration

```yaml
rate-limiter:
  enabled: true
  type: token-bucket          # token-bucket | leaky-bucket | fixed-window | sliding-window-log | sliding-window-counter
  key-source: client-ip       # client-ip | header:X-Api-Key
  exclude-paths:
    - /actuator/**

  token-bucket:
    bucket-size: 10
    refill-rate: 5
    refill-interval: 1s

  leaky-bucket:
    bucket-size: 10
    leak-rate: 2
    leak-interval: 1s

  fixed-window:
    limit: 100
    window: 1m

  sliding-window-log:
    limit: 100
    window: 1m

  sliding-window-counter:
    limit: 100
    window: 1m
    sub-windows: 10
```

### Additional configurable options (documented for extension)

| Setting | Purpose |
|---------|---------|
| `enabled` | Toggle rate limiting on/off |
| `key-source` | Identify clients by IP or HTTP header |
| `exclude-paths` | Skip rate limiting for health checks etc. |
| `window` / intervals | Time unit for rate definitions |
| `sub-windows` | Accuracy vs memory tradeoff for sliding window counter |
| Request cost | Some endpoints could consume more than 1 token (default: 1) |
| Storage backend | In-memory for demo; Redis for distributed deployments |
| Whitelist / blacklist | Bypass or hard-block specific keys |

## Project structure

```
src/main/java/com/interviewprep/ratelimiter/
├── RateLimiterApplication.java
├── config/          # properties, filter registration
├── controller/      # TimeController
├── filter/          # RateLimiterFilter
├── factory/         # RateLimiterStrategyFactory
├── model/           # RateLimiterType, RateLimiterDecision
├── strategy/        # five algorithm implementations
└── support/         # ClientKeyResolver
```

## Requirements

- Java 21+
- Maven 3.8+

## Build and run

```bash
cd rate-limiter-demo
mvn -q compile
mvn spring-boot:run
```

## Test

```bash
mvn test
```

## Example usage

```bash
# Allowed request
curl -i http://localhost:8080/api/time

# Exhaust token bucket (default bucket-size=10)
for i in $(seq 1 11); do
  curl -s -o /dev/null -w "Request $i: %{http_code}\n" http://localhost:8080/api/time
done

# Health check is not rate limited
curl -i http://localhost:8080/actuator/health
```

## Limitations

State is stored in-memory per JVM instance. For multi-instance deployments, replace the in-memory store with a shared backend such as Redis.
