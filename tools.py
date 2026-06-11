import os

from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import create_retriever_tool


PGVECTOR_CONNECTION = os.getenv(
    "PGVECTOR_CONNECTION",
    "postgresql+psycopg://postgres:postgres@localhost:5432/personal_librarian"
)
PGVECTOR_COLLECTION = os.getenv("PGVECTOR_COLLECTION", "personal_docs")


def get_pgvector_store(embeddings):
    return PGVector(
        embeddings=embeddings,
        collection_name=PGVECTOR_COLLECTION,
        connection=PGVECTOR_CONNECTION,
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
