from PyPDF2 import PdfReader, PdfWriter
import io
from PIL import Image
import subprocess
import os
import tempfile

def split_pdf(document, split_number: int = 9):
    reader = PdfReader(document)
    total_pages = len(reader.pages)
    pdf_parts = []
    for start in range(0, total_pages, split_number):
        writer = PdfWriter()
        end = min(start + split_number, total_pages)
        for i in range(start, end):
            writer.add_page(reader.pages[i])
        memory_file = io.BytesIO()
        writer.write(memory_file)
        memory_file.seek(0)
        pdf_parts.append(memory_file)
    return pdf_parts

def convert_to_pdf(input_path: str, output_dir: str):
    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        input_path
    ], check=True)
    pdf_filename = os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
    return os.path.join(output_dir, pdf_filename)

def flatten_pdf(input_path, output_path):
    subprocess.run([
        "gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
        f"-sOutputFile={output_path}", input_path
    ], check=True)
    
def img_to_pdf(inputFile, output_path: str) -> str:
    try:
        image_data = inputFile.read()
        image = Image.open(io.BytesIO(image_data))
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(output_path, "PDF")
        return f"PDF saved successfully to {output_path}"
    except Exception as e:
        return f"Error: {e}"
    
async def preprocess(document):
    try:
        filename = document.filename
        ext = os.path.splitext(filename)[-1].lower()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, filename)
            document.file.seek(0)
            with open(input_path, 'wb') as f:
                f.write(document.file.read())
            if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                output_pdf_path = os.path.join(tmpdir, 'converted.pdf')
                document.file.seek(0)
                img_to_pdf(document.file, output_pdf_path)
            elif ext in ['.docx', '.doc', '.ppt', '.pptx', '.xls', '.xlsx', '.odt']:
                output_pdf_path = convert_to_pdf(input_path, tmpdir)
            elif ext == '.pdf':
                output_pdf_path = input_path
            else:
                return {"error": f"Unsupported file type: {ext}"}
            flattened_pdf_path = os.path.join(tmpdir, 'flattened.pdf')
            with open(output_pdf_path, 'rb') as f:
                original_pdf = io.BytesIO(f.read())
            flatten_pdf(output_pdf_path, flattened_pdf_path)
            with open(flattened_pdf_path, 'rb') as flat_pdf:
                flattened_pdf_data = flat_pdf.read()
                flattened_pdf = io.BytesIO(flattened_pdf_data)
                pdf_parts = split_pdf(io.BytesIO(flattened_pdf_data))
            reader = PdfReader(io.BytesIO(flattened_pdf_data))
            page_count = len(reader.pages)
            return {
                "flattened_pdf_parts": pdf_parts,
                "flattened_pdf": flattened_pdf,
                "original_pdf": original_pdf,
                "page_count": page_count
            }
    except Exception as e:
        print("Error in preprocess / " + str(e))