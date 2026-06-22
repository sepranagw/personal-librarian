import os
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.utils import filter_complex_metadata
from dotenv import load_dotenv

from personal_librarian.config import get_pgvector_store as config_get_pgvector_store
from personal_librarian.config import require_pgvector_collection

load_dotenv()

MANIFEST_FILE = "processed_files.json"


@dataclass(frozen=True)
class IngestConfig:
    manifest_file: str = MANIFEST_FILE
    source_dir: str = "./data"
    chunk_size: int = 1000
    chunk_overlap: int = 100
    pgvector_connection: str | None = None
    pgvector_collection: str | None = None


class ManifestStore:
    def __init__(self, manifest_file):
        self.manifest_file = manifest_file

    def load(self):
        if os.path.exists(self.manifest_file):
            with open(self.manifest_file, 'r') as f:
                return json.load(f)
        return {}

    def save(self, manifest):
        with open(self.manifest_file, 'w') as f:
            json.dump(manifest, f)


class IngestionService:
    def __init__(self, config, manifest_loader=None, manifest_saver=None):
        self.config = config
        self.manifest_loader = manifest_loader
        self.manifest_saver = manifest_saver

    def yield_loader(self, filename, file_path):
        loader_dict = {
            ".pdf": lambda: PyPDFLoader(file_path),
            ".doc": lambda: Docx2txtLoader(file_path),
            ".xls": lambda: UnstructuredExcelLoader(file_path, mode="elements"),
            ".ppt": lambda: UnstructuredPowerPointLoader(file_path, mode="elements"),
        }
        extension = filename.rfind('.')
        # if .pptx, shorten to .ppt, .xlsx -> .xls, etc
        extension_short = filename[extension:extension + 4] if extension != -1 else ""
        return loader_dict[extension_short]() if extension_short else None

    def chunk_and_filter_docs(self, docs):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
        )
        chunks = text_splitter.split_documents(docs)
        return filter_complex_metadata(chunks)

    def _extract_page(self, metadata):
        page = metadata.get("page")
        if page is None:
            page = metadata.get("page_number")
        if page is None:
            page = metadata.get("slide_number")
        return page

    def _extract_doc_date(self, metadata):
        for key in ["doc_date", "date", "created", "modified", "last_modified"]:
            value = metadata.get(key)
            if value:
                return str(value)
        return None

    def enrich_metadata(self, docs, filename, file_path, mtime):
        ingested_at = datetime.now(timezone.utc).isoformat()
        source_mtime = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
        source_type = os.path.splitext(filename)[1].lower()

        for doc in docs:
            metadata = dict(doc.metadata or {})
            metadata["source"] = str(metadata.get("source") or filename)
            metadata["source_file"] = filename
            metadata["source_path"] = file_path
            metadata["source_type"] = source_type
            metadata["ingested_at"] = ingested_at
            metadata["source_mtime"] = source_mtime

            page = self._extract_page(metadata)
            metadata["page"] = "" if page is None else str(page)

            doc_date = self._extract_doc_date(metadata)
            metadata["doc_date"] = "" if doc_date is None else doc_date

            doc.metadata = metadata

        return docs

    def get_pgvector_store(self, embeddings):
        # Use the config module's function for environment-based initialization,
        # or allow override via config for testing
        if self.config.pgvector_connection and self.config.pgvector_collection:
            from langchain_postgres import PGVector
            return PGVector(
                embeddings=embeddings,
                collection_name=self.config.pgvector_collection,
                connection=self.config.pgvector_connection,
                use_jsonb=True,
            )
        # Otherwise use the shared config function (validates environment)
        return config_get_pgvector_store(embeddings)

    def load_new_docs(self, loader, filename, manifest, mtime, vectorstore):
        print(f"Processing: {filename}")
        file_path = os.path.join(self.config.source_dir, filename)
        docs = loader.load()
        docs = self.enrich_metadata(docs, filename, file_path, mtime)
        filtered_chunks = self.chunk_and_filter_docs(docs)

        vectorstore.add_documents(filtered_chunks)
        manifest[filename] = mtime
        return True, vectorstore, manifest

    def run(self):
        manifest = self.manifest_loader() if self.manifest_loader else {}
        embeddings = OpenAIEmbeddings()
        vectorstore = self.get_pgvector_store(embeddings)

        new_docs_loaded = False

        for filename in os.listdir(self.config.source_dir):
            file_path = os.path.join(self.config.source_dir, filename)
            mtime = os.path.getmtime(file_path)

            if filename in manifest and manifest[filename] >= mtime:
                print(f"Skipping {filename}, already previously processed...")
                continue

            loader = self.yield_loader(filename, file_path)

            if loader:
                new_docs_loaded, vectorstore, manifest = self.load_new_docs(
                    loader,
                    filename,
                    manifest,
                    mtime,
                    vectorstore,
                )

        if new_docs_loaded:
            if self.manifest_saver:
                self.manifest_saver(manifest)
            print(
                f"Database updated in PGVector collection "
                f"'{self.config.pgvector_collection or require_pgvector_collection()}'"
            )
        else:
            print("No new changes detected.")


_DEFAULT_CONFIG = IngestConfig()
_DEFAULT_MANIFEST_STORE = ManifestStore(_DEFAULT_CONFIG.manifest_file)
_DEFAULT_SERVICE = IngestionService(_DEFAULT_CONFIG)


def load_manifest():
    return _DEFAULT_MANIFEST_STORE.load()


def save_manifest(manifest):
    _DEFAULT_MANIFEST_STORE.save(manifest)


def build_vector_db():
    service = IngestionService(
        _DEFAULT_CONFIG,
        manifest_loader=load_manifest,
        manifest_saver=save_manifest,
    )
    service.run()


def main():
    print("--- Starting Ingestion Process ---")
    build_vector_db()


if __name__ == "__main__":
    main()
