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
Azure AI Agent with Function Tools Example (Persistent Version)

This sample demonstrates creating PERSISTENT agents in Azure AI Foundry that
will be visible in the portal and can be reused across sessions.
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


async def tools_on_agent_level() -> None:
    """Example showing tools defined when creating the agent - creates persistent agent."""
    print("=== Tools Defined on Agent Level (Persistent) ===")

    project_endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model_deployment = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
    ):
        # Create a persistent agent in Azure AI Foundry
        print("Creating persistent agent in Azure AI Foundry...")
        azure_ai_agent = await project_client.agents.create_agent(
            model=model_deployment,
            name="WeatherTimeAssistant",
            instructions="You are a helpful assistant that can provide weather and time information.",
        )
        print(f"✓ Agent created with ID: {azure_ai_agent.id}\n")

        try:
            async with ChatAgent(
                chat_client=AzureAIAgentClient(
                    project_client=project_client,
                    agent_id=azure_ai_agent.id,
                    async_credential=credential
                ),
                tools=[get_weather, get_time],  # Tools defined at agent creation
            ) as agent:
                # First query - agent can use weather tool
                query1 = "What's the weather like in New York?"
                print(f"User: {query1}")
                result1 = await agent.run(query1)
                print(f"Agent: {result1}\n")

                # Second query - agent can use time tool
                query2 = "What's the current UTC time?"
                print(f"User: {query2}")
                result2 = await agent.run(query2)
                print(f"Agent: {result2}\n")

                # Third query - agent can use both tools if needed
                query3 = "What's the weather in London and what's the current UTC time?"
                print(f"User: {query3}")
                result3 = await agent.run(query3)
                print(f"Agent: {result3}\n")
        finally:
            # Keep agent alive in Azure AI Foundry
            print(f"✓ Agent '{azure_ai_agent.name}' (ID: {azure_ai_agent.id}) will remain in Azure AI Foundry\n")


async def tools_on_run_level() -> None:
    """Example showing tools passed to the run method - creates persistent agent."""
    print("=== Tools Passed to Run Method (Persistent) ===")

    project_endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model_deployment = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
    ):
        # Create a persistent agent in Azure AI Foundry
        print("Creating persistent agent in Azure AI Foundry...")
        azure_ai_agent = await project_client.agents.create_agent(
            model=model_deployment,
            name="FlexibleAssistant",
            instructions="You are a helpful assistant.",
        )
        print(f"✓ Agent created with ID: {azure_ai_agent.id}\n")

        try:
            async with ChatAgent(
                chat_client=AzureAIAgentClient(
                    project_client=project_client,
                    agent_id=azure_ai_agent.id,
                    async_credential=credential
                ),
            ) as agent:
                # First query with weather tool
                query1 = "What's the weather like in Seattle?"
                print(f"User: {query1}")
                result1 = await agent.run(query1, tools=[get_weather])  # Tool passed to run method
                print(f"Agent: {result1}\n")

                # Second query with time tool
                query2 = "What's the current UTC time?"
                print(f"User: {query2}")
                result2 = await agent.run(query2, tools=[get_time])  # Different tool for this query
                print(f"Agent: {result2}\n")

                # Third query with multiple tools
                query3 = "What's the weather in Chicago and what's the current UTC time?"
                print(f"User: {query3}")
                result3 = await agent.run(query3, tools=[get_weather, get_time])  # Multiple tools
                print(f"Agent: {result3}\n")
        finally:
            # Keep agent alive in Azure AI Foundry
            print(f"✓ Agent '{azure_ai_agent.name}' (ID: {azure_ai_agent.id}) will remain in Azure AI Foundry\n")


async def mixed_tools_example() -> None:
    """Example showing both agent-level tools and run-method tools - creates persistent agent."""
    print("=== Mixed Tools Example (Persistent) ===")

    project_endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model_deployment = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
    ):
        # Create a persistent agent in Azure AI Foundry
        print("Creating persistent agent in Azure AI Foundry...")
        azure_ai_agent = await project_client.agents.create_agent(
            model=model_deployment,
            name="ComprehensiveAssistant",
            instructions="You are a comprehensive assistant that can help with various information requests.",
        )
        print(f"✓ Agent created with ID: {azure_ai_agent.id}\n")

        try:
            async with ChatAgent(
                chat_client=AzureAIAgentClient(
                    project_client=project_client,
                    agent_id=azure_ai_agent.id,
                    async_credential=credential
                ),
                tools=[get_weather],  # Base tool available for all queries
            ) as agent:
                # Query using both agent tool and additional run-method tools
                query = "What's the weather in Denver and what's the current UTC time?"
                print(f"User: {query}")

                # Agent has access to get_weather (from creation) + additional tools from run method
                result = await agent.run(
                    query,
                    tools=[get_time],  # Additional tools for this specific query
                )
                print(f"Agent: {result}\n")
        finally:
            # Keep agent alive in Azure AI Foundry
            print(f"✓ Agent '{azure_ai_agent.name}' (ID: {azure_ai_agent.id}) will remain in Azure AI Foundry\n")


async def main() -> None:
    print("=== Azure AI Persistent Agents with Function Tools Examples ===\n")
    print("These agents will be created in Azure AI Foundry and visible in the portal.\n")
    print(f"View agents at: {os.environ['AZURE_AI_PROJECT_ENDPOINT'].replace('/api/projects/', '/projects/')}\n")

    await tools_on_agent_level()
    await tools_on_run_level()
    await mixed_tools_example()

    print("All persistent agents have been created, tested, and cleaned up.")


if __name__ == "__main__":
    asyncio.run(main())
