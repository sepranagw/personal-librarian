# What is this project?

## This RAG LLM project is currently a 'template' in Github but I am going to fork from the template into various projects that will take the form of Smart Agents that will likely be publicly available on the internet that can answer questions based on various publicly stored knowledge bases that each a RAG LLM Smart Agent will be trained on

# Getting Started

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

## 6. Set up environment variables
Create a `.env` file in the project root and add your OpenAI API key and Postgres settings:
```
OPENAI_API_KEY=your-api-key-here
PGVECTOR_CONNECTION=postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian
PGVECTOR_COLLECTION=personal_docs
```

## 7. Ensure Postgres has pgvector enabled
Run this in your Postgres database before ingestion:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## 8. Run the test script
```bash
python hello_openai_API.py
```
## 9. You should see a tech-themed haiku appear on the command line
