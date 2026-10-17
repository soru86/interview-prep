# Spring Boot Microservice Test Suite Plan

Tech stack: Java 25, Spring Boot 3.5.7, Spring Data JPA, REST Controllers, Aurora PostgreSQL, Kafka (publish/subscribe), MQ (incoming subscription), S3 ingestion.

Constraints: no mocking frameworks (Mockito/PowerMock/etc.), every test exercises real Controller → Service → Repository layers against real ephemeral infrastructure, Testcontainers-managed Postgres/Kafka/LocalStack/MQ started and torn down per test suite, automatic DDL/DML setup, and a realistic path to 60%+ JaCoCo coverage.

## 1. Guiding principles

- **No test doubles of any kind.** No Mockito/PowerMock/EasyMock, no `@MockBean`. Every layer boundary (Controller → Service → Repository → DB, and out to Kafka/MQ/S3) is exercised with a real implementation talking to a real ephemeral backend.
- **One shared infrastructure lifecycle per JVM test run.** Containers start once (singleton-container pattern), the full Spring context wires against them, and each individual test resets *data* (not containers) for isolation. Full teardown happens when the JVM exits (Testcontainers' Ryuk reaper handles this automatically — no manual `stop()` needed, though we add an explicit static-block startup for clarity).
- **Schema/data setup is automatic, not manual.** Flyway (preferred over raw `schema.sql`/`data.sql`) runs DDL + master-data DML against the container on every context load — same mechanism for local dev and CI.
- **Coverage is a byproduct of layer-complete tests, not a target chased with trivial tests.** Structure the suite so business-logic-heavy classes (services, listeners, mappers) are naturally covered by the same integration tests that verify behavior; exclude generated/boilerplate code from the JaCoCo denominator so the 60% gate reflects real logic.

> Note on constraint "do not use Docker containers, instead ... start/stop in-memory test containers": Testcontainers *is* a Docker-orchestration library — it always launches real ephemeral Docker containers via the Docker daemon, it just does so fully from JUnit code instead of a static `docker-compose` file or manually-run containers. This plan treats the constraint as "no static/shared docker-compose environment — manage container lifecycle in code, scoped to the test run," which is what Testcontainers' singleton-container pattern below provides.

## 2. Postgres: Testcontainers vs. H2 — recommendation

**Recommendation: skip H2, use Testcontainers Postgres for everything, including "unit-style" repository tests.** Reasons:

- Aurora PostgreSQL exposes real Postgres semantics (JSONB, `ON CONFLICT`, window functions, sequences, specific constraint/error messages, case-sensitivity, extensions) that H2's Postgres-compatibility mode only partially emulates. A repository test that passes on H2 and fails on Aurora is worse than no test — it's false confidence.
- You already need Testcontainers for Kafka/LocalStack/MQ, so there's no "simpler setup" advantage to introducing a second DB technology just for some tests — it's actually *more* moving parts (two schema-init paths, two dialects to keep in sync).
- Testcontainers' Postgres startup is ~1–2s with a reused singleton container, so the traditional "H2 is faster" argument mostly evaporates once you stop spinning up a fresh container per test class.

So: one database technology (real Postgres via Testcontainers) across the whole suite, local and CI identical.

## 3. Dependency stack (`pom.xml`)

```xml
<properties>
    <java.version>25</java.version>
    <testcontainers.version>1.20.4</testcontainers.version>
    <awaitility.version>4.2.2</awaitility.version>
</properties>

<dependencies>
    <!-- Core Spring test support (JUnit 5 Jupiter comes transitively) -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
        <exclusions>
            <!-- Explicitly drop Mockito so nobody accidentally reaches for @MockBean -->
            <exclusion>
                <groupId>org.mockito</groupId>
                <artifactId>mockito-core</artifactId>
            </exclusion>
            <exclusion>
                <groupId>org.mockito</groupId>
                <artifactId>mockito-junit-jupiter</artifactId>
            </exclusion>
        </exclusions>
    </dependency>

    <!-- Testcontainers -->
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>testcontainers-bom</artifactId>
        <version>${testcontainers.version}</version>
        <type>pom</type>
        <scope>import</scope>
    </dependency>
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>junit-jupiter</artifactId>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>postgresql</artifactId>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>kafka</artifactId>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>localstack</artifactId>
        <scope>test</scope>
    </dependency>
    <!-- MQ: pick the module matching your actual broker (see §4.4) -->
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>mqcontainer</artifactId> <!-- if IBM MQ -->
        <scope>test</scope>
    </dependency>

    <!-- Flyway for real DDL/DML setup -->
    <dependency>
        <groupId>org.flywaydb</groupId>
        <artifactId>flyway-database-postgresql</artifactId>
    </dependency>

    <!-- Real S3 client for LocalStack interaction in tests -->
    <dependency>
        <groupId>software.amazon.awssdk</groupId>
        <artifactId>s3</artifactId>
    </dependency>

    <!-- Async assertion polling (not a mock — just a wait/poll utility) -->
    <dependency>
        <groupId>org.awaitility</groupId>
        <artifactId>awaitility</artifactId>
        <version>${awaitility.version}</version>
        <scope>test</scope>
    </dependency>

    <!-- JSON assertion ergonomics for controller tests -->
    <dependency>
        <groupId>org.assertj</groupId>
        <artifactId>assertj-core</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

> Confirm the actual MQ vendor before implementing — Testcontainers ships different modules (`mqcontainer` for IBM MQ, or a plain `GenericContainer` running `apache/activemq-artemis` / `rabbitmq` images for JMS/AMQP). Examples below assume IBM MQ-style JMS since "MQ" strongly suggests it; swap the container image if it's ActiveMQ/RabbitMQ/Solace.

## 4. Infrastructure lifecycle — singleton container base class

All integration tests extend one base class. Containers start exactly once per JVM (test run), the Spring context binds to them via `@DynamicPropertySource`, and Ryuk guarantees teardown when the JVM exits — satisfying "start for the suite, clean up after."

```java
@Testcontainers
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public abstract class AbstractIntegrationTest {

    static final PostgreSQLContainer<?> POSTGRES =
        new PostgreSQLContainer<>("postgres:16-alpine")
            .withDatabaseName("appdb").withReuse(true);

    static final KafkaContainer KAFKA =
        new KafkaContainer(DockerImageName.parse("apache/kafka:3.8.0"))
            .withReuse(true);

    static final LocalStackContainer LOCALSTACK =
        new LocalStackContainer(DockerImageName.parse("localstack/localstack:3.8"))
            .withServices(LocalStackContainer.Service.S3)
            .withReuse(true);

    static final MQContainer MQ =
        new MQContainer(DockerImageName.parse("icr.io/ibm-messaging/mq:latest"))
            .withReuse(true);

    static {
        POSTGRES.start();
        KAFKA.start();
        LOCALSTACK.start();
        MQ.start();
    }

    @DynamicPropertySource
    static void registerProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", POSTGRES::getJdbcUrl);
        registry.add("spring.datasource.username", POSTGRES::getUsername);
        registry.add("spring.datasource.password", POSTGRES::getPassword);
        registry.add("spring.flyway.url", POSTGRES::getJdbcUrl);

        registry.add("spring.kafka.bootstrap-servers", KAFKA::getBootstrapServers);

        registry.add("aws.s3.endpoint", () -> LOCALSTACK.getEndpointOverride(LocalStackContainer.Service.S3).toString());
        registry.add("aws.region", LOCALSTACK::getRegion);
        registry.add("aws.accessKey", LOCALSTACK::getAccessKey);
        registry.add("aws.secretKey", LOCALSTACK::getSecretKey);

        registry.add("mq.host", MQ::getHost);
        registry.add("mq.port", () -> MQ.getMappedPort(1414));
    }
}
```

Notes:
- `.withReuse(true)` + a `~/.testcontainers.properties` with `testcontainers.reuse.enable=true` lets containers survive across *local* test runs for fast iteration; on CI, reuse is a no-op (fresh containers every pipeline run) so behavior stays correct either way.
- No manual `stop()` calls — Testcontainers' Ryuk container watches the JVM and force-removes everything when it exits, satisfying the "clean up after the suite" requirement without you managing it.

## 5. Automatic schema + master data

Use Flyway, not ad-hoc SQL scripts, so DDL and DML are versioned and run identically in every environment:

```
src/test/resources/db/migration/
  V1__create_schema.sql        (DDL: tables, indexes, constraints)
  V2__master_data.sql          (DML: reference/lookup data required by FKs or business logic)
```

`spring.flyway.locations=classpath:db/migration` (test scope) points at this test-only path if it needs to differ from production migrations (e.g., extra seed data not wanted in prod); otherwise reuse `src/main/resources/db/migration` and layer test-only seed data in a separate `src/test/resources/db/testdata` location applied via `spring.flyway.locations=classpath:db/migration,classpath:db/testdata`. Flyway runs automatically on `ApplicationContext` startup — no code needed in tests.

**Per-test data isolation:** wrap each test in `@Transactional` where the whole flow is DB-only (repository/service tests) so Spring rolls back after each test — real DB, zero mocking, zero cross-test pollution. For tests that also touch Kafka/S3/MQ (whose side effects aren't transactional), add an explicit `@AfterEach` cleanup: truncate affected tables, delete S3 objects via the real S3 client, purge the MQ queue via a real JMS admin call.

## 6. Layer-by-layer test strategy (covers every class)

| Layer | What's tested | How (real, no mocks) |
|---|---|---|
| **Entities/Domain** | JPA mapping correctness, constraints, custom `equals/hashCode` | Exercised transitively via repository tests; add direct tests for any hand-written domain logic |
| **Repositories** | Custom `@Query` methods, pagination, uniqueness constraints, cascades | `@SpringBootTest` (not `@DataJpaTest`, which defaults to embedded DB) against the real Testcontainers Postgres, asserting actual rows |
| **Services** | Business logic, transactional boundaries, orchestration across repo/Kafka/S3/MQ | Full context test calling the service bean directly, then asserting DB state / emitted Kafka records / S3 objects |
| **REST Controllers** | Request validation, status codes, response payloads, error mapping | `TestRestTemplate`/`WebTestClient` on `RANDOM_PORT` — real HTTP round trip through the actual `DispatcherServlet`, not `@WebMvcTest` |
| **`@ControllerAdvice` / exception handlers** | Correct HTTP status + error body per exception type | Trigger the real exception through the HTTP call (e.g., request invalid payload, missing resource) and assert on the response |
| **Kafka producers** | Message published on business event, correct key/payload/headers | Real `KafkaConsumer` subscribed to the test topic reads back what the service published |
| **Kafka consumers/listeners** | Message correctly processed into DB/downstream call | Real `KafkaTemplate` publishes a test message; `Awaitility.await()` polls DB/state until the `@KafkaListener` has processed it |
| **MQ subscriber (`@JmsListener`)** | Incoming message triggers correct processing | Real `JmsTemplate`/JMS `Connection` sends a message to the test queue; await + assert resulting DB/service state |
| **S3 ingestion** | File uploaded → downstream processing (parse, persist, notify) | Real `S3Client` (AWS SDK) pointed at LocalStack `putObject`s a fixture file; await + assert ingestion outcome |
| **Mappers (MapStruct)** | Field mapping correctness | Call the real generated mapper bean directly with representative input objects |
| **Validators / DTOs** | Bean Validation constraints fire correctly | Real `Validator` bean, or through controller HTTP tests with invalid payloads |
| **Utility/helper classes** | Pure logic (formatting, calculations) | Plain JUnit 5 tests, no Spring context — fastest tests in the suite, run first |
| **Configuration classes** | Beans wire up correctly, properties bind | Covered implicitly — if the `ApplicationContext` fails to load, every test fails, which itself is the test |

## 7. Test data construction (no mocking, but no copy-pasted fixtures either)

Use the **Test Data Builder** pattern for real domain/DTO objects so tests stay readable without ever touching a mocking framework:

```java
public class OrderTestDataBuilder {
    private String customerId = "CUST-001";
    private BigDecimal amount = BigDecimal.TEN;
    // fluent with...() methods
    public Order build() { return new Order(customerId, amount, ...); }
}
```

These build real entities that get persisted through the real repository/service — never a stub standing in for a collaborator.

## 8. JaCoCo coverage plan

```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.12</version>
    <executions>
        <execution>
            <goals><goal>prepare-agent</goal></goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals><goal>report</goal></goals>
        </execution>
        <execution>
            <id>check</id>
            <phase>verify</phase>
            <goals><goal>check</goal></goals>
            <configuration>
                <rules>
                    <rule>
                        <element>BUNDLE</element>
                        <limits>
                            <limit>
                                <counter>LINE</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.60</minimum>
                            </limit>
                        </limits>
                    </rule>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

- Add `lombok.config` with `lombok.addLombokGeneratedAnnotation = true` at the project root — JaCoCo automatically excludes `@Generated`-annotated Lombok methods (getters/setters/builders) from the denominator, so you're not "paying" coverage tax for boilerplate.
- Exclude MapStruct `*Impl` generated classes, `*Application.java` main class, and pure `dto`/`config` packages via `<excludes>` in the JaCoCo config if they contain no branching logic worth covering.
- Because every test in this suite runs through Controller→Service→Repository (and Kafka/MQ/S3 where relevant), coverage accrues naturally from behavior tests — you should clear 60% comfortably by covering the service layer's business logic paths (happy path + 1–2 key error/edge paths per method) plus controller happy/validation-failure paths, without writing coverage-padding tests.

## 9. Isolation & cleanup between individual tests

| Resource | Reset strategy |
|---|---|
| Postgres | `@Transactional` + rollback for pure DB tests; explicit `TRUNCATE ... CASCADE` in `@AfterEach` for tests with non-transactional side effects |
| Kafka | Unique topic name per test class (e.g. `orders-events-${testClassName}`), or seek consumer to end before test and only assert on newly-produced records |
| S3 (LocalStack) | Real `S3Client.deleteObjects()` for the test bucket in `@AfterEach` |
| MQ | Real JMS browse+consume to purge the test queue in `@AfterEach` |

## 10. CI/CD notes

- Standard GitHub Actions/GitLab CI Linux runners ship Docker preinstalled — Testcontainers works with zero extra setup.
- Pin exact image tags (as shown above) so local and CI runs are deterministic.
- If running JUnit 5 with parallel execution, keep containers static/singleton (as in §4) so parallel test classes share one set of infrastructure rather than racing to start their own.

## 11. Suggested test source layout

```
src/test/java/.../
  support/AbstractIntegrationTest.java
  support/OrderTestDataBuilder.java
  controller/OrderControllerIT.java
  service/OrderServiceIT.java
  repository/OrderRepositoryIT.java
  messaging/kafka/OrderEventProducerIT.java
  messaging/kafka/OrderEventConsumerIT.java
  messaging/mq/IncomingSubscriptionListenerIT.java
  ingestion/S3IngestionServiceIT.java
  mapper/OrderMapperTest.java          (no Spring context needed)
  util/DateUtilsTest.java              (no Spring context needed)
src/test/resources/
  db/migration/V1__create_schema.sql
  db/migration/V2__master_data.sql
  application-test.yml
  fixtures/sample-ingest-file.csv
```

## 12. Next step

`test-fw` is currently an empty project. The suggested next step is scaffolding this into an actual runnable Maven project (`pom.xml`, the base test classes, one worked example per layer including the Kafka/MQ/S3 tests) as a working skeleton to build on.
