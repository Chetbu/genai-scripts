import os
from openai import AzureOpenAI

model="gpt-35-turbo"

def query_azure_openai(prompt, deployment_name=model, max_tokens=100, temperature=0.4):
    """
    Queries an Azure OpenAI deployment using the openai library.

    Args:
        prompt (str): The prompt to send to the LLM.
        deployment_name (str): The name of your deployed model (e.g., "gpt-35-turbo").
        max_tokens (int): The maximum number of tokens to generate.
        temperature (float): Controls the randomness of the output (0.0 = deterministic, 1.0 = very random).

    Returns:
        str: The generated text from the LLM, or None if there was an error.
    """
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage (make sure you have set the environment variables):
print(query_azure_openai("Why is the sky blue?"))
