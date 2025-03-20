import pymupdf4llm
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

output_dir = Path(Path(__file__).parent.parent, 'output')


def pdf2md_pymupdf():
    """
    Convert a pdf to a md file using a python library (pymupdf4llm)

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

    md_text = pymupdf4llm.to_markdown(file_path_object)

    output_file = Path(output_dir, file_path_object.name[:-4] + "_pymupdf.md")
    with open(output_file, "w") as md:
        md.write(md_text)

    print(f"Markdown output written to: {output_file}")

pdf2md_pymupdf()