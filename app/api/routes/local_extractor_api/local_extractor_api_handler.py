import pdfplumber
import camelot
import tempfile
import io
import os
import ocrmypdf
from app.core.util.pdf_util import preprocess

async def local_extract(document):
    preprocessed_pdf = await preprocess(document)
    pdf_stream = preprocessed_pdf["original_pdf"]
    page_count = 0
    try:
        is_scanned = True
        with pdfplumber.open(pdf_stream) as pdf:
            for i, page in enumerate(pdf.pages[:2]):
                if page.extract_text():
                    is_scanned = False
                    break
            page_count = len(pdf.pages)
        if is_scanned:
            try:
                pdf_stream = preprocessed_pdf["flattened_pdf"]
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as input_file:
                    input_file.write(pdf_stream.getvalue())
                    input_path = input_file.name
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as output_file:
                    output_path = output_file.name
                ocrmypdf.ocr(
                    input_path,
                    output_path,
                    lang="vie",
                    force_ocr=True,
                    progress_bar=True
                )
                with open(output_path, "rb") as f:
                    pdf_stream = io.BytesIO(f.read())
            finally:
                os.remove(input_path)
                os.remove(output_path)
        full_content = ""
        paragraphs = []
        tempTable = []
        with pdfplumber.open(pdf_stream) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                tables = page.extract_tables()
                for table in tables:
                    tempTable.append(table)
                if text:
                    print(f"Page {i+1}: Text extracted")
                    full_content = full_content + text + "\n"
                    paragraphs.append(text + "\n")
                else:
                    print(f"Page {i+1}: Cannot extract text")
            page_count = len(pdf.pages)
        rtables = tempTable
        if is_scanned:
            ctables = camelot.read_pdf(pdf_stream, pages="1-end", flavor="stream")
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
    except Exception as e:
        print(str(e))