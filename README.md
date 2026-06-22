# Getting Started

## Prerequisites

Before starting, make sure the following are installed on your machine:

- **Python 3.10+** — https://www.python.org/downloads/
- **Git** — https://git-scm.com/downloads
- **Docker Desktop** — https://www.docker.com/products/docker-desktop (required for the recommended Postgres+pgvector setup)
- An **OpenAI API key** — https://platform.openai.com/account/api-keys

---

## 1. Open a bash or powershell terminal

## 2. Clone the repository and go into the root directory
```bash
git clone https://github.com/sepranagw/personal-librarian.git
cd personal-librarian
```

## 3. Create your virtual environment
```bash
python -m venv venv
```

## 4. Activate newly created virtual environment
#### Linux/Mac
```bash
source venv/bin/activate
```
#### Windows 
```powershell
venv\Scripts\activate
```

**Windows Troubleshooting:** If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating again.

## 5. Install dependencies
```bash
pip install -r requirements.txt
```

## 6. Set up Postgres + pgvector

This project uses Postgres with the pgvector extension as its vector store. The recommended approach on Windows is Docker Desktop, because installing pgvector server binaries natively on Windows is not straightforward (no pre-built binaries are available via Stack Builder or GitHub releases as of this writing).

### Option A: Docker (recommended, all platforms)

#### 6a. Install Docker Desktop
Download and install from: https://www.docker.com/products/docker-desktop

Make sure Docker Desktop is running (whale icon in taskbar) before continuing.

#### 6b. Start the pgvector container

The image `pgvector/pgvector:pg17` ships with pgvector already installed. The tag name encodes the Postgres major version — if a newer Postgres version is available in the future, check https://hub.docker.com/r/pgvector/pgvector/tags for the right tag name.

```powershell
docker run --name pgvector-db `
  -e POSTGRES_PASSWORD=postgres `
  -e POSTGRES_DB=personal_librarian `
  -p 5432:5432 `
  -d pgvector/pgvector:pg17
```

Verify the container is running:
```powershell
docker ps
```
You should see `pgvector-db` with status `Up`.

#### 6c. Enable the pgvector extension

```powershell
docker exec -it pgvector-db psql -U postgres -d personal_librarian -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Verify:
```powershell
docker exec -it pgvector-db psql -U postgres -d personal_librarian -c "SELECT extname FROM pg_extension WHERE extname='vector';"
```

You should see `vector` returned in the output.

#### 6d. Stopping and restarting the container

To stop the container:
```powershell
docker stop pgvector-db
```

To start it again after stopping or after a reboot (Docker Desktop must be running first):
```powershell
docker start pgvector-db
```

> **Important:** The `pgvector-db` container does not start automatically on reboot. Each time you restart your machine or Docker Desktop, you must run `docker start pgvector-db` before running ingest or the agent. You can verify it's running with `docker ps`.

---

### Option B: Native Postgres install (Windows, advanced)

Native installation is possible but requires extra steps to get pgvector working. Use this only if you cannot use Docker.

#### 6e. Install PostgreSQL via winget (native)

First check what package IDs are available for your system — the versioned ID may change over time:
```powershell
winget search postgresql
```

Install using the versioned ID shown (example for version 17):
```powershell
winget install --id PostgreSQL.PostgreSQL.17 -e --source winget
```

If the installer reports exit code 1 but the files exist under `C:\Program Files\PostgreSQL\`, the service may not have been created. In that case, run the following in an elevated (Admin) PowerShell terminal to initialize the cluster and register the service:

```powershell
# Initialize data directory (will prompt for postgres password)
& "C:\Program Files\PostgreSQL\17\bin\initdb.exe" `
  -D "C:\Program Files\PostgreSQL\17\data" `
  -U postgres `
  -A scram-sha-256 `
  -W

# Register Windows service
& "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe" register `
  -N postgresql-x64-17 `
  -D "C:\Program Files\PostgreSQL\17\data"

# Start the service
Start-Service -Name postgresql-x64-17
```

The service name will include the major version number. Use `Get-Service *postgres*` to find the exact name on your system.

#### 6f. Install pgvector server binaries (native)

**This is the hard part on Windows.** pgvector does not ship pre-built Windows binaries via Stack Builder or GitHub releases. Options:

- Build from source (requires Visual Studio and Postgres dev headers — complex).
- Use a third-party package such as Postgres.app (Mac only) or a cloud-hosted Postgres with pgvector.
- Switch to the Docker approach above.

#### 6g. Create the database and enable extension (native)

Add psql to your PATH for the current session (adjust version folder if needed):
```powershell
$env:Path += ";C:\Program Files\PostgreSQL\17\bin"
```

Create the database:
```powershell
psql -U postgres -h localhost -p 5432 -d postgres -c "CREATE DATABASE personal_librarian;"
```

Enable the extension:
```powershell
psql -U postgres -h localhost -p 5432 -d personal_librarian -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

---

### 6h. Verify Python connectivity

After setting up via either option, confirm your Python environment can connect:

```powershell
python -c "import os; from dotenv import load_dotenv; import psycopg; load_dotenv(); dsn=os.getenv('PGVECTOR_CONNECTION').replace('postgresql+psycopg://','postgresql://'); conn=psycopg.connect(dsn, connect_timeout=5); cur=conn.cursor(); cur.execute('select extname from pg_extension where extname=%s',('vector',)); print('PGVECTOR_ENABLED:', cur.fetchone()); cur.close(); conn.close()"
```

Expected output: `PGVECTOR_ENABLED: ('vector',)`

---

## 7. Set up environment variables

Now that your database is running, create a `.env` file in the project root:

```
OPENAI_API_KEY=your-api-key-here
PGVECTOR_CONNECTION=postgresql+psycopg://<db_user>:<db_password>@<db_host>:<db_port>/<db_name>
PGVECTOR_COLLECTION=personal_docs
```

**What each value means:**
- `OPENAI_API_KEY` — your OpenAI API key from https://platform.openai.com/account/api-keys
- `PGVECTOR_CONNECTION` — the connection string for your Postgres database. Replace each part:
  - `<db_user>` — your Postgres username (e.g. `postgres`)
  - `<db_password>` — the password set when creating the Postgres instance, this was likely set by docker as `postgres`
  - `<db_host>` — hostname of your DB server (`localhost` if running locally or via Docker on the same machine)
  - `<db_port>` — Postgres port (default is `5432`)
  - `<db_name>` — the database name you created (e.g. `personal_librarian`)
- `PGVECTOR_COLLECTION` — the name of the vector collection inside the database. You can keep `personal_docs` or choose your own name.

**Example using Docker with default settings (as set up in Step 6):**
```
PGVECTOR_CONNECTION=postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian
PGVECTOR_COLLECTION=personal_docs
```

---

## 8. Run the test script
```bash
python hello_openai_API.py
```
## 9. You should see a tech-themed haiku appear on the command line

---

## 10. Ingest your documents

Create the data directory if it does not exist:

```bash
mkdir -p data
```

PowerShell equivalent on Windows:

```powershell
New-Item -ItemType Directory -Path .\data -Force
```

Then add your documents (PDF, DOCX, XLSX, PPTX) to the `./data/` folder and run:

```bash
python ingest.py
```

This processes each file, generates embeddings via OpenAI, and stores them in the pgvector database. Files already processed are tracked in `processed_files.json` and skipped on subsequent runs.

> **Note:** Make sure your pgvector container (or native Postgres) is running before ingesting.

---

## 11. Run the agent

```bash
python main.py
```

The agent will start an interactive session where you can ask questions about your ingested documents. Type `exit` or `quit` to stop.

> **Reminder:** Both Docker Desktop and the `pgvector-db` container must be running before starting the agent. Run `docker start pgvector-db` if needed.
