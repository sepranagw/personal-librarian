from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
# from langchain.tools import create_retriever_tool
from langchain_core.tools import create_retriever_tool


def get_retriever_tool():
    # Load the existing database
    vectorstore = Chroma(
        persist_directory="./db",
        embedding_function=OpenAIEmbeddings()
    )
    retriever = vectorstore.as_retriever()

    # Wrap it as a tool
    return create_retriever_tool(
        retriever,
        "search_personal_docs",
        "Use this tool to find information from the user's uploaded files and notes."
    )
