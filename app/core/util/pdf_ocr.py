import tempfile
import os
import ocrmypdf
from app.core.util.pdf_util import flatten_pdf

def convert_to_textbased_pdf(path):
    temp_flattened = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    try:
        flatten_pdf(path, temp_flattened.name)
        ocrmypdf.ocr(
            temp_flattened.name,
            path,
            lang="vie",
            force_ocr=True,
            progress_bar=True)
    finally:
        os.remove(temp_flattened.name)