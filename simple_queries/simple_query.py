import os
import requests
import json

api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("OPENAI_API_VERSION")
model="gpt-35-turbo"

def query_azure_llm(prompt, deployment_name=model, max_tokens=100, temperature=0.4):
    """
    Queries an Azure OpenAI Language Model (LLM) endpoint.

    Args:
        prompt (str): The prompt to send to the LLM.
        deployment_name (str): The name of your deployed model (e.g., "my-gpt-35-turbo").
        max_tokens (int): The maximum number of tokens to generate.
        temperature (float): Controls the randomness of the output (0.0 = deterministic, 1.0 = very random).

    Returns:
        str: The generated text from the LLM, or None if there was an error.
    """

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    url = f"{endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"

    payload = json.dumps({
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful AI assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    })

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        response_data = response.json()

        # Extract the generated text
        generated_text = response_data["choices"][0]["message"]["content"]
        return generated_text

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        if 'response' in locals() and response :
          print(f"Response content: {response.content}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error parsing response: {e}")
        if 'response' in locals() and response :
          print(f"Response content: {response.content}")
        return None
    except Exception as e:
        print(f"An unexpected error occured: {e}")
        if 'response' in locals() and response :
          print(f"Response content: {response.content}")
        return None
    
print(query_azure_llm("Why is the sky blue ?"))