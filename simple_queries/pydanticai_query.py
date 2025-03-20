import os
from pydantic_ai import Agent

from openai import AsyncAzureOpenAI

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

model="gpt-35-turbo"

def query_azure_openai_with_pydanticai(prompt:str, model_name:str=model):

    api_key=os.getenv("AZURE_OPENAI_API_KEY")
    api_version=os.getenv("OPENAI_API_VERSION")
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")

    client = AsyncAzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        api_key=api_key,
    )

    model = OpenAIModel(
        model_name,
        provider=OpenAIProvider(openai_client=client),
    )
    agent = Agent(model)

    result = agent.run_sync(prompt)  
    return result.data

print(query_azure_openai_with_pydanticai("Why is the sky blue ?"))