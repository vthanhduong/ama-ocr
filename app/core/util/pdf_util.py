from PyPDF2 import PdfReader, PdfWriter
import io
import subprocess
import os

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