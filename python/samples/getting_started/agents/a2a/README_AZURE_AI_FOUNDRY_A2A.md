# Azure AI Foundry Agents with A2A Protocol

This directory demonstrates how to use **Azure AI Foundry persistent agents** with the **A2A (Agent-to-Agent) protocol** for standardized agent communication.

## Overview

This integration combines:
- **Azure AI Foundry**: Enterprise-grade agent management and deployment
- **Persistent Agents**: Agents that remain visible in the Azure AI Foundry portal
- **A2A Protocol**: Standardized communication protocol for agent interoperability

## What is A2A Protocol?

The **Agent-to-Agent (A2A) protocol** is a standardized communication protocol that enables different agent systems to communicate seamlessly. Key features:

- **Discovery**: Agents expose their capabilities via `/.well-known/agent.json` (Agent Card)
- **Interoperability**: Agents from different frameworks can communicate
- **Standardization**: Common message format across platforms
- **Protocol Specification**: https://a2a-protocol.org/latest/

## Architecture

```
┌─────────────────────────────────────────┐
│    Azure AI Foundry Portal              │
│    (Persistent Agent Management)        │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│    A2A Server (FastAPI)                 │
│    ┌─────────────────────────────────┐  │
│    │  /.well-known/agent.json        │  │  ◄── Agent Discovery
│    │  (Agent Card)                   │  │
│    └─────────────────────────────────┘  │
│    ┌─────────────────────────────────┐  │
│    │  /api/messages                  │  │  ◄── A2A Messages
│    │  (A2A Protocol Endpoint)        │  │
│    └─────────────────────────────────┘  │
│                  │                       │
│                  ▼                       │
│    ┌─────────────────────────────────┐  │
│    │  Azure AI Agent                 │  │
│    │  • Function Tools               │  │
│    │  • Persistent in Portal         │  │
│    └─────────────────────────────────┘  │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│    A2A Client                           │
│    (Any framework supporting A2A)       │
└─────────────────────────────────────────┘
```

## Files in this Directory

### Server Examples

1. **`azure_ai_foundry_a2a_server.py`** - **Recommended**
   - Exposes Azure AI Foundry persistent agents via A2A protocol
   - Agents remain visible in Azure AI Foundry portal
   - Includes function tools (weather, time)
   - Full A2A protocol compliance

2. **`a2a_server_simple.py`**
   - Simple A2A server using Azure OpenAI directly
   - Good for learning A2A basics
   - No persistent agent management

### Client Examples

1. **`azure_ai_foundry_a2a_client.py`** - **Recommended**
   - Comprehensive client for Azure AI Foundry A2A server
   - Tests multiple queries and function tools
   - Detailed output and documentation

2. **`agent_with_a2a.py`**
   - Basic A2A client example
   - Good for learning A2A client basics

## Prerequisites

### 1. Azure Setup

You need an Azure AI Foundry project with:
- Azure OpenAI deployment
- Azure AI Project endpoint
- Proper authentication configured

### 2. Environment Variables

Create a `.env` file in the `azure_ai` directory:

```bash
# Azure AI Foundry settings
AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o

# Azure OpenAI settings (for simple server)
AZURE_OPENAI_ENDPOINT=https://your-aoai.cognitiveservices.azure.com
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o
```

### 3. Install Dependencies

```bash
# Activate your virtual environment
.venv\Scripts\Activate.ps1  # Windows PowerShell
source .venv/bin/activate    # Linux/Mac

# Install required packages
pip install fastapi uvicorn agent-framework[azure-ai] python-dotenv
```

## Quick Start Guide

### Option 1: Azure AI Foundry with A2A (Recommended)

This approach creates persistent agents visible in Azure AI Foundry portal.

#### Step 1: Start the A2A Server

```bash
# Navigate to the a2a directory
cd python/samples/getting_started/agents/a2a

# Run the Azure AI Foundry A2A server
python azure_ai_foundry_a2a_server.py
```

You should see:
```
======================================================================
Azure AI Foundry A2A Server
======================================================================
...
Initializing Azure AI Foundry persistent agent...
✓ Persistent agent created: 'A2AWeatherTimeAssistant' (ID: asst_xxx)
✓ Agent is visible in Azure AI Foundry portal
✓ Agent initialized with 2 function tools
✓ A2A server ready at http://localhost:8000
...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### Step 2: Test the Agent Card (Discovery)

In a browser or with curl:
```bash
curl http://localhost:8000/.well-known/agent.json
```

You should see the agent card JSON with capabilities and endpoints.

#### Step 3: Run the A2A Client

Open a **new terminal** and run:

```powershell
# Set the A2A agent host
$env:A2A_AGENT_HOST="http://localhost:8000"

# Run the client
python azure_ai_foundry_a2a_client.py
```

Expected output:
```
======================================================================
Azure AI Foundry A2A Client
======================================================================

📡 Connecting to A2A agent at: http://localhost:8000

🔍 Step 1: Discovering agent via A2A protocol...
✓ Agent discovered: A2AWeatherTimeAssistant
  Description: Azure AI Foundry persistent agent...

🤖 Step 2: Creating A2A agent wrapper...
✓ A2A agent created: A2AWeatherTimeAssistant

======================================================================
Testing Azure AI Foundry Agent via A2A Protocol
======================================================================

📝 Query 1: Testing weather function tool
----------------------------------------------------------------------
User: What's the weather like in Seattle?
⏳ Sending to Azure AI Foundry agent...

🤖 Agent Response:
  The weather in Seattle is sunny with a high of 22°C.

📝 Query 2: Testing time function tool
----------------------------------------------------------------------
User: What's the current UTC time?
⏳ Sending to Azure AI Foundry agent...

🤖 Agent Response:
  The current UTC time is 2025-11-12 15:30:45.

...
```

#### Step 4: View Agent in Azure AI Foundry Portal

1. Go to https://ai.azure.com
2. Navigate to your project
3. Click on "Agents" in the left menu
4. You'll see the agent: **A2AWeatherTimeAssistant**
5. Click on it to view details, runs, and configuration

The agent **remains visible even after the server shuts down**.

### Option 2: Simple A2A Server (Learning)

For learning A2A basics without persistent agents:

```bash
# Start simple server
python a2a_server_simple.py

# In new terminal, set host and run client
$env:A2A_AGENT_HOST="http://localhost:8000"
python agent_with_a2a.py
```

## Key Concepts

### 1. Persistent vs Ephemeral Agents

**Persistent Agents** (Azure AI Foundry):
- ✓ Visible in Azure AI Foundry portal
- ✓ Reusable across sessions
- ✓ Managed through portal UI
- ✓ Created with `project_client.agents.create_agent()`

**Ephemeral Agents** (Simple):
- ✗ Not visible in portal
- ✗ Exist only during runtime
- ✗ No central management
- Created directly with chat clients

### 2. A2A Protocol Components

#### Agent Card (`/.well-known/agent.json`)
```json
{
  "name": "A2AWeatherTimeAssistant",
  "description": "Agent description",
  "capabilities": {
    "streaming": false,
    "tools": ["get_weather", "get_time"]
  },
  "endpoints": {
    "message": {
      "path": "/api/messages",
      "method": "POST"
    }
  }
}
```

#### A2A Message Format
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What's the weather in Seattle?"
    }
  ]
}
```

#### A2A Response Format
```json
{
  "messages": [
    {
      "role": "assistant",
      "content": "The weather in Seattle is sunny..."
    }
  ],
  "metadata": {
    "agent_id": "asst_xxx",
    "timestamp": "2025-11-12T15:30:45Z"
  }
}
```

### 3. Function Tools with A2A

The server demonstrates function tools working through A2A:

```python
def get_weather(location: str) -> str:
    """Get the weather for a given location."""
    return f"The weather in {location} is..."

def get_time() -> str:
    """Get the current UTC time."""
    return f"The current UTC time is..."

# Tools are registered with the agent
agent = ChatAgent(
    chat_client=AzureAIAgentClient(...),
    tools=[get_weather, get_time]
)
```

When a client sends "What's the weather in Seattle?":
1. Client sends A2A message to server
2. Server forwards to Azure AI Foundry agent
3. Agent recognizes need for `get_weather` tool
4. Tool executes and returns data
5. Agent formulates response
6. Server returns A2A-formatted response to client

## Benefits of Azure AI Foundry + A2A

### 1. **Enterprise Management**
- Centralized agent management in Azure AI Foundry portal
- Version control and deployment tracking
- Usage monitoring and analytics

### 2. **Standardized Communication**
- A2A protocol enables interoperability
- Agents can communicate across frameworks
- Standard discovery via agent cards

### 3. **Persistent Agents**
- Agents survive server restarts
- Reusable across multiple applications
- Shared across teams

### 4. **Function Tools**
- Extend agent capabilities with custom tools
- Tools work seamlessly through A2A protocol
- Easy to add new capabilities

### 5. **Scalability**
- Azure-backed infrastructure
- Load balancing and high availability
- Global distribution

## Troubleshooting

### Connection Refused
**Problem**: `Connection refused` when running client

**Solutions**:
1. Ensure server is running: `python azure_ai_foundry_a2a_server.py`
2. Verify server URL: `$env:A2A_AGENT_HOST="http://localhost:8000"`
3. Check firewall settings
4. Try `http://127.0.0.1:8000` instead

### Agent Not Initialized
**Problem**: "Agent not initialized" error

**Solutions**:
1. Check environment variables in `.env` file
2. Verify Azure credentials: `az login`
3. Ensure Azure AI project endpoint is correct
4. Check server startup logs for initialization errors

### 404 on Agent Card
**Problem**: `/.well-known/agent.json` returns 404

**Solutions**:
1. Verify server is running
2. Check URL: `http://localhost:8000/.well-known/agent.json`
3. Review server logs for errors

### Authentication Errors
**Problem**: Azure authentication failures

**Solutions**:
1. Run `az login` to authenticate
2. Check Azure credentials: `az account show`
3. Verify subscription and project access
4. Use `DefaultAzureCredential` which tries multiple auth methods

## Advanced Scenarios

### Multiple Agents with A2A

Run multiple A2A servers on different ports:

```bash
# Server 1 (Weather agent)
PORT=8000 python azure_ai_foundry_a2a_server.py

# Server 2 (Time agent)
PORT=8001 python azure_ai_foundry_a2a_server.py
```

Client can connect to either:
```bash
$env:A2A_AGENT_HOST="http://localhost:8000"  # Weather
$env:A2A_AGENT_HOST="http://localhost:8001"  # Time
```

### Agent Orchestration

Create an orchestrator agent that delegates to multiple A2A agents:

```python
# Orchestrator connects to multiple A2A agents
weather_agent = A2AAgent(..., url="http://localhost:8000")
time_agent = A2AAgent(..., url="http://localhost:8001")

# Route queries based on intent
if "weather" in query:
    response = await weather_agent.run(query)
elif "time" in query:
    response = await time_agent.run(query)
```

### Production Deployment

For production use:
1. Deploy A2A server to Azure App Service or Container Apps
2. Use HTTPS endpoints
3. Add authentication/authorization middleware
4. Implement rate limiting
5. Add monitoring and logging
6. Use production-grade WSGI/ASGI server

Example production config:
```bash
gunicorn -k uvicorn.workers.UvicornWorker \
  -w 4 \
  -b 0.0.0.0:443 \
  --certfile=/path/to/cert.pem \
  --keyfile=/path/to/key.pem \
  azure_ai_foundry_a2a_server:app
```

## Resources

- **A2A Protocol Specification**: https://a2a-protocol.org/latest/
- **Azure AI Foundry**: https://ai.azure.com
- **Agent Framework Documentation**: [Repository README](../../../../../README.md)
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Azure OpenAI**: https://learn.microsoft.com/azure/ai-services/openai/

## Next Steps

1. ✅ Run the Quick Start guide above
2. ✅ View your agent in Azure AI Foundry portal
3. ✅ Test different queries with function tools
4. ✅ Explore the server and client code
5. ✅ Try creating your own custom function tools
6. ✅ Deploy to Azure for production use
7. ✅ Build agent orchestration patterns

## Support

For issues or questions:
- Review the troubleshooting section above
- Check the main repository README
- Open an issue on GitHub
- Consult Azure AI documentation

---

**Happy Agent Building! 🤖**
