import os
import asyncio
import faiss
import numpy as np

from openai import AsyncAzureOpenAI

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from pathlib import Path

current_dir = str(Path(__file__).parent)

model="gpt-35-turbo"
embeddings = "text-embedding-3-small-1"

async def rag_chatbot(user_message: str, llm_model_name:str=model, embeddings_model_name:str=embeddings):
    """
    A simple chatbot function that takes a user message as input and returns a response, with a rag search tool.

    :param user_message: The message from the user
    :return: The response from the chatbot
    """

    system_prompt_str : str = 'Search the RAG database using the retrieve tool for the given query and return the results.'
   
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
        )
    
    #creation of the RAG database
    index_faiss = faiss.IndexFlatL2(1536)

    #load the rag_db txt into a vector 
    file_filepath = Path(current_dir, "rag_db.txt")
    with open(file_filepath) as f:
        document_list = f.read().splitlines()
    
    #We create the embedding vector each document
    doc_vectors = []
    doc_ids = []
    for doc_id, doc in enumerate(document_list):
        doc_vector_response = await client.embeddings.create(input=[doc], model=embeddings_model_name)
        doc_vector = doc_vector_response.data[0].embedding
        doc_vectors.append(doc_vector)
        doc_ids.append(doc_id)

    # Convert the list of vectors to a NumPy array
    doc_vectors_np = np.array(doc_vectors).astype('float32')

    # Add the vectors to the index
    index_faiss.add(doc_vectors_np)
   
    #create a tool to search in the database    
    @agent.tool_plain
    async def retrieve(search_query: str) -> str:
        """Retrieve relevant documents from the database using the search query. Returns a long string containing all the needed informations

        Args:
            context: The run context.
            search_query: The search query.
        """

        #create the query vector, using the same embedding
        search_embed = await client.embeddings.create(input=[search_query], model=embeddings_model_name)
        search_vector = search_embed.data[0].embedding

        #search the database
        distance_array, index_array = index_faiss.search(np.array([search_vector]).astype('float32'), k=2)
        index_list = index_array.tolist()
        #retrieve the documents and add it in a string result
        context_full_str = "\n\n"

        for index in index_list[0]:
            print(index, type(index))
            context_full_str += document_list[index]
            context_full_str += "\n\n"

        return context_full_str

    async with agent.iter(user_message) as result:
        async for node in result:
            print(node)

asyncio.run(rag_chatbot("What is in the pond ?"))