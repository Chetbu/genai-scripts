import os
import requests
import json

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
endpoint_url = endpoint + "/openai/deployments"
api_key = os.getenv("AZURE_OPENAI_API_KEY")

def get_azure_models():
    """
    Queries an Azure OpenAI Language Model (LLM) endpoint for all the models deployed.

    Returns:
        list[str]: The list of all the models deployed.
    """
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    req = requests.get(endpoint_url, headers=headers)
    id_list = [x["id"] for x in json.loads(req.content)['data']]

    return id_list

print(get_azure_models())