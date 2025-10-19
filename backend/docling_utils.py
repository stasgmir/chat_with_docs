from docling.document_converter import DocumentConverter
from pathlib import Path
import tempfile
import os

def save_uploaded_file_as_markdown(file_bytes: bytes, filename: str, combined_output="output/combined_docs.md") -> dict:

    tmp_path = None
    try:

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name


        converter = DocumentConverter()

        result = converter.convert(tmp_path)
        markdown = result.document.export_to_markdown()

        os.makedirs(os.path.dirname(combined_output), exist_ok=True)

        with open(combined_output, "a", encoding="utf-8") as f:
            f.write("\n\n")
            f.write(f"---\n### 📄 START OF DOCUMENT: {filename}\n---\n\n")
            f.write(markdown.strip())
            f.write(f"\n\n---\n### 📄 END OF DOCUMENT: {filename}\n---\n\n")

        return {
            "status": "Success",
            "file": filename,
            "combined_output": combined_output,
            "markdown_length": len(markdown),
            "preview": markdown[:200].replace("\n", " "),
        }

    except Exception as e:
        return {"status": "Failed", "file": filename, "error": str(e)}

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
