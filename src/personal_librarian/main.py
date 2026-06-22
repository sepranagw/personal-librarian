from dotenv import load_dotenv
import re
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from personal_librarian.tools import get_retriever_tool


load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Initialize tools and agent lazily to avoid import-time errors
_agent = None


def _extract_citations(tool_content):
    source_matches = re.findall(r"^Source:\s*(.+)$", tool_content, re.MULTILINE)
    page_matches = re.findall(r"^Page:\s*(.+)$", tool_content, re.MULTILINE)
    date_matches = re.findall(r"^Date:\s*(.+)$", tool_content, re.MULTILINE)

    citations = []
    for i, source in enumerate(source_matches):
        page = page_matches[i] if i < len(page_matches) else ""
        date = date_matches[i] if i < len(date_matches) else ""

        citation = f"Source: {source.strip()}"
        if page and page.strip():
            citation += f", Page: {page.strip()}"
        if date and date.strip():
            citation += f", Date: {date.strip()}"
        citations.append(citation)

    return citations


def get_agent():
    """Lazy initialization of agent to avoid loading tools on import."""
    global _agent
    if _agent is None:
        tools = [get_retriever_tool()]
        _agent = create_agent(model, tools)
    return _agent


def handle_chat(user_input):
    """
    Standardizes the input/output for local chat or AWS Lambda.
    """
    # The modern agent expects a dictionary with a list of messages
    inputs = {"messages": [("user", user_input)]}
    agent = get_agent()
    result = agent.invoke(inputs)

    # In the unified agent, the result is a State object
    # and the answer is the content of the last message
    final_answer = result["messages"][-1].content

    # Logic to extract sources from the message history
    sources = set()
    for msg in result["messages"]:
        if hasattr(msg, "name") and msg.name == "search_personal_docs":
            content = getattr(msg, "content", "")
            citations = _extract_citations(content)
            if citations:
                for citation in citations:
                    sources.add(citation)
            else:
                sources.add(f"Retrieved from: {msg.name}")

    return {
        "answer": final_answer,
        "sources": list(sources)
    }


def main():
    print("--- Unified LangChain Agent Active ---")
    print("\nWelcome to your Smart Agent Personal Assistant.")
    print("\nAsk me any questions regarding your documents.")
    while True:
        print("\n********If you'd like to finish, enter 'exit' or 'quit' without surrounding quotes.**********")
        q = input("\nYou: ")
        if q.lower() in ["exit", "quit"]:
            break

        try:
            res = handle_chat(q)
            print(f"\nAgent: {res['answer']}")
            if res["sources"]:
                print(f"Sources: {res['sources']}")
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
