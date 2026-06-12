# ADR: Migration from Motor to Native Async PyMongo

## Context

Following [ADR-02](02_ADR-mongo_connector_to_async_refactor.md), the project adopted Motor as its
async MongoDB driver. Motor is a thin wrapper around PyMongo maintained by MongoDB, Inc., which was
the recommended async option before `pymongo 4.13`.

Starting with `pymongo 4.13`, MongoDB, Inc. introduced a native async interface directly into the
core `pymongo` package: `pymongo.AsyncMongoClient` and the `pymongo.asynchronous.*` submodule.
This makes Motor effectively redundant — it delegates to the same underlying C driver but adds an
extra dependency and an indirection layer.

MongoDB, Inc. has signalled that Motor is in maintenance mode and that new async development
should target the native async API.

## Decision

Replace the `motor` package with the native async interface from `pymongo>=4.13`:
- `motor.motor_asyncio.AsyncIOMotorClient` → `pymongo.AsyncMongoClient`
- `motor.motor_asyncio.AsyncIOMotorDatabase` → `pymongo.asynchronous.database.AsyncDatabase`

Drop `motor` from `pyproject.toml` dependencies entirely.

## Rationale

- **One fewer dependency.** The same `pymongo` package already installed for the sync connector
  now covers the async case too. No additional install required.
- **API stability.** The native async API is developed and maintained inside the official
  `pymongo` package; Motor's future development is uncertain.
- **Nearly identical interface.** Method names, collection access syntax, and error types are the
  same between Motor and native async pymongo. Migration was mechanical (rename imports, adjust
  type annotations).
- **`uuidRepresentation` parity.** Both clients now configured with `uuidRepresentation="standard"`
  for consistent UUID handling across sync and async paths.

## Consequences

### Positive Outcomes
- Simpler dependency graph: one `pymongo` install covers sync and async operations.
- Aligns with MongoDB's stated direction for Python async support.
- No behavioral change: the async method signatures and error semantics are identical.

### Challenges & Mitigation
- **Documentation drift.** ADR-02 and the README previously referenced Motor.
  → ADR-02 marked Superseded; README updated; this ADR records the new baseline.
- **Type annotations.** `AsyncDatabase[Any]` replaces `AsyncIOMotorDatabase` in type hints;
  a `# ty: ignore[invalid-method-override]` suppression remains on `get_ocr_result` due to
  the sync/async override on the inherited `get_ocr_result` method until the class hierarchy
  is refactored.

## Status
_Accepted_ — implemented in `src/core/documentstorage/utils.py`.
`pymongo>=4.17` is the baseline; `motor` is removed from all dependency manifests.
