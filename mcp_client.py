from typing import List, Dict, TypedDict
from dotenv import load_dotenv
from tool_mapping import execute_tool, tools
from groq import Groq
import os
import json
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import nest_asyncio

nest_asyncio.apply()

load_dotenv() 


class ToolDefinition(TypedDict):
    name: str
    description: str
    input_schema: dict


class MCP_ChatBot:
    def __init__(self):
        # Initialize session and client objects
        self.sessions = {}  # Dictionary to store sessions
        self.exit_stack = AsyncExitStack()
        self.available_tools = []
        self.available_prompts = []
        self.tool_to_session = {}  # Dictionary to map tools to sessions
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
       

    async def connect_to_server(self, server_name, server_config) -> None:
        """Connect to a single MCP server."""
        try:
            server_params = StdioServerParameters(**server_config)
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            
            # Initialize the session
            try:
                await session.initialize()
            except Exception as e:
                print(f"Warning: Session initialization failed for {server_name}: {e}")
                return
            
            self.sessions[server_name] = session
            
            # List available tools for this session
            try:
                response = await session.list_tools()
                if response and response.tools:
                    tools = response.tools
                    print(f"\nConnected to {server_name} with tools:", [t.name for t in tools])
                    
                    for tool in tools:
                        self.tool_to_session[tool.name] = session
                        self.available_tools.append({
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": tool.inputSchema
                            }
                        })
            except Exception as e:
                print(f"Warning: Could not list tools for {server_name}: {e}")

        except Exception as e:
            print(f"Failed to connect to {server_name}: {e}")
            raise

    async def connect_to_servers(self) -> None:
        """Connect to all configured MCP servers."""
        try:
            with open("server_config.json", "r") as file:
                data = json.load(file)
            
            servers = data.get("mcpServers", {})
            
            for server_name, server_config in servers.items():
                await self.connect_to_server(server_name, server_config)
        except Exception as e:
            print(f"Error loading server configuration: {e}")
            raise

    async def process_query(self, query) -> None:
        """Process a query using Groq and handle tool calls."""
        messages = [{'role': 'user', 'content': query}]
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                tools=self.available_tools,
                tool_choice="auto",
                max_tokens=2024
            )
            
            process_query = True
            while process_query:
                assistant_message = response.choices[0].message
                
                # Handle text response
                if assistant_message.content:
                    print(assistant_message.content)
                    process_query = False
                
                # Handle tool calls
                if assistant_message.tool_calls:
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        
                        print(f"Calling tool {tool_name} with args {tool_args}")
                        
                        # Call the tool using MCP session
                        session = self.tool_to_session[tool_name]
                        result = await session.call_tool(tool_name, arguments=tool_args)
                        
                        # Add the tool response to messages
                        messages.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call]
                        })
                        
                        tool_response = str(result.content) if result.content is not None else ""
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_response
                        })
                        
                        # Get new response from Groq
                        response = self.groq_client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=messages,
                            tools=self.available_tools,
                            tool_choice="auto",
                            max_tokens=2024
                        )
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            raise

    async def chat_loop(self):
        """Main chat loop for user interaction."""
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")
        while True:
            try:
                query = input("\nQuery: ").strip()
        
                if query.lower() == 'quit':
                    break
                    
                await self.process_query(query)
                print("\n")
                    
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources and close connections."""
        try:
            # Close the exit stack which will handle session cleanup
            try:
                await self.exit_stack.aclose()
            except Exception as e:
                if "unhandled errors in a TaskGroup" in str(e):
                    pass
                else:
                    print(f"Warning: Error during exit stack cleanup: {str(e)}")
        except Exception as e:
            print(f"Warning: Error during cleanup: {str(e)}")