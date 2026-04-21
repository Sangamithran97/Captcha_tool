import os
import asyncio
from dotenv import load_dotenv

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_KEY:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env file")

async def main():
    print("🔗 Connecting to MCP Captcha Server...")

    SERVER_PATH = os.path.abspath("mcp_server.py")

    client = MultiServerMCPClient({
        "Captcha Tools": {
            "transport": "stdio",
            "command": "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3",
            "args": [SERVER_PATH],
        }
    })

    try:
        tools = await client.get_tools()
        if not tools:
            print("⚠️ No tools discovered. Check server logs.")
            return
        tool_names = [t.name if hasattr(t, "name") else str(t) for t in tools]
        print(f"✅ Connected! Tools discovered: {tool_names}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return


    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_KEY,
        temperature=0.3
    )

    agent = create_react_agent(
        model=llm,
        tools=tools,
        checkpointer=InMemorySaver(),
        prompt="You are a CAPTCHA assistant that can generate, verify, and decode CAPTCHAs using the available tools."
    )

    thread_config = {"configurable": {"thread_id": "captcha_session"}}

    while True:
        q = input("\n💬 Ask me something (or type 'exit' to quit): ").strip()
        if q.lower() == "exit":
            print("👋 Exiting session.")
            break

        try:
            response = await agent.ainvoke(
                {"messages": [{"role": "user", "content": q}]},
                config=thread_config
            )
            print("\n🧠 Response:\n", response["messages"][-1].content)
        except Exception as e:
            print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())