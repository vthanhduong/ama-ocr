import tempfile
import shutil
import os
from app.core.util.pdf_util import convert_to_pdf
from app.core.util.pdf_ocr import convert_to_textbased_pdf
import pdfplumber
import camelot

def local_extract(document):
    temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(document.filename)[-1])
    temp_dir = tempfile.mkdtemp()
    temp_pdf_path = ""
    page_count = 0
    try:
        with open(temp_input.name, "wb") as buffer:
            document.file.seek(0)
            shutil.copyfileobj(document.file, buffer)
            ext = os.path.splitext(document.filename)[-1].lower()
        if ext in [".docx", ".xlsx"]:
            print(f"Converting {ext} to PDF...")
            temp_pdf_path = convert_to_pdf(temp_input.name, temp_dir)
        elif ext == ".pdf":
            temp_pdf_path = temp_input.name
        else:
            return {
                "status_code": 400,
                "error": "Unsupported file format. Only PDF, DOCX, and XLSX are supported."
            }
        is_scanned = True
        with pdfplumber.open(temp_pdf_path) as pdf:
            for i, page in enumerate(pdf.pages[:2]):
                if page.extract_text():
                    is_scanned = False
                    break
            page_count = len(pdf.pages)
        if is_scanned:
            print("Scanned document found! Bad quality images, trying to extract text...")
            convert_to_textbased_pdf(temp_pdf_path)
        full_content = ""
        paragraphs = []
        tempTable = []
        with pdfplumber.open(temp_pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                tables = page.extract_tables()
                for table in tables:
                    tempTable.append(table)
                if text:
                    print(f"Page {i+1}: Text extracted")
                    full_content = full_content + text + "\n"
                    paragraphs.append(text + "\n")
                    print(full_content)
                else:
                    print(f"Page {i+1}: Cannot extract text")
            page_count = len(pdf.pages)
        rtables = tempTable
        if len(rtables) == 0:
            ctables = camelot.read_pdf(temp_pdf_path, pages="1-end", flavor="stream")
            for table in ctables:
                df = table.df
                new_table = []
                for index, row in df.iterrows():
                    new_row = []
                    for cell in row:
                        new_row.append(cell)
                    new_table.append(new_row)
                rtables.append(new_table)
        obj = {
            "full_content": full_content,
            "page_count": page_count,
            "paragraphs": paragraphs,
            "tables": rtables
        }
        return obj
    finally:
        if os.path.exists(temp_input.name):
            os.remove(temp_input.name)
        if os.path.exists(temp_pdf_path) and temp_pdf_path != temp_input.name:
            os.remove(temp_pdf_path)
        shutil.rmtree(temp_dir, ignore_errors=True)