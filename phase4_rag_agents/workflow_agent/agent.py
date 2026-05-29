import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def web_search(query):
    return f"Simulated search results for: {query}"

def summarize(text):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Summarize: {text}"}],
    )
    return resp.choices[0].message.content

TOOLS = {"web_search": web_search, "summarize": summarize}

def run_agent(task):
    messages = [
        {"role": "system", "content": "You are a workflow agent. Use the available tools: web_search, summarize."},
        {"role": "user", "content": task},
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=[{
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web",
                "parameters": {"type": "object", "properties": {"query": {"type": "string"}}},
            },
        }],
    )
    return response.choices[0].message

if __name__ == "__main__":
    result = run_agent("Search for AI news and summarize the top result")
    print(result)
