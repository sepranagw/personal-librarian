import os

from dotenv import load_dotenv
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import create_retriever_tool

load_dotenv()


def _require_pgvector_connection():
    connection = os.getenv("PGVECTOR_CONNECTION")
    if not connection:
        raise ValueError(
            "PGVECTOR_CONNECTION is required. Set it in your environment or .env file."
        )
    return connection


def _require_pgvector_collection():
    collection = os.getenv("PGVECTOR_COLLECTION")
    if not collection:
        raise ValueError(
            "PGVECTOR_COLLECTION is required. Set it in your environment or .env file."
        )
    return collection


def get_pgvector_store(embeddings):
    connection = _require_pgvector_connection()
    collection_name = _require_pgvector_collection()
    return PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )


def get_retriever_tool():
    embeddings = OpenAIEmbeddings()
    vectorstore = get_pgvector_store(embeddings)
    retriever = vectorstore.as_retriever()

    # Wrap it as a tool
    return create_retriever_tool(
        retriever,
        "search_personal_docs",
        "Use this tool to find information from the user's uploaded files and notes."
    )
