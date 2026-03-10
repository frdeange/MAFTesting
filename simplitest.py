# filepath: Direct OpenAI compatible approach
from openai import OpenAI 
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from agent_framework_devui import serve

# edit base_url with your <foundry-resource-name>, <project-name>, and <app-name>
openai = OpenAI(
    api_key=get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default"),
    base_url="https://demoenvkikoaiscfwjw.services.ai.azure.com/api/projects/demoenvkikoprjcfwjw/applications/TesKikoAgent/protocols/openai/responses?api-version=2025-11-15-preview",
    default_query = {"api-version": "2025-11-15-preview"}
)
