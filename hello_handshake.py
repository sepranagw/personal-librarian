from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

try:
    llm = ChatOpenAI(model="gpt-4o-mini")
    res = llm.invoke("Say 'System Ready'")
    print(f"✅ Connection Test: {res.content}")
except Exception as e:
    print(f"❌ Connection Error: {e}")
