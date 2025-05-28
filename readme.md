# Model Context Protocol (MCP)
## Example with simple chatbox

MCP is an open standard, open-source framework introduced by Anthropic which aims to standardize how AI models (especially large language models or LLMs) integrate and share data with external tools, systems, and data sources.
Think of it as learning API REST protocol. It will allow you to quickly create AI agents and escalate it using industries best practices.

For this example I am using GROQ with llama model, which is free.
The content has been taking from this course: https://learn.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic/lesson/hg6oi/chatbot-example
It will research papers on a given topic and return 5 titles with IDs. They will be stored on a papers folder. You can pass as many requirements as needed and then write quit to exit.

### How to run it

First get your API KEY from GROQ: https://console.groq.com/keys

Then run it:
```
python -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
python main.py
```

### Running the server

With the class research_server.py we are creating the server for our model. You can test it with an inspector (with no need of the client of our model). Primitivs will be shown (tools, resources, prompts)... For me, kind of a swagger that helps you to understand what is created on the back.

First you will need to install uv
````
pip install uv
````

Then initialize uv. this will create a project.toml file, what uv uses to define project's dependencies and configurations.
````
uv init
```
Install dependencies:
```
uv add mcp arxiv
```
And run the inspector:
````
npx @modelcontextprotocol/inspector uv run research_server.py
```

Note that for the inspector you will need node.js in your local. 
Source: https://github.com/modelcontextprotocol/inspector
