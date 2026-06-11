# How to run unit tests

## 1. Open a bash or powershell terminal. Install coverage if you haven't already
```bash
pip install coverage
```

## 2. Run the following command with coverage.  Results will show you how many tests passed. OK means they all passed.
```bash
coverage run -m unittest discover tests
```

## 3. Run the following to see your code coverage for each production code file
```bash
coverage report
```

## 3. Run the following to write an XML coverage report
```bash
coverage xml
```

## 4. Optional: If you have Coverage Gutters installed, you can use it to parse coverage.xml to visually display code coverage for every Python script

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

