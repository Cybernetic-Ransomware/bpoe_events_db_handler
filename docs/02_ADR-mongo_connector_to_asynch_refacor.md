# ADR: Migration from PyMongo to Motor for MongoDB Access

## Context
A key component of the system interacts with a MongoDB database to store and retrieve OCR-related data.
Initially, the application used PyMongo, a synchronous MongoDB client. However, the broader architecture
includes asynchronous components, such as FastAPI's lifespan management and an asyncpg-based connector to a PostgreSQL database.
This means that using a synchronous MongoDB driver like PyMongo blocks the event loop,
reducing scalability and violating the consistency of the async-first design.

The system already handles concurrency-sensitive workloads (e.g., concurrent OCR uploads or retrievals),
making it important to ensure non-blocking database operations throughout the stack.

## Decision


The project will migrate from PyMongo to Motor,
the official asynchronous MongoDB driver for Python, for all MongoDB interactions.

## Rationale
### Evaluation of Alternatives
- PyMongo: Synchronous driver, well-documented and mature. But it blocks the event loop
when used in an async context, leading to performance bottlenecks and poor scaling under load.

- Motor: Fully async-compatible driver, maintained by MongoDB, Inc. Natively supports asyncio
and integrates well with FastAPI’s dependency injection and event-driven lifecycle.

### Technical Considerations
- Event Loop Compatibility: Motor uses asyncio, ensuring non-blocking I/O.
This aligns with the application’s design philosophy and avoids blocking FastAPI’s event loop.

- Pooling: Motor uses the same underlying C driver as PyMongo (libmongoc),
supporting connection pooling out of the box.

- Consistency with Other Components: The application already includes async PostgreSQL access
via asyncpg. Using Motor brings MongoDB access in line with this model.

- Error Handling and Admin Check Logic: The migration will preserve the existing application logic, including:
    - Validation of user permissions (e.g., admin email bypass logic outside of debug mode)
    - Detailed error handling and logging during startup and request processing

- Code Simplicity and Maintainability: With Motor, dependency injection remains
straightforward, and query interfaces are similar to PyMongo, reducing migration overhead.

## Consequences
### Positive Outcomes
- Improved Scalability: Asynchronous MongoDB access avoids blocking the event loop,
increasing the app's ability to serve concurrent requests.

- Architectural Consistency: All database access (MongoDB and PostgreSQL)
now uses async interfaces.

- Cleaner Lifecycle Management: FastAPI’s lifespan can initialize and teardown
Motor connections in an async-compatible manner.

- No loss of core features: The custom admin-check logic
and error wrappers will be preserved during migration.

### Challenges & Mitigation
- Migration Effort: Requires refactoring existing sync MongoConnector
methods to async def and using await for all DB interactions.
Mitigated by 1-to-1 mapping of method names and similar API structure between PyMongo and Motor.

- Test Adaptation: Existing unit tests will need to be adapted for
async contexts using tools like pytest-asyncio.

- Learning Curve: Minor adjustment required for developers unfamiliar with Motor;
eased by similarity to PyMongo and targeted internal documentation.

## Status
_Accepted_ — this decision applies to all MongoDB-related operations within the application.
The migration will proceed incrementally, starting with the OCR-related functionality.