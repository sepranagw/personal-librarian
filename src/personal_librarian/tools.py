from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import create_retriever_tool
from langchain_core.prompts import PromptTemplate

from personal_librarian.config import get_pgvector_store

load_dotenv()


def get_retriever_tool():
    embeddings = OpenAIEmbeddings()
    vectorstore = get_pgvector_store(embeddings)
    retriever = vectorstore.as_retriever()

    document_prompt = PromptTemplate.from_template(
        "Source: {source_file}\n"
        "Path: {source_path}\n"
        "Page: {page}\n"
        "Date: {doc_date}\n"
        "Content:\n{page_content}"
    )

    # Wrap it as a tool
    return create_retriever_tool(
        retriever,
        "search_personal_docs",
        (
            "Use this tool to find information from the user's uploaded files and notes. "
            "Retrieved chunks include source metadata for citations."
        ),
        document_prompt=document_prompt,
    )


def get_retriever_tool_with_filter(metadata_filter, k=4):
    embeddings = OpenAIEmbeddings()
    vectorstore = get_pgvector_store(embeddings)
    search_kwargs = {"k": k, "filter": metadata_filter}
    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)

    document_prompt = PromptTemplate.from_template(
        "Source: {source_file}\n"
        "Path: {source_path}\n"
        "Page: {page}\n"
        "Date: {doc_date}\n"
        "Content:\n{page_content}"
    )

    return create_retriever_tool(
        retriever,
        "search_personal_docs",
        (
            "Use this tool to find information from the user's uploaded files and notes. "
            "Retrieved chunks include source metadata for citations."
        ),
        document_prompt=document_prompt,
    )
