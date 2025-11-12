# Copyright (c) Microsoft. All rights reserved.

"""
Azure AI Foundry A2A Client

This client demonstrates how to connect to an Azure AI Foundry persistent agent
exposed via the A2A (Agent-to-Agent) protocol.

This example shows:
1. How to discover an agent via its A2A agent card (/.well-known/agent.json)
2. How to communicate with an Azure AI Foundry agent using A2A protocol
3. How to use function tools (weather, time) through A2A communication
4. How the agent remains persistent in Azure AI Foundry portal

To run this client:
1. Start the A2A server first:
   python azure_ai_foundry_a2a_server.py

2. In a new terminal, set the A2A agent host:
   $env:A2A_AGENT_HOST="http://localhost:8000"

3. Run this client:
   python azure_ai_foundry_a2a_client.py

What happens:
- Client discovers the Azure AI Foundry agent via A2A protocol
- Sends queries that trigger function tools (weather, time)
- Receives responses from the persistent Azure AI Foundry agent
- Agent remains visible in Azure AI Foundry portal throughout
"""

import asyncio
import os
from datetime import datetime

import httpx
from a2a.client import A2ACardResolver
from agent_framework.a2a import A2AAgent


async def demonstrate_azure_ai_foundry_a2a():
    """
    Demonstrates connecting to and using an Azure AI Foundry persistent agent
    via the A2A protocol.
    """
    # Get A2A agent host from environment
    a2a_agent_host = os.getenv("A2A_AGENT_HOST")
    if not a2a_agent_host:
        raise ValueError(
            "A2A_AGENT_HOST environment variable is not set.\n"
            "Set it to your A2A server URL, e.g.:\n"
            "  $env:A2A_AGENT_HOST=\"http://localhost:8000\""
        )

    print("=" * 70)
    print("Azure AI Foundry A2A Client")
    print("=" * 70)
    print(f"\n📡 Connecting to A2A agent at: {a2a_agent_host}")
    
    try:
        # Initialize HTTP client with proper timeout
        async with httpx.AsyncClient(timeout=120.0) as http_client:
            # Step 1: Discover the agent via A2A protocol
            print("\n🔍 Step 1: Discovering agent via A2A protocol...")
            resolver = A2ACardResolver(httpx_client=http_client, base_url=a2a_agent_host)
            
            # Fetch the agent card from /.well-known/agent.json
            agent_card = await resolver.get_agent_card(relative_card_path="/.well-known/agent.json")
            
            print(f"✓ Agent discovered: {agent_card.name}")
            print(f"  Description: {agent_card.description}")
            print(f"  Capabilities: {agent_card.capabilities if hasattr(agent_card, 'capabilities') else 'N/A'}")
            
            # Step 2: Create A2AAgent instance
            print("\n🤖 Step 2: Creating A2A agent wrapper...")
            agent = A2AAgent(
                name=agent_card.name,
                description=agent_card.description,
                agent_card=agent_card,
                url=a2a_agent_host,
            )
            print(f"✓ A2A agent created: {agent.name}")
            
            # Step 3: Test queries that use function tools
            print("\n" + "=" * 70)
            print("Testing Azure AI Foundry Agent via A2A Protocol")
            print("=" * 70)
            
            # Query 1: Weather tool
            print("\n📝 Query 1: Testing weather function tool")
            print("-" * 70)
            query1 = "What's the weather like in Seattle?"
            print(f"User: {query1}")
            print("⏳ Sending to Azure AI Foundry agent...")
            
            response1 = await agent.run(query1)
            print(f"\n🤖 Agent Response:")
            for message in response1.messages:
                print(f"  {message.text}")
            
            # Query 2: Time tool
            print("\n📝 Query 2: Testing time function tool")
            print("-" * 70)
            query2 = "What's the current UTC time?"
            print(f"User: {query2}")
            print("⏳ Sending to Azure AI Foundry agent...")
            
            response2 = await agent.run(query2)
            print(f"\n🤖 Agent Response:")
            for message in response2.messages:
                print(f"  {message.text}")
            
            # Query 3: Multiple tools
            print("\n📝 Query 3: Testing multiple function tools")
            print("-" * 70)
            query3 = "What's the weather in London and what's the current UTC time?"
            print(f"User: {query3}")
            print("⏳ Sending to Azure AI Foundry agent...")
            
            response3 = await agent.run(query3)
            print(f"\n🤖 Agent Response:")
            for message in response3.messages:
                print(f"  {message.text}")
            
            # Query 4: General conversation
            print("\n📝 Query 4: Testing general conversation")
            print("-" * 70)
            query4 = "Tell me a joke about programming"
            print(f"User: {query4}")
            print("⏳ Sending to Azure AI Foundry agent...")
            
            response4 = await agent.run(query4)
            print(f"\n🤖 Agent Response:")
            for message in response4.messages:
                print(f"  {message.text}")
            
            # Summary
            print("\n" + "=" * 70)
            print("✅ Success! All queries completed")
            print("=" * 70)
            print("\n📊 Summary:")
            print(f"  • Connected to: {a2a_agent_host}")
            print(f"  • Agent: {agent_card.name}")
            print(f"  • Protocol: A2A (Agent-to-Agent)")
            print(f"  • Backend: Azure AI Foundry")
            print(f"  • Queries: 4 (weather, time, combined, general)")
            print(f"  • Agent Status: Persistent (visible in Azure AI Foundry portal)")
            
            # Portal information
            if "AZURE_AI_PROJECT_ENDPOINT" in os.environ:
                portal_url = f"{os.environ['AZURE_AI_PROJECT_ENDPOINT']}/agents"
                print(f"\n🌐 View agent in Azure AI Foundry portal:")
                print(f"  {portal_url}")
            
            print("\n💡 Key Points:")
            print("  • Agent is persistent and reusable across sessions")
            print("  • Function tools (weather, time) work through A2A protocol")
            print("  • Same agent can be accessed by multiple clients")
            print("  • Agent remains in Azure AI Foundry portal after server shutdown")
            print("=" * 70)
            
    except httpx.ConnectError:
        print(f"\n✗ Connection failed: Unable to connect to {a2a_agent_host}")
        print("\nTroubleshooting:")
        print("  1. Ensure the A2A server is running:")
        print("     python azure_ai_foundry_a2a_server.py")
        print(f"  2. Verify the server is accessible at {a2a_agent_host}")
        print("  3. Check firewall and network settings")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main entry point."""
    await demonstrate_azure_ai_foundry_a2a()


if __name__ == "__main__":
    asyncio.run(main())
