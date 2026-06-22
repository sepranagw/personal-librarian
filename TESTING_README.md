# How to run unit tests

## 1. Ensure dependencies are installed
The testing dependencies (pytest and pytest-cov) are already specified in `pyproject.toml` and `requirements-dev.txt`.

```bash
pip install -e ".[dev]"
```

## 2. Run tests with coverage
```bash
pytest --cov=src/personal_librarian --cov-report=term-missing
```

## 3. Generate HTML coverage report
```bash
pytest --cov=src/personal_librarian --cov-report=html
```

## 4. Generate XML coverage report
```bash
pytest --cov=src/personal_librarian --cov-report=xml
```

## 5. Optional: If you have Coverage Gutters installed, you can use it to parse coverage.xml to visually display code coverage for every Python script

## Troubleshooting

# You may see the following error in your IDE terminal, especially if it is VSCode
- **PGVector / Postgres connection errors:** If tests or local runs fail when initializing the vector store, verify your `PGVECTOR_CONNECTION` value and that your Postgres instance is reachable.

  - Example connection string in `.env`:
    ```bash
    PGVECTOR_CONNECTION=postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian
    ```

  - Ensure the database has pgvector enabled:
    ```sql
    CREATE EXTENSION IF NOT EXISTS vector;
    ```

  - If the app hangs while trying to connect, test the database independently and verify host, port, and credentials.

