# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from datetime import datetime, timezone
from typing import Any
from dotenv import load_dotenv
load_dotenv()

from agent_framework import (
    AgentProtocol,
    AgentThread,
    HostedMCPTool,
    HostedWebSearchTool,
)
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

"""
Azure AI Agent with Multiple Tools Example (Persistent Version)

This sample demonstrates integrating multiple tools (MCP and Web Search) with Azure AI Agents,
including user approval workflows for function call security.
This version creates PERSISTENT agents that will be visible in Azure AI Foundry portal.

Prerequisites:
1. Set AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME environment variables
2. For Bing search functionality, set BING_CONNECTION_ID environment variable to your Bing connection ID
   Example: BING_CONNECTION_ID="/subscriptions/{subscription-id}/resourceGroups/{resource-group}/
            providers/Microsoft.CognitiveServices/accounts/{ai-service-name}/projects/{project-name}/
            connections/{connection-name}"

To set up Bing Grounding:
1. Go to Azure AI Foundry portal (https://ai.azure.com)
2. Navigate to your project's "Connected resources" section
3. Add a new connection for "Grounding with Bing Search"
4. Copy the connection ID and set it as the BING_CONNECTION_ID environment variable
"""


def get_time() -> str:
    """Get the current UTC time."""
    current_time = datetime.now(timezone.utc)
    return f"The current UTC time is {current_time.strftime('%Y-%m-%d %H:%M:%S')}."


async def handle_approvals_with_thread(query: str, agent: "AgentProtocol", thread: "AgentThread"):
    """Here we let the thread deal with the previous responses, and we just rerun with the approval."""
    from agent_framework import ChatMessage

    result = await agent.run(query, thread=thread, store=True)
    while len(result.user_input_requests) > 0:
        new_input: list[Any] = []
        for user_input_needed in result.user_input_requests:
            print(
                f"User Input Request for function from {agent.name}: {user_input_needed.function_call.name}"
                f" with arguments: {user_input_needed.function_call.arguments}"
            )
            user_approval = input("Approve function call? (y/n): ")
            new_input.append(
                ChatMessage(
                    role="user",
                    contents=[user_input_needed.create_response(user_approval.lower() == "y")],
                )
            )
        result = await agent.run(new_input, thread=thread, store=True)
    return result


async def main() -> None:
    """Example showing multiple tools for Azure AI Agent with persistent agent creation."""
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
            name="DocsAgent-MultiTools",
            instructions="You are a helpful assistant that can help with microsoft documentation questions.",
        )
        print(f"✓ Agent created with ID: {azure_ai_agent.id}\n")

        try:
            agent = AzureAIAgentClient(
                project_client=project_client,
                agent_id=azure_ai_agent.id,
                async_credential=credential
            ).create_agent(
                name="DocsAgent",
                instructions="You are a helpful assistant that can help with microsoft documentation questions.",
                tools=[
                    HostedMCPTool(
                        name="Microsoft Learn MCP",
                        url="https://learn.microsoft.com/api/mcp",
                    ),
                    HostedWebSearchTool(count=5),
                    get_time,
                ],
            )
            thread = agent.get_new_thread()
            # First query
            query1 = "How to create an Azure storage account using az cli and what time is it?"
            print(f"User: {query1}")
            result1 = await handle_approvals_with_thread(query1, agent, thread)
            print(f"{agent.name}: {result1}\n")
            print("\n=======================================\n")
            # Second query
            query2 = "What is Microsoft Agent Framework and use a web search to see what is Reddit saying about it?"
            print(f"User: {query2}")
            result2 = await handle_approvals_with_thread(query2, agent, thread)
            print(f"{agent.name}: {result2}\n")
        finally:
            # Keep agent alive in Azure AI Foundry
            print(f"✓ Agent '{azure_ai_agent.name}' (ID: {azure_ai_agent.id}) will remain in Azure AI Foundry\n")


if __name__ == "__main__":
    asyncio.run(main())
