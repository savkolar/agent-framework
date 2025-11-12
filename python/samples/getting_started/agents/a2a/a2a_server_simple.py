# Copyright (c) Microsoft. All rights reserved.

"""
Simple A2A Server Example

This sample demonstrates how to host an agent using the A2A protocol.
It creates a FastAPI server that exposes an agent at /.well-known/agent.json
and handles A2A protocol messages.

To run this server:
1. Install dependencies: pip install fastapi uvicorn
2. Run: python a2a_server_simple.py
3. The server will start at http://localhost:8000

Then test with the client:
1. Set environment: $env:A2A_AGENT_HOST="http://localhost:8000"
2. Run client: python agent_with_a2a.py
"""

import asyncio
import os
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# Import agent framework components
from agent_framework import ChatAgent
from azure.ai.inference.aio import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

app = FastAPI(title="A2A Server Example")

# Agent card definition - this is what gets exposed at /.well-known/agent.json
AGENT_CARD = {
    "name": "PythonJokeAgent",
    "description": "A helpful agent that tells jokes and answers questions",
    "version": "1.0.0",
    "id": "python-joke-agent-001",
    "capabilities": {
        "streaming": False,
        "sync": True,
        "async": True
    },
    "endpoints": {
        "message": {
            "path": "/api/messages",
            "method": "POST"
        }
    },
    "model": {
        "name": "gpt-4o",
        "provider": "Azure OpenAI"
    }
}

# Initialize the agent
agent = None


async def initialize_agent():
    """Initialize the ChatAgent with Azure OpenAI."""
    global agent
    
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o")
    
    if not endpoint or not api_key:
        raise ValueError("AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY must be set")
    
    chat_client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key),
        api_version="2024-05-01-preview"
    )
    
    agent = ChatAgent(
        chat_client=chat_client,
        model=deployment,
        name="PythonJokeAgent",
        instructions="You are a helpful and humorous assistant. Tell engaging jokes when asked and provide helpful answers to questions."
    )
    
    print(f"✓ Agent initialized with model: {deployment}")


@app.on_event("startup")
async def startup_event():
    """Initialize the agent on server startup."""
    await initialize_agent()


@app.get("/.well-known/agent.json")
async def get_agent_card():
    """
    A2A protocol endpoint - returns the agent card.
    This is the standard discovery endpoint for A2A agents.
    """
    return JSONResponse(content=AGENT_CARD)


@app.post("/api/messages")
async def handle_message(request: Request):
    """
    A2A protocol endpoint - handles incoming messages.
    This endpoint receives A2A-formatted messages and returns responses.
    """
    try:
        # Parse the incoming A2A message
        body = await request.json()
        
        # Extract the message content
        # A2A messages typically have: {"messages": [{"role": "user", "content": "..."}]}
        messages = body.get("messages", [])
        
        if not messages:
            return JSONResponse(
                status_code=400,
                content={"error": "No messages provided"}
            )
        
        # Get the last user message
        user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content")
                if isinstance(content, str):
                    user_message = content
                elif isinstance(content, list):
                    # Handle content arrays
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            user_message = item.get("text")
                            break
                break
        
        if not user_message:
            return JSONResponse(
                status_code=400,
                content={"error": "No user message found"}
            )
        
        print(f"\n📨 Received message: {user_message}")
        
        # Run the agent
        response = await agent.run(user_message)
        response_text = response.text if hasattr(response, 'text') else str(response)
        
        print(f"🤖 Agent response: {response_text}")
        
        # Return A2A-formatted response
        a2a_response = {
            "messages": [
                {
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            ],
            "status": "completed"
        }
        
        return JSONResponse(content=a2a_response)
        
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/")
async def root():
    """Root endpoint - provides server information."""
    return {
        "name": "Python A2A Server",
        "version": "1.0.0",
        "agent": AGENT_CARD["name"],
        "agent_card_url": "/.well-known/agent.json",
        "message_endpoint": "/api/messages"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None
    }


if __name__ == "__main__":
    print("=" * 70)
    print("Python A2A Server - Starting")
    print("=" * 70)
    print("\nEndpoints:")
    print("  - Agent Card: http://localhost:8000/.well-known/agent.json")
    print("  - Messages:   http://localhost:8000/api/messages")
    print("  - Health:     http://localhost:8000/health")
    print("\nTo test with the A2A client:")
    print("  1. Set environment: $env:A2A_AGENT_HOST=\"http://localhost:8000\"")
    print("  2. Run client: python agent_with_a2a.py")
    print("\n" + "=" * 70 + "\n")
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
