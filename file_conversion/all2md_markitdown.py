from markitdown import MarkItDown
import os
import tkinter as tk
from tkinter import filedialog

from pathlib import Path
script_name = Path(__file__).stem

output_dir = Path(Path(__file__).parent.parent, 'output')

def all2md_markitdown():
    """
    Convert a document to a md file using a microsoft library called markitdown.


    Returns:
        Write a md file in the output folder.
    """

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

    markitdown = MarkItDown()
    result = markitdown.convert(file_path_object)

   

    # print(full_str_markdown)
    output_file = Path(output_dir, file_path_object.name[:-4] + "_markitdown.md")
    with open(output_file, "w") as md:
        md.write(result.text_content)

    print(f"Markdown output written to: {output_file}")

all2md_markitdown()
