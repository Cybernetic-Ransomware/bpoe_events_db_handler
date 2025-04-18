# Event's database handlers for BPOE app
This repository contains an asynchronous connection pool for handling main db.

## Overview
The purpose of this project is to build a handler for main db.

## Features
- robust Postgres17 database foundation,
- extended timeline handling by TimescaleDB,
- multiple connector asynch pool handler,
- accessible only via a gateway connection.

## Requirements
- Python >=3.12.10 with UV package manager
- Docker Desktop / Docker + Compose

## Getting Started (Windows)
### Deploy
1. Clone the repository:
      ```powershell
      git clone https://github.com/Cybernetic-Ransomware/bpoe-events_db_handler.git
      ```
2. Set .env file based on the template.
3. Run using Docker:
      ```powershell
      docker-compose -f .\docker\docker-compose.yml up --build -d
      ```
### Dev-instance
1. Clone the repository:
      ```powershell
      git clone https://github.com/Cybernetic-Ransomware/bpoe-events_db_handler.git
      ```
2. Set .env file based on the template.
3. Create an instance of Postgres >=17.4 with installed timescaledb extension,
4. Provide access to a database instance with users that match the [.env.template](docker/.env.template) file.
5. Install UV:
      ```powershell
      pip install uv
      ```
6. Install dependencies:
      ```powershell
      uv sync
      ```
7. Install pre-commit hooks:
      ```powershell
      uv run pre-commit install
      uv run pre-commit autoupdate
      uv run pre-commit run --all-files
      ```
8Run the application locally:
      ```powershell
      uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
      ```

## Testing
#### Postman
- The repository will include a Postman collection with ready-to-import webhook mockers

#### Pytest
```powershell
uv sync --extra dev
uv run pytest
```

#### Ruff
```powershell
uv sync --extra dev
uv run ruff check
```
or as a standalone tool:
```powershell
uvx ruff check
```

#### Mypy
```powershell
uv sync --extra dev
uv run mypy .\src\
```
or as a standalone tool:
```powershell
uvx mypy .\src\
```

#### Database Access:
Connect to the Postgres Instance via pgAdmin.

## Useful links and documentation
- Install TimescaleDB on Windows: [TimescaleDB](https://docs.timescale.com/self-hosted/latest/install/installation-windows/)
