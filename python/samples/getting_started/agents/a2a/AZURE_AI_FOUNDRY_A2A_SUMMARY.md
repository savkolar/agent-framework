# Azure AI Foundry Agents with A2A Protocol - Summary

## What I've Created

I've created a comprehensive example showing how to use **Azure AI Foundry persistent agents with the A2A (Agent-to-Agent) protocol**. This combines enterprise-grade agent management with standardized agent communication.

## Files Created

### 1. **azure_ai_foundry_a2a_server.py** ⭐ Main Server
A production-ready FastAPI server that:
- ✅ Creates **persistent agents** in Azure AI Foundry (visible in portal)
- ✅ Exposes agents via **A2A protocol** (/.well-known/agent.json)
- ✅ Includes **function tools** (weather, time)
- ✅ Handles A2A protocol messages at /api/messages
- ✅ Provides health checks and documentation endpoints
- ✅ Agent **survives server restarts** (persistent in Azure AI Foundry)

**Key Features:**
```python
# Creates persistent agent visible in portal
azure_ai_agent = await project_client.agents.create_agent(
    model=model_deployment,
    name="A2AWeatherTimeAssistant",
    instructions="You are a helpful assistant..."
)

# Exposes A2A agent card
@app.get("/.well-known/agent.json")
async def get_agent_card():
    return JSONResponse(content=AGENT_CARD)

# Handles A2A messages
@app.post("/api/messages")
async def handle_message(request: Request):
    # Process A2A message, run agent, return A2A response
    ...
```

### 2. **azure_ai_foundry_a2a_client.py** ⭐ Main Client
A comprehensive client that:
- ✅ Discovers agents via A2A protocol (agent card)
- ✅ Tests multiple queries (weather, time, combined, general)
- ✅ Demonstrates function tool usage through A2A
- ✅ Shows detailed output and documentation
- ✅ Provides troubleshooting information

**Test Scenarios:**
1. Weather query: "What's the weather in Seattle?"
2. Time query: "What's the current UTC time?"
3. Combined query: "What's the weather in London and the current time?"
4. General conversation: "Tell me a joke about programming"

### 3. **README_AZURE_AI_FOUNDRY_A2A.md** 📚 Complete Documentation
Comprehensive guide including:
- ✅ Architecture diagrams
- ✅ Quick start guide
- ✅ Setup instructions
- ✅ Key concepts explained
- ✅ Troubleshooting section
- ✅ Advanced scenarios
- ✅ Production deployment guidance

## How It Works

### Architecture Flow

```
┌─────────────────────────────────────────┐
│    Azure AI Foundry Portal              │
│    (Agent Management & Visibility)      │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│    A2A Server (FastAPI)                 │
│    • /.well-known/agent.json            │  ◄── Discovery
│    • /api/messages                      │  ◄── Communication
│                                          │
│    Azure AI Agent + Function Tools      │
│    • get_weather(location)              │
│    • get_time()                         │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│    A2A Client                           │
│    (Any framework supporting A2A)       │
└─────────────────────────────────────────┘
```

### Key Benefits

1. **Persistent Agents**: Agents remain in Azure AI Foundry portal
2. **Standardized Communication**: A2A protocol for interoperability
3. **Function Tools**: Extend agent capabilities (weather, time, etc.)
4. **Enterprise Management**: Central portal for agent lifecycle
5. **Reusability**: Same agent accessible by multiple clients

## Running the Example

### Quick Start (3 Steps)

**Step 1: Start the A2A Server**
```bash
cd python/samples/getting_started/agents/a2a
python azure_ai_foundry_a2a_server.py
```

Expected output:
```
======================================================================
Azure AI Foundry A2A Server
======================================================================
Initializing Azure AI Foundry persistent agent...
✓ Persistent agent created: 'A2AWeatherTimeAssistant' (ID: asst_xxx)
✓ Agent is visible in Azure AI Foundry portal
✓ Agent initialized with 2 function tools
✓ A2A server ready at http://localhost:8000
```

**Step 2: Verify Agent Card (Optional)**
```bash
# In browser or curl
curl http://localhost:8000/.well-known/agent.json
```

**Step 3: Run the Client**
```powershell
# In a NEW terminal
$env:A2A_AGENT_HOST="http://localhost:8000"
python azure_ai_foundry_a2a_client.py
```

Expected output:
```
======================================================================
Azure AI Foundry A2A Client
======================================================================

🔍 Step 1: Discovering agent via A2A protocol...
✓ Agent discovered: A2AWeatherTimeAssistant

🤖 Step 2: Creating A2A agent wrapper...
✓ A2A agent created: A2AWeatherTimeAssistant

======================================================================
Testing Azure AI Foundry Agent via A2A Protocol
======================================================================

📝 Query 1: Testing weather function tool
User: What's the weather like in Seattle?
🤖 Agent Response:
  The weather in Seattle is sunny with a high of 22°C.

📝 Query 2: Testing time function tool
User: What's the current UTC time?
🤖 Agent Response:
  The current UTC time is 2025-11-12 15:30:45.

... (more queries)

✅ Success! All queries completed
```

### View in Azure AI Foundry Portal

1. Go to https://ai.azure.com
2. Navigate to your project
3. Click "Agents" in left menu
4. See agent: **A2AWeatherTimeAssistant**
5. Agent persists even after server shutdown! ✨

## What Makes This Special

### 1. **Persistent Agents** vs Ephemeral
Most agent examples create temporary agents that disappear after execution. This example creates **persistent agents** that:
- ✅ Remain in Azure AI Foundry portal indefinitely
- ✅ Can be reused across multiple sessions
- ✅ Are manageable through the portal UI
- ✅ Support enterprise governance and monitoring

### 2. **A2A Protocol Compliance**
Implements full A2A protocol:
- ✅ Agent Card discovery (`/.well-known/agent.json`)
- ✅ Standard message format
- ✅ Interoperability with other A2A-compliant agents
- ✅ Cross-framework communication

### 3. **Function Tools via A2A**
Demonstrates function tools working through A2A:
- ✅ Client doesn't need to know about tools
- ✅ Agent automatically determines when to use tools
- ✅ Tool execution happens server-side
- ✅ Results seamlessly integrated into responses

### 4. **Production-Ready Pattern**
The code follows production best practices:
- ✅ Proper async context management
- ✅ Error handling and logging
- ✅ Health check endpoints
- ✅ Clean resource cleanup
- ✅ Environment-based configuration

## A2A Protocol Explained

### What is A2A?

**A2A (Agent-to-Agent)** is a standardized protocol for agent communication, like HTTP for web servers. It enables:
- Agents from different frameworks to communicate
- Standard discovery mechanism (agent cards)
- Interoperability across platforms

### Agent Card Example

```json
{
  "name": "A2AWeatherTimeAssistant",
  "description": "Azure AI Foundry persistent agent with tools",
  "capabilities": {
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

### Communication Flow

1. **Discovery**: Client fetches `/.well-known/agent.json`
2. **Message**: Client sends A2A-formatted message to `/api/messages`
3. **Processing**: Server forwards to Azure AI agent
4. **Tool Execution**: Agent uses function tools as needed
5. **Response**: Server returns A2A-formatted response

## Comparison: Different Approaches

| Feature | Simple A2A Server | **Azure AI Foundry + A2A** |
|---------|-------------------|---------------------------|
| Persistent Agent | ❌ No | ✅ Yes |
| Portal Visibility | ❌ No | ✅ Yes |
| A2A Protocol | ✅ Yes | ✅ Yes |
| Function Tools | ✅ Yes | ✅ Yes |
| Enterprise Management | ❌ No | ✅ Yes |
| Reusable Across Sessions | ❌ No | ✅ Yes |
| Production Ready | ⚠️ Basic | ✅ Full |

## Next Steps

### 1. **Try It Yourself**
```bash
# Start server (Terminal 1)
python azure_ai_foundry_a2a_server.py

# Run client (Terminal 2)
$env:A2A_AGENT_HOST="http://localhost:8000"
python azure_ai_foundry_a2a_client.py

# View agent in portal
# Visit: https://ai.azure.com → Your Project → Agents
```

### 2. **Customize Function Tools**
Add your own tools to the server:

```python
def get_stock_price(symbol: str) -> str:
    """Get current stock price."""
    # Your implementation
    return f"Stock {symbol}: $123.45"

# Add to agent
agent = ChatAgent(
    chat_client=AzureAIAgentClient(...),
    tools=[get_weather, get_time, get_stock_price]  # Add your tool
)
```

### 3. **Multi-Agent Orchestration**
Create multiple specialized agents:
- Weather agent on port 8000
- Stock agent on port 8001
- Orchestrator agent that delegates to both

### 4. **Deploy to Production**
- Host on Azure App Service or Container Apps
- Use HTTPS endpoints
- Add authentication middleware
- Implement rate limiting
- Set up monitoring

## Troubleshooting

### Can't connect to server
```bash
# Check if server is running
curl http://localhost:8000/health

# Check environment variable
echo $env:A2A_AGENT_HOST  # Should be http://localhost:8000
```

### Agent not in portal
```bash
# Verify Azure credentials
az login
az account show

# Check environment variables
echo $env:AZURE_AI_PROJECT_ENDPOINT
echo $env:AZURE_AI_MODEL_DEPLOYMENT_NAME
```

### Dependencies missing
```bash
# Install required packages
pip install fastapi uvicorn agent-framework[azure-ai] python-dotenv
```

## Resources

- **Documentation**: See `README_AZURE_AI_FOUNDRY_A2A.md` for full guide
- **A2A Specification**: https://a2a-protocol.org/latest/
- **Azure AI Foundry**: https://ai.azure.com
- **Server Code**: `azure_ai_foundry_a2a_server.py`
- **Client Code**: `azure_ai_foundry_a2a_client.py`

## Summary

You now have a complete, production-ready example of:
✅ **Azure AI Foundry persistent agents** (enterprise management)
✅ **A2A protocol** (standardized communication)
✅ **Function tools** (extensible capabilities)
✅ **Client-server architecture** (scalable deployment)

This pattern enables you to build enterprise-grade agent systems with:
- Central management in Azure AI Foundry
- Standardized communication via A2A
- Reusable, persistent agents
- Easy integration with other systems

**Happy building! 🚀**
