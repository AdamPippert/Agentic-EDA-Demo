# agent.py

import os
from typing import Annotated, Any, Dict
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig
from fastapi import FastAPI
from langserve import add_routes
import uvicorn

# --- 1. Define Tools ---
@tool
def multiply(a: int, b: int) -> int:
    """Multiplies two integers and returns the result."""
    return a * b

@tool
def add(a: int, b: int) -> int:
    """Adds two integers and returns the result."""
    return a + b

tools = [multiply, add]

# --- 2. Initialize LLM and Agent ---
# Ensure OPENAI_API_KEY is set in your environment variables on OpenShift
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Get the prompt for the tool-calling agent
prompt = hub.pull("hwchase17/openai-tools-agent")

# Create the agent
agent_runnable = create_tool_calling_agent(llm, tools, prompt)

# A simple wrapper for execution (optional, but good practice for API)
def invoke_agent(input_data: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
    """Invokes the agent with a message and returns the final response."""
    # The agent expects a list of messages
    message = HumanMessage(content=input_data.get("input", "What is 2 + 2?"))
    result = agent_runnable.invoke({"input": message, "tools": tools, "chat_history": []}, config)
    
    # Process the final result to return a string response
    # In a real app, you would handle tool calls/intermediate steps differently.
    # For a simple synchronous call, this is fine.
    # The actual output structure from agent.invoke can be complex; 
    # for a final answer, it's often a HumanMessage or AIMessage.
    
    # To simplify, let's just return the message content from the last step.
    return {"output": result.content}

# --- 3. Set up LangServe API (Recommended for deployment) ---
app = FastAPI(
    title="LangChain Tool-Calling Agent",
    version="1.0",
    description="An agent deployed via LangServe on OpenShift AI",
)

# Add the runnable to the FastAPI app under a specific path
# This exposes a REST API endpoint like /agent/invoke
add_routes(
    app,
    agent_runnable.with_config({"tags": ["agent"]}),
    path="/agent"
)

if __name__ == "__main__":
    # You might want to use Gunicorn for production, but uvicorn for local testing
    uvicorn.run(app, host="0.0.0.0", port=8080)
