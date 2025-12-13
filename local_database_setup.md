# Local Postgres Database Setup

This guide details how to set up, run, and verify the local PostgreSQL database used for `SESSION_STORAGE=local-postgres`.

## Prerequisites
- Docker & Docker Compose installed.
- Python environment set up (`uv sync`).

## 1. Start Database
Run the following command to start the Postgres container in the background:
```bash
docker-compose up -d
```

## 2. Environment Configuration
Ensure your `.env` or run command includes:
- `SESSION_STORAGE=local-postgres`
- `POSTGRES_HOST=localhost`
- `POSTGRES_PORT=5432`
- `POSTGRES_USER=user`
- `POSTGRES_PASSWORD=password`
- `POSTGRES_DB=sessions`

## 3. Run Commands

### Running the App with Local DB
```bash
SESSION_STORAGE=local-postgres \
AGENT_MODEL=gemini-2.5-flash \
uv run python pilot/main.py
```

### Running Tests
To run the integration tests that verify database connectivity:
```bash
uv run python -m pytest pilot/tests/test_memory_flow_integration.py
```

### Running Benchmark Evaluation
To run the evaluation benchmarks using the local database:
```bash
SESSION_STORAGE=local-postgres \
AGENT_MODEL=gemini-2.5-flash \
uv run python pilot/evaluation/benchmark_prompts.py
```

## 4. Troubleshooting
- **Connection Refused**: Ensure Docker container is running (`docker ps`).
- **Authentication Failed**: Verify `POSTGRES_USER` and `POSTGRES_PASSWORD` match `docker-compose.yml`.
- **Database Not Found**: Ensure `POSTGRES_DB` matches.
