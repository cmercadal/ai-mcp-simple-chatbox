from typing import List
from dotenv import load_dotenv
from tool_mapping import execute_tool, tools
from groq import Groq
import os
import json

load_dotenv() 
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def process_query(query):
    messages = [{'role': 'user', 'content': query}]
    
    # Create the chat completion with tools
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        tools=tools,
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
                
                # Execute the tool
                result = execute_tool(tool_name, tool_args)
                
                # Add the tool response to messages
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call]
                })
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
                
                # Get new response from Groq
                response = groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    max_tokens=2024
                )

def chat_loop():
    print("Type your queries or 'quit' to exit.")
    while True:
        try:
            query = input("\nQuery: ").strip()
            if query.lower() == 'quit':
                break
    
            process_query(query)
            print("\n")
        except Exception as e:
            print(f"\nError: {str(e)}")

def main():
    chat_loop()

if __name__ == "__main__":
    main()