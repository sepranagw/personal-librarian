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

def load_new_docs(loader, filename, embeddings, manifest, mtime, vectorstore):
    print(f"Processing: {filename}")
    docs = loader.load()
    filtered_chunks = chunk_and_filter_docs(docs)

    if vectorstore is None:
        vectorstore = FAISS.from_documents(filtered_chunks, embeddings)
    else:
        vectorstore.add_documents(filtered_chunks)
    manifest[filename] = mtime
    return True, vectorstore, manifest

def build_vector_db():
    manifest = load_manifest()
    embeddings = OpenAIEmbeddings()

    if os.path.exists(FAISS_INDEX_PATH):
        vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        vectorstore = None

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
            new_docs_loaded, vectorstore, manifest= load_new_docs(loader, filename, embeddings, manifest, mtime, vectorstore)

    if new_docs_loaded:
        save_manifest(manifest)
        vectorstore.save_local(FAISS_INDEX_PATH)
        print(f"Database updated and saved to {FAISS_INDEX_PATH}")
    else:
        print("No new changes detected.")


if __name__ == "__main__":
    print("--- Starting Ingestion Process ---")
    build_vector_db()
