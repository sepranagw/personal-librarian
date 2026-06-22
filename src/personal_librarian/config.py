"""
Shared configuration and environment validation for Personal Librarian.
Consolidates environment variable handling and vector store initialization.
"""
import os
from langchain_postgres import PGVector


def require_pgvector_connection():
    """Get and validate PGVECTOR_CONNECTION from environment."""
    connection = os.getenv("PGVECTOR_CONNECTION")
    if not connection:
        raise ValueError(
            "PGVECTOR_CONNECTION is required. Set it in your environment or .env file."
        )
    return connection


def require_pgvector_collection():
    """Get and validate PGVECTOR_COLLECTION from environment."""
    collection = os.getenv("PGVECTOR_COLLECTION")
    if not collection:
        raise ValueError(
            "PGVECTOR_COLLECTION is required. Set it in your environment or .env file."
        )
    return collection


def get_pgvector_store(embeddings):
    """
    Initialize and return a PGVector store for vector embeddings.

    Args:
        embeddings: OpenAIEmbeddings instance

    Returns:
        PGVector instance configured with environment settings
    """
    connection = require_pgvector_connection()
    collection_name = require_pgvector_collection()
    return PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )
