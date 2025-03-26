# genai-scripts
Shared repo for python scripts, facilitating the day to day use of GenAI solutions

## Getting Started

This repository contains several Python scripts that interact with various Generative AI APIs. To use these scripts, you'll need to set up your environment and configure API keys. Follow the steps below to get started:

### Prerequisites

1.  **Python 3.8+:** Ensure you have Python 3.8 or a later version installed on your system. You can check your Python version by running `python --version` or `python3 --version` in your terminal.

2.  **Virtual Environment (Recommended):** It's highly recommended to use a virtual environment to isolate the project's dependencies. This prevents conflicts with other Python projects on your system.

    *   **Create a virtual environment:**
        ```bash
        python3 -m venv .venv  # or python -m venv .venv
        ```
    *   **Activate the virtual environment:**
        *   **Linux/macOS:**
            ```bash
            source .venv/bin/activate
            ```
        *   **Windows:**
            ```bash
            .venv\Scripts\activate
            ```
        You should see `(.venv)` at the start of your terminal prompt once activated.
3. **Install project dependencies**:
    Install all the librairies listed in the requirements file.
    ```bash
    pip install -r requirements.in
    ```

4.  **API Keys:** You will need API keys for the different AI services your scripts will use.
    *   All the API keys should be stored inside the `.env` file in the root of the project
    * The content of the `.env` file should be like the following (replace with your keys):
     ```properties
        OPENAI_API_VERSION="2023-12-01-preview"
        AZURE_OPENAI_API_KEY="your_azure_openai_api_key"
        GROQ_API_KEY="your_groq_api_key"
        MISTRAL_API_KEY="your_mistral_api_key"
        GEMINI_API_KEY="your_gemini_api_key"
     ```

    *   **Important:**
        *   Never commit your `.env` file to version control. It is already listed in the `.gitignore` file to avoid accidental uploads.
        *   Keep your API keys confidential.
    *   **The API Keys needed for each script are listed at the begining of each one, or they can be guessed by reading the code**

### How to Run the Scripts

1.  **Navigate to the project directory:**
    ```bash
    cd genai-scripts
    ```

2.  **Ensure your virtual environment is activated** (see Prerequisites step 2).

3. **Run the script**
    * For example, to run the `script_name.py` script:
    ```bash
    python script_name.py
    ```

## Contributing

If you would like to contribute to this project, please feel free to open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



