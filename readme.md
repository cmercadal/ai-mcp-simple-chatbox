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




