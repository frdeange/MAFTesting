"""Deploy agent to Azure AI Foundry from YAML definition."""

import asyncio
import os
import sys
from pathlib import Path
from agent_framework_declarative import AgentFactory
from azure.identity.aio import DefaultAzureCredential


async def deploy_agent(yaml_file: str) -> None:
    """
    Deploy an agent to Azure AI Foundry.
    
    Args:
        yaml_file: Path to the agent YAML definition file
    """
    yaml_path = Path(yaml_file)
    
    if not yaml_path.exists():
        print(f"❌ Error: File not found: {yaml_file}")
        sys.exit(1)
    
    project_endpoint = os.getenv("AZURE_FOUNDRY_PROJECT_ENDPOINT")
    
    if not project_endpoint:
        print("❌ Error: AZURE_FOUNDRY_PROJECT_ENDPOINT environment variable not set")
        sys.exit(1)
    
    print(f"📦 Deploying agent from: {yaml_path.name}")
    print(f"🎯 Target project: {project_endpoint}")
    
    try:
        # Create credentials
        credential = DefaultAzureCredential()
        
        # Create factory
        factory = AgentFactory(
            client_kwargs={
                "async_credential": credential,
                "project_endpoint": project_endpoint
            }
        )
        
        # Deploy agent (registers in Azure AI Foundry)
        agent = factory.create_agent_from_yaml_path(yaml_path)
        
        print(f"✅ Agent deployed successfully!")
        print(f"   Name: {agent.name}")
        print(f"   Description: {agent.description or 'N/A'}")
        print(f"\n🎉 Agent '{agent.name}' is now available in Azure AI Foundry")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python deploy_agent.py <path-to-agent.yaml>")
        print("Example: python deploy_agent.py agents/mslearnagent.yaml")
        sys.exit(1)
    
    asyncio.run(deploy_agent(sys.argv[1]))
