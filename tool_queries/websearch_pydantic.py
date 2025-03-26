import os
import asyncio

from openai import AsyncAzureOpenAI

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

model="gpt-35-turbo"

async def websearch_chatbot(user_message: str, llm_model_name:str=model):
    """
    A simple chatbot function that takes a user message as input and returns a response, with a duck duck go search tool.

    :param user_message: The message from the user
    :return: The response from the chatbot
    """

    tools=[duckduckgo_search_tool()]
    system_prompt_str : str = 'Search DuckDuckGo for the given query and return the results.'
   
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
    api_version=os.getenv("OPENAI_API_VERSION")
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")

    client = AsyncAzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        api_key=api_key,
    )

    model = OpenAIModel(
        llm_model_name,
        provider=OpenAIProvider(openai_client=client),
    )

    agent = Agent(
        model,
        system_prompt=system_prompt_str,
        tools=tools
        )

    async with agent.iter(user_message) as result:
        async for node in result:
            print(node)

asyncio.run(websearch_chatbot("What is EPAM share price today ?"))