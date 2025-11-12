# Copyright (c) Microsoft. All rights reserved.
from dotenv import load_dotenv
load_dotenv()

import asyncio
import os
from datetime import datetime, timezone
from random import randint
from typing import Annotated

from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from pydantic import Field

"""
Create a Persistent Agent in Azure AI Foundry (Keep Alive)

This script creates a persistent agent that will remain visible in Azure AI Foundry
until you manually delete it. Run this script to create the agent, then check the portal.
"""


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


async def main() -> None:
    project_endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model_deployment = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]
    
    # Portal URL for viewing agents
    portal_url = project_endpoint.replace('/api/projects/', '/projects/')
    
    print("=== Creating Persistent Agent in Azure AI Foundry ===\n")
    print(f"Portal URL: {portal_url}\n")

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
    ):
        # Create a persistent agent in Azure AI Foundry
        print("Creating persistent agent...")
        azure_ai_agent = await project_client.agents.create_agent(
            model=model_deployment,
            name="TestPersistentAgent",
            instructions="You are a helpful assistant that can provide weather and time information.",
        )
        print(f"✓ Agent created with ID: {azure_ai_agent.id}\n")
        print(f"✓ Agent name: {azure_ai_agent.name}\n")
        print(f"✓ Model: {azure_ai_agent.model}\n")
        
        # Test the agent with a simple query
        print("Testing the agent...")
        async with ChatAgent(
            chat_client=AzureAIAgentClient(
                project_client=project_client,
                agent_id=azure_ai_agent.id,
                async_credential=credential
            ),
            tools=[get_weather, get_time],
        ) as agent:
            query = "What's the weather like in Seattle?"
            print(f"\nUser: {query}")
            result = await agent.run(query)
            print(f"Agent: {result}\n")
        
        print("=" * 70)
        print("AGENT HAS BEEN CREATED AND WILL REMAIN IN AZURE AI FOUNDRY")
        print("=" * 70)
        print(f"\nAgent ID: {azure_ai_agent.id}")
        print(f"Agent Name: TestPersistentAgent")
        print(f"\nView in portal: {portal_url}")
        print("\nThe agent will persist until you manually delete it.")
        print("To delete the agent, you can either:")
        print("  1. Delete it from the Azure AI Foundry portal")
        print("  2. Run the delete script (if provided)")
        print(f"  3. Use Azure CLI: az ml agent delete --id {azure_ai_agent.id}")
        

if __name__ == "__main__":
    asyncio.run(main())
