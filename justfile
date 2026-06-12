# bpoe-events-db-handler — task runner
# Install: scoop install just  |  winget install Casey.Just

set shell := ["pwsh", "-Command"]

# Run pre-commit on staged files, then open Commitizen
# Stage your changes first: git add <files>
commit:
    uv run pre-commit run
    uv run cz commit

# Bump version on release (auto-tags vX.Y.Z, updates pyproject.toml + uv.lock)
bump:
    uv run cz bump --no-verify
    uv lock
    $v = (uv run cz version --project); git tag -d "v$v" && git add uv.lock && git commit --amend --no-edit && git tag "v$v"

# Auto-format source files
format:
    uv run ruff format src/

# Run the full linting suite
lint:
    uv run ruff check --fix src/
    uv run ty check src/
    uv run python -m codespell_lib src/
    uv run bandit -r src/ -c pyproject.toml -q

# Run unit tests (excludes integration)
test:
    uv run pytest -m "not integration"

# Run integration tests (requires Docker — starts real Postgres and MongoDB via testcontainers)
test-integration:
    uv run pytest -m integration

# Run all tests including integration
test-all:
    uv run pytest

# Start full Docker stack (app + postgres + mongodb) with rebuild
up:
    docker-compose -f docker/docker-compose.yml up --build -d

# Stop and remove Docker stack containers
down:
    docker-compose -f docker/docker-compose.yml down

# Stream Docker app logs
logs:
    docker-compose -f docker/docker-compose.yml logs -f app
