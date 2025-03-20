from mistralai import Mistral
import os
import tkinter as tk
from tkinter import filedialog

from pathlib import Path
script_name = Path(__file__).stem

output_dir = Path(Path(__file__).parent.parent, 'output')


#Get the api key from the .env file to be able to communicate with the Mistral API
api_key = os.getenv("MISTRAL_API_KEY")


def pdf2md_mistralOCR():
    """
    Convert a pdf to a md file using a API call to Mistral API and the OCR endpoint.

    Returns:
        Write a md file in the output folder.
    """
    client = Mistral(api_key=api_key)

    # Create a Tkinter root window (it won't be shown)
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Open a file dialog to choose a PDF file
    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF files", "*.pdf")],
    )

    # Check if a file was selected
    if not file_path:
        print("No file selected.")
        return  # Exit the function if no file was selected

    # Now, continue with the selected file
    file_path_object = Path(file_path)

    uploaded_pdf = client.files.upload(
        file={
            "file_name": file_path_object.name,
            "content": open(file_path, "rb"),
        },
        purpose="ocr",
    )

    signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)

    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": signed_url.url,
        },
    )

    full_str_markdown = ""

    for page in ocr_response.pages:
        full_str_markdown += page.markdown

    # print(full_str_markdown)
    output_file = Path(output_dir, file_path_object.name[:-4] + "_mistralOCR.md")
    with open(output_file, "w") as md:
        md.write(full_str_markdown)

    print(f"Markdown output written to: {output_file}")

pdf2md_mistralOCR()