# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agent_framework import ChatAgent, MCPStreamableHTTPTool
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

"""
Azure AI Agent with Local MCP Example (Persistent Version)

This sample demonstrates integration of Azure AI Agents with local Model Context Protocol (MCP)
servers, showing both agent-level and run-level tool configuration patterns.
This version creates PERSISTENT agents that will be visible in Azure AI Foundry portal.
"""


async def mcp_tools_on_run_level() -> None:
    """Example showing MCP tools defined when running the agent."""
    print("=== Tools Defined on Run Level (Persistent) ===")

    project_endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model_deployment = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

    # Tools are provided when running the agent
    # This means we have to ensure we connect to the MCP server before running the agent
    # and pass the tools to the run method.
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        MCPStreamableHTTPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
        ) as mcp_server,
    ):
        # Create a persistent agent in Azure AI Foundry
        print("Creating persistent agent in Azure AI Foundry...")
        azure_ai_agent = await project_client.agents.create_agent(
            model=model_deployment,
            name="DocsAgent-RunLevel",
            instructions="You are a helpful assistant that can help with microsoft documentation questions.",
        )
        print(f"✓ Agent created with ID: {azure_ai_agent.id}\n")

        try:
            async with ChatAgent(
                chat_client=AzureAIAgentClient(
                    project_client=project_client,
                    agent_id=azure_ai_agent.id,
                    async_credential=credential
                ),
                name="DocsAgent",
                instructions="You are a helpful assistant that can help with microsoft documentation questions.",
            ) as agent:
                # First query
                query1 = "How to create an Azure storage account using az cli?"
                print(f"User: {query1}")
                result1 = await agent.run(query1, tools=mcp_server)
                print(f"{agent.name}: {result1}\n")
                print("\n=======================================\n")
                # Second query
                query2 = "What is Microsoft Agent Framework?"
                print(f"User: {query2}")
                result2 = await agent.run(query2, tools=mcp_server)
                print(f"{agent.name}: {result2}\n")
        finally:
            # Keep agent alive in Azure AI Foundry
            print(f"✓ Agent '{azure_ai_agent.name}' (ID: {azure_ai_agent.id}) will remain in Azure AI Foundry\n")


async def mcp_tools_on_agent_level() -> None:
    """Example showing tools defined when creating the agent."""
    print("=== Tools Defined on Agent Level (Persistent) ===")

    project_endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model_deployment = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    # The agent will connect to the MCP server through its context manager.
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
    ):
        # Create a persistent agent in Azure AI Foundry
        print("Creating persistent agent in Azure AI Foundry...")
        azure_ai_agent = await project_client.agents.create_agent(
            model=model_deployment,
            name="DocsAgent-AgentLevel",
            instructions="You are a helpful assistant that can help with microsoft documentation questions.",
        )
        print(f"✓ Agent created with ID: {azure_ai_agent.id}\n")

        try:
            async with AzureAIAgentClient(
                project_client=project_client,
                agent_id=azure_ai_agent.id,
                async_credential=credential
            ).create_agent(
                name="DocsAgent",
                instructions="You are a helpful assistant that can help with microsoft documentation questions.",
                tools=MCPStreamableHTTPTool(  # Tools defined at agent creation
                    name="Microsoft Learn MCP",
                    url="https://learn.microsoft.com/api/mcp",
                ),
            ) as agent:
                # First query
                query1 = "How to create an Azure storage account using az cli?"
                print(f"User: {query1}")
                result1 = await agent.run(query1)
                print(f"{agent.name}: {result1}\n")
                print("\n=======================================\n")
                # Second query
                query2 = "What is Microsoft Agent Framework?"
                print(f"User: {query2}")
                result2 = await agent.run(query2)
                print(f"{agent.name}: {result2}\n")
        finally:
            # Keep agent alive in Azure AI Foundry
            print(f"✓ Agent '{azure_ai_agent.name}' (ID: {azure_ai_agent.id}) will remain in Azure AI Foundry\n")


async def main() -> None:
    print("=== Azure AI Chat Client Agent with MCP Tools Examples (Persistent) ===\n")
    print("These agents will be created in Azure AI Foundry and visible in the portal.\n")
    print(f"View agents at: {os.environ['AZURE_AI_PROJECT_ENDPOINT'].replace('/api/projects/', '/projects/')}\n")

    await mcp_tools_on_agent_level()
    await mcp_tools_on_run_level()

    print("All persistent agents have been created, tested, and cleaned up.")


if __name__ == "__main__":
    asyncio.run(main())
