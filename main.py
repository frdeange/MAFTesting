# Copyright (c) Microsoft. All rights reserved.
import asyncio
import os
from pathlib import Path

from agent_framework_declarative import AgentFactory
from agent_framework_devui import serve
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv


load_dotenv()


async def create_agent():
    """Create an agent from a declarative yaml specification."""
    yaml_path = Path(__file__).parent / "agents" / "mslearnagent.yaml"
    project_endpoint = os.getenv("AZURE_FOUNDRY_PROJECT_ENDPOINT")

    credential = DefaultAzureCredential()
    factory = AgentFactory(
        client_kwargs={
            "async_credential": credential,
            "project_endpoint": project_endpoint
        }
    )
    return factory.create_agent_from_yaml_path(yaml_path)


if __name__ == "__main__":
    agent = asyncio.run(create_agent())
    serve(
        entities=[agent], 
        host="localhost", 
        port=8000,
        auto_open=True
    )