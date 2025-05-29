import tempfile
import os
import ocrmypdf
from app.core.util.pdf_util import flatten_pdf

def convert_to_textbased_pdf(path, output):
    try:
        ocrmypdf.ocr(
            path,
            output,
            lang="vie",
            force_ocr=True,
            progress_bar=True)
    finally:
        print('uh')