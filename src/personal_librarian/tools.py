from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import create_retriever_tool

from personal_librarian.config import get_pgvector_store

load_dotenv()


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
