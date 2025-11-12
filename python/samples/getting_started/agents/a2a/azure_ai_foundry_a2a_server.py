# Copyright (c) Microsoft. All rights reserved.

"""
Azure AI Foundry Agent with A2A Protocol

This sample demonstrates how to expose an Azure AI Foundry persistent agent
via the A2A (Agent-to-Agent) protocol. This combines:
1. Azure AI Foundry persistent agents (visible in the portal)
2. A2A protocol for standardized agent communication

Architecture:
- Creates a persistent agent in Azure AI Foundry
- Exposes it via FastAPI with A2A protocol endpoints
- Agent remains visible and manageable in Azure AI Foundry portal

To run this server:
1. Configure your .env file with Azure AI credentials:
   - AZURE_AI_PROJECT_ENDPOINT
   - AZURE_AI_MODEL_DEPLOYMENT_NAME
2. Install dependencies: pip install fastapi uvicorn
3. Run: python azure_ai_foundry_a2a_server.py
4. Server starts at http://localhost:8000

To test with a client:
1. Set environment: $env:A2A_AGENT_HOST="http://localhost:8000"
2. Run client: python agent_with_a2a.py

Features:
- ✓ Persistent agent in Azure AI Foundry
- ✓ A2A protocol compliance (/.well-known/agent.json)
- ✓ Function tools (weather, time)
- ✓ Visible in Azure AI Foundry portal
- ✓ Reusable across sessions
"""

import asyncio
import os
from datetime import datetime, timezone
from random import randint
from typing import Annotated, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
from pydantic import Field

# Import agent framework components
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

load_dotenv()

app = FastAPI(title="Azure AI Foundry A2A Server")

# Global variables for agent and clients
agent = None
azure_ai_agent = None
project_client = None
credential = None


# Define function tools for the agent
def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


def get_time() -> str:
    """Get the current UTC time."""
    current_time = datetime.now(timezone.utc)
    return f"The current UTC time is {current_time.strftime('%Y-%m-%d %H:%M:%S')}."


async def initialize_agent():
    """
    Initialize the Azure AI Foundry persistent agent.
    This creates an agent that will be visible in the Azure AI Foundry portal.
    """
    global agent, azure_ai_agent, project_client, credential
    
    project_endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    model_deployment = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME")
    
    if not project_endpoint or not model_deployment:
        raise ValueError("AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME must be set")
    
    # Initialize Azure credentials and project client
    credential = DefaultAzureCredential()
    project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)
    
    # Create or retrieve persistent agent in Azure AI Foundry
    print("Initializing Azure AI Foundry persistent agent...")
    azure_ai_agent = await project_client.agents.create_agent(
        model=model_deployment,
        name="A2AWeatherTimeAssistant",
        instructions="You are a helpful assistant that can provide weather and time information via A2A protocol.",
    )
    
    print(f"✓ Persistent agent created: '{azure_ai_agent.name}' (ID: {azure_ai_agent.id})")
    print(f"✓ Agent is visible in Azure AI Foundry portal")
    
    # Create ChatAgent wrapper with function tools
    agent = ChatAgent(
        chat_client=AzureAIAgentClient(
            project_client=project_client,
            agent_id=azure_ai_agent.id,
            async_credential=credential
        ),
        tools=[get_weather, get_time],
        name=azure_ai_agent.name,
    )
    
    print(f"✓ Agent initialized with {len(agent.tools)} function tools")
    print(f"✓ A2A server ready at http://localhost:8000")


# Agent Card - A2A protocol discovery endpoint
AGENT_CARD = {
    "name": "A2AWeatherTimeAssistant",
    "description": "Azure AI Foundry persistent agent that provides weather and time information via A2A protocol",
    "version": "1.0.0",
    "id": "azure-ai-foundry-a2a-001",
    "capabilities": {
        "streaming": False,
        "sync": True,
        "async": True,
        "tools": ["get_weather", "get_time"]
    },
    "endpoints": {
        "message": {
            "path": "/api/messages",
            "method": "POST",
            "description": "Send messages to the Azure AI Foundry agent"
        }
    },
    "model": {
        "name": "Azure AI Agent",
        "provider": "Azure AI Foundry",
        "backend": "Azure OpenAI"
    },
    "metadata": {
        "framework": "Microsoft Agent Framework",
        "persistent": True,
        "portal_visible": True
    }
}


@app.on_event("startup")
async def startup_event():
    """Initialize the Azure AI Foundry agent on server startup."""
    try:
        await initialize_agent()
    except Exception as e:
        print(f"✗ Failed to initialize agent: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown (but keep agent in Azure AI Foundry)."""
    global project_client, credential
    
    if project_client:
        await project_client.close()
    if credential:
        await credential.close()
    
    print(f"\n✓ Server shut down")
    print(f"✓ Agent '{azure_ai_agent.name}' remains in Azure AI Foundry portal")


@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "service": "Azure AI Foundry A2A Server",
        "status": "running",
        "agent": {
            "name": azure_ai_agent.name if azure_ai_agent else "Not initialized",
            "id": azure_ai_agent.id if azure_ai_agent else None,
            "persistent": True,
            "portal_url": f"{os.environ.get('AZURE_AI_PROJECT_ENDPOINT')}/agents" if azure_ai_agent else None
        },
        "endpoints": {
            "agent_card": "/.well-known/agent.json",
            "messages": "/api/messages",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "agent_id": azure_ai_agent.id if azure_ai_agent else None
    }


@app.get("/.well-known/agent.json")
async def get_agent_card():
    """
    A2A protocol discovery endpoint.
    Returns the agent card describing the agent's capabilities and endpoints.
    This is the standard A2A protocol endpoint for agent discovery.
    """
    print("📋 Agent card requested via A2A discovery")
    return JSONResponse(content=AGENT_CARD)


@app.post("/api/messages")
async def handle_message(request: Request):
    """
    A2A protocol message endpoint.
    Handles incoming messages and returns agent responses in A2A format.
    
    Expected A2A message format:
    {
        "messages": [
            {"role": "user", "content": "What's the weather in Seattle?"}
        ]
    }
    
    Returns A2A response format:
    {
        "messages": [
            {"role": "assistant", "content": "The weather in Seattle is..."}
        ],
        "metadata": {...}
    }
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Parse incoming A2A message
        body = await request.json()
        print(f"\n📨 Received A2A message: {body}")
        
        # Extract messages from A2A format
        messages = body.get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="No messages in request")
        
        # Get the latest user message
        user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")
        
        print(f"💬 User query: {user_message}")
        
        # Run the Azure AI Foundry agent
        print(f"🤖 Running Azure AI Foundry agent '{azure_ai_agent.name}'...")
        result = await agent.run(user_message)
        
        # Extract the response text
        response_text = ""
        for message in result.messages:
            if hasattr(message, 'text'):
                response_text += message.text
        
        print(f"✓ Agent response generated")
        
        # Return A2A-formatted response
        a2a_response = {
            "messages": [
                {
                    "role": "assistant",
                    "content": response_text
                }
            ],
            "metadata": {
                "agent_id": azure_ai_agent.id,
                "agent_name": azure_ai_agent.name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "protocol": "A2A",
                "source": "Azure AI Foundry"
            }
        }
        
        return JSONResponse(content=a2a_response)
        
    except Exception as e:
        print(f"✗ Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("=" * 70)
    print("Azure AI Foundry A2A Server")
    print("=" * 70)
    print("\nThis server exposes Azure AI Foundry persistent agents via A2A protocol")
    print("\nFeatures:")
    print("  • Persistent agents (visible in Azure AI Foundry portal)")
    print("  • A2A protocol compliance")
    print("  • Function tools (weather, time)")
    print("  • Reusable across sessions")
    print("\nEndpoints:")
    print("  • /.well-known/agent.json - Agent card discovery")
    print("  • /api/messages - A2A message handling")
    print("  • /health - Health check")
    print("\nStarting server...")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
