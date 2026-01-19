from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import create_retriever_tool
import os



def get_retriever_tool():
    # Load the existing database
    embeddings = OpenAIEmbeddings()
    faiss_path = "./db/faiss_index"
    if not os.path.exists(faiss_path):
        raise FileNotFoundError(f"FAISS index not found at {faiss_path}. Run ingest.py first.")
    vectorstore = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever()

    # Wrap it as a tool
    return create_retriever_tool(
        retriever,
        "search_personal_docs",
        "Use this tool to find information from the user's uploaded files and notes."
    )
