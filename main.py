from typing import List
from dotenv import load_dotenv
from tool_mapping import execute_tool, tools
from research_server import mcp
import asyncio
from mcp_client import MCP_ChatBot
import sys
import signal

def run_mcp_server():
    try:
        print("Starting MCP server...")
        mcp.run(transport='stdio', log_level="INFO")
    except Exception as e:
        print(f"Error running MCP server: {str(e)}")
        sys.exit(1)

async def shutdown():
    print("\nShutdown signal received...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop = asyncio.get_running_loop()
    loop.stop()

async def main():
    # Set up signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))

    chatbot = MCP_ChatBot()
    try:
        print("Connecting to servers...")
        await chatbot.connect_to_servers()
        print("Starting chat loop...")
        await chatbot.chat_loop()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
    finally:
        try:
            print("Cleaning up resources...")
            await chatbot.cleanup()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        sys.exit(1)