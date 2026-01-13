from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent  # <--- The updated, non-deprecated import
from tools import get_retriever_tool

# 1. Setup
load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
tools = [get_retriever_tool()]

# 2. Build the Agent
# This is the modern 'Unified Agent' that replaces create_react_agent
agent = create_agent(model, tools)

def handle_chat(user_input):
    """
    Standardizes the input/output for local chat or AWS Lambda.
    """
    # The modern agent expects a dictionary with a list of messages
    inputs = {"messages": [("user", user_input)]}
    result = agent.invoke(inputs)
    
    # In the unified agent, the result is a State object 
    # and the answer is the content of the last message
    final_answer = result["messages"][-1].content
    
    # Logic to extract sources from the message history
    sources = set()
    for msg in result["messages"]:
        if hasattr(msg, "name") and msg.name == "search_personal_docs":
            # We add a marker to know this came from our specific tool
            sources.add(f"Retrieved from: {msg.name}")

    return {
        "answer": final_answer,
        "sources": list(sources)
    }

if __name__ == "__main__":
    print("--- Unified LangChain Agent Active ---")
    print("\nWelcome to your Smart Agent Personal Assistant.")
    print("\nAsk me any questions regarding your documents.")
    while True:
        print("\n********If you'd like to finish, enter 'exit' or 'quit' without surrounding quotes.**********")
        q = input("\nYou: ")
        if q.lower() in ["exit", "quit"]: break
        res = handle_chat(q)
        print(f"\nAgent: {res['answer']}")
        if res["sources"]:
            print(f"Sources: {res['sources']}")