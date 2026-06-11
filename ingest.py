import os
import json
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_community.vectorstores.utils import filter_complex_metadata
from dotenv import load_dotenv

load_dotenv()

MANIFEST_FILE = "processed_files.json"
PGVECTOR_CONNECTION = os.getenv(
    "PGVECTOR_CONNECTION",
    "postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian"
)
PGVECTOR_COLLECTION = os.getenv("PGVECTOR_COLLECTION", "personal_docs")


def load_manifest():
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_manifest(manifest):
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f)

def yield_loader(filename, file_path):
    loader_dict = {
        ".pdf" : lambda: PyPDFLoader(file_path),
        ".doc" : lambda: Docx2txtLoader(file_path),
        ".xls" : lambda: UnstructuredExcelLoader(file_path, mode="elements"),
        ".ppt" : lambda: UnstructuredPowerPointLoader(file_path, mode="elements")
    }
    extension = filename.rfind('.')
    # if .pptx, shorten to .ppt, .xlsx -> .xls, etc
    extension_short = filename[extension:extension+4] if extension != -1 else ""
    return loader_dict[extension_short]() if extension_short else None

def chunk_and_filter_docs(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    return filter_complex_metadata(chunks)


def get_pgvector_store(embeddings):
    return PGVector(
        embeddings=embeddings,
        collection_name=PGVECTOR_COLLECTION,
        connection=PGVECTOR_CONNECTION,
        use_jsonb=True,
    )

def load_new_docs(loader, filename, manifest, mtime, vectorstore):
    print(f"Processing: {filename}")
    docs = loader.load()
    filtered_chunks = chunk_and_filter_docs(docs)

    vectorstore.add_documents(filtered_chunks)
    manifest[filename] = mtime
    return True, vectorstore, manifest

def build_vector_db():
    manifest = load_manifest()
    embeddings = OpenAIEmbeddings()
    vectorstore = get_pgvector_store(embeddings)

    new_docs_loaded = False
    source_dir = "./data"

    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        mtime = os.path.getmtime(file_path)

        if filename in manifest and manifest[filename] >= mtime:
            print(f"Skipping {filename}, already previously processed...")
            continue

        loader = yield_loader(filename, file_path)

        if loader:
            new_docs_loaded, vectorstore, manifest = load_new_docs(loader, filename, manifest, mtime, vectorstore)

    if new_docs_loaded:
        save_manifest(manifest)
        print(f"Database updated in PGVector collection '{PGVECTOR_COLLECTION}'")
    else:
        print("No new changes detected.")


if __name__ == "__main__":
    print("--- Starting Ingestion Process ---")
    build_vector_db()
