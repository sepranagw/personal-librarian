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
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import filter_complex_metadata
from dotenv import load_dotenv

load_dotenv()

MANIFEST_FILE = "processed_files.json"
FAISS_INDEX_PATH = "./db/faiss_index"


def load_manifest():
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_manifest(manifest):
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f)


def build_vector_db():
    manifest = load_manifest()
    embeddings = OpenAIEmbeddings()

    # Initialize VectorStore (loads existing if it exists)
    if os.path.exists(FAISS_INDEX_PATH):
        vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        vectorstore = None

    new_docs_loaded = False
    source_dir = "./data"

    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        mtime = os.path.getmtime(file_path)

        # Skip if already processed
        if filename in manifest and manifest[filename] >= mtime:
            print(f"Skipping {filename}, already previously processed...")
            continue

        loader = None
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif filename.endswith(".docx") or filename.endswith(".doc"):
            loader = Docx2txtLoader(file_path)
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            loader = UnstructuredExcelLoader(file_path, mode="elements")
        elif filename.endswith(".pptx") or filename.endswith(".ppt"):
            loader = UnstructuredPowerPointLoader(file_path, mode = "elements")

        if loader:
            print(f"Processing: {filename}")
            docs = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_documents(docs)
            filtered_chunks = filter_complex_metadata(chunks)

            if vectorstore is None:
                vectorstore = FAISS.from_documents(filtered_chunks, embeddings)
            else:
                vectorstore.add_documents(filtered_chunks)
            manifest[filename] = mtime
            new_docs_loaded = True

    if new_docs_loaded:
        save_manifest(manifest)
        vectorstore.save_local(FAISS_INDEX_PATH)
        print(f"Database updated and saved to {FAISS_INDEX_PATH}")
    else:
        print("No new changes detected.")


if __name__ == "__main__":
    print("--- Starting Ingestion Process ---")
    build_vector_db()
