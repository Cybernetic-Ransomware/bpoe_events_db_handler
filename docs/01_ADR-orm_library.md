# ADR: Selection of asyncpg over SQLAlchemy for Transactional Database Access

## Context
The application architecture requires efficient and scalable access to a central relational database
that will serve as the core of transactional operations. Given the need for high performance and
the planned use of PostgreSQL extensions such as TimescaleDB and PostGIS,
a solution was required that offers flexibility in query composition and supports asynchronous connection pooling.

Two approaches were implemented and evaluated:
- A direct connector using asyncpg
- An SQLAlchemy-based approach (with async support)

The goal was to determine which option better meets the architecture's performance and extensibility requirements.

## Decision
The project will use `asyncpg` directly as the connector for the main transactional PostgreSQL database.

## Rationale
### Evaluation of Alternatives
- asyncpg: offers native async support and fine-grained control over connection pooling.
Queries can be expressed in raw SQL, enabling full flexibility when using PostgreSQL-specific
features, including TimescaleDB’s hypertables and PostGIS’s spatial queries.

- SQLAlchemy (async): Provides ORM abstraction and a query-building interface.
However, its async support introduces more complexity, showed lower performance during testing,
and restricts flexibility in leveraging advanced PostgreSQL extensions.

The asyncpg implementation provided better control, lower latency,
and less abstraction overhead — all of which align better with the architectural goals.

### Technical Considerations
- Performance: asyncpg is highly optimized for PostgreSQL and
better suited to high-throughput scenarios due to its low overhead.

- Asynchronous Pooling: Built-in pooling in asyncpg
ensures efficient resource usage without external tools.

- Extension Support: Direct access to SQL allows easier
integration with PostgreSQL extensions like TimescaleDB and PostGIS,
which often require raw queries or custom connection settings.

### Integration with Existing Environment
The use of asyncpg aligns with the system’s asynchronous design.
While it requires manual query composition, this approach matches
the team’s familiarity and avoids unnecessary ORM overhead. No major changes to tooling are required.

### Future Potential


This decision provides a solid foundation for advanced PostgreSQL features and performance tuning.
It keeps the architecture lightweight and adaptable, while still leaving room
for introducing higher-level abstractions if needed in specific areas.

## Consequences
### Positive Outcomes
- Increased performance due to minimal abstraction
- Full control over SQL, supporting advanced PostgreSQL features
- Natural integration into the async application stack
- Simplified dependency and tooling setup

### Challenges & Mitigation
- Manual Query Handling: Increases the need for internal consistency and query hygiene; mitigated through shared query utilities and review practices.
- No ORM Abstractions: May result in more repetitive code; helper functions will be developed for common operations.
- Learning Curve for Raw SQL: Internal documentation and onboarding support will help new contributors adapt quickly.

## Status
_Accepted_ — this decision applies project-wide to all transactional PostgreSQL database interactions.