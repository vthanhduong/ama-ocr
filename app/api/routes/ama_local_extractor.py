# import uuid
# from fastapi import APIRouter, UploadFile, HTTPException, File, Depends, Form
# from app.core.config import settings
# from sqlalchemy import asc, desc
# from sqlalchemy.orm import Session
# from app.database.connector import get_db
# import pdfplumber
# import shutil
# import os
# import tempfile
# import json
# import camelot
# from app.core.util.pdf_ocr import convert_to_textbased_pdf
# from app.core.util.pdf_util import convert_to_pdf
# from app.core.util import response_converter
# from app.api.routes.google_api.google_ai_api_handler import google_gemini_20_flash
# from app.models import AnalyzeResult

# ama_local_extractor_router = APIRouter(prefix='/local-extractor-preview', tags=['Local Extractor'])

# @ama_local_extractor_router.post('/analyze')
# async def analyze_document_test(document: UploadFile = File(...), db: Session = Depends(get_db)):
#     '''
#     Extract
#     '''
#     temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(document.filename)[-1])
#     temp_dir = tempfile.mkdtemp()
#     temp_pdf_path = ""
#     page_count = 0
#     try:
#         with open(temp_input.name, "wb") as buffer:
#             document.file.seek(0)
#             shutil.copyfileobj(document.file, buffer)
#             ext = os.path.splitext(document.filename)[-1].lower()
#         if ext in [".docx", ".xlsx"]:
#             print(f"Converting {ext} to PDF...")
#             temp_pdf_path = convert_to_pdf(temp_input.name, temp_dir)
#         elif ext == ".pdf":
#             temp_pdf_path = temp_input.name
#         else:
#             return {
#                 "status_code": 400,
#                 "error": "Unsupported file format. Only PDF, DOCX, and XLSX are supported."
#             }
#         is_scanned = True
#         with pdfplumber.open(temp_pdf_path) as pdf:
#             for i, page in enumerate(pdf.pages[:2]):
#                 if page.extract_text():
#                     is_scanned = False
#                     break
#             page_count = len(pdf.pages)
#         if is_scanned:
#             print("Scanned document found! Bad quality images, trying to extract text...")
#             convert_to_textbased_pdf(temp_pdf_path)
#             document.file.seek(0)
#             obj = await google_gemini_20_flash(document)
#             converted = response_converter.convertResponse(obj, page_count)
#             final_obj = json.dumps(converted, ensure_ascii=False)
#             file_name = document.filename
#             file_size = document.size
#             file_extension = '.' + document.filename.split('.')[-1]
#             db_analyzeResult = AnalyzeResult(
#                 id=str(uuid.uuid4()),
#                 file_name=file_name,
#                 file_size=file_size,
#                 api_version=settings.API_VERSION,
#                 file_extension=file_extension,
#                 model="google/gemini-20-flash",
#                 output_data=final_obj,
#                 input_token=0,
#                 output_token=0,
#                 estimated_cost=0.0
#             )
#             db.add(db_analyzeResult)
#             db.commit()
#             db.refresh(db_analyzeResult)
#             return {
#                 "status_code": 200,
#                 "success": "success",
#                 "data": db_analyzeResult,
#             }
#         full_content = ""
#         paragraphs = []
#         ctables = []
#         with pdfplumber.open(temp_pdf_path) as pdf:
#             for page in pdf.pages:
#                 text = page.extract_text()
#                 tables = page.extract_tables()
#                 for table in tables:
#                     ctables.append(table)
#                 if text:
#                     print(f"Page {i+1}: Text extracted")
#                     full_content += text + "\n"
#                     paragraphs.append(text + "\n")
#                     obj = {
#                         "paragraphs": paragraphs,
#                         "tables": ctables,
#                     }
#                 else:
#                     print(f"Page {i+1}: Cannot extract text")
#             page_count = len(pdf.pages)
#         tabless = camelot.read_pdf(temp_pdf_path, pages="1-end", flavor="lattice")
#         obj = {
#             "full_content": full_content,
#             "page_count": page_count,
#             "paragraphs": paragraphs,
#             "tables": tabless
#         }
#         for table in tabless:
#             df = table.df
#             for row_index, row in df.iterrows():
#                 print(f"Row {row_index}:")
#                 for col_index, cell in enumerate(row):
#                     print(f"  Col {col_index}: {cell}")
#         return {
#             'message': 'yes'
#         }
#         file_name = document.filename
#         file_size = document.size
#         file_extension = '.' + document.filename.split('.')[-1]
#         db_analyzeResult = AnalyzeResult(
#             id=str(uuid.uuid4()),
#             api_version=settings.API_VERSION,
#             file_name=file_name,
#             file_size=file_size,
#             file_extension=file_extension,
#             model="ama/local-extractor",
#             output_data=json.dumps(obj, ensure_ascii=False),
#             input_token= 0,
#             output_token= 0,
#             estimated_cost=0.0
#         )
#         db.add(db_analyzeResult)
#         db.commit()
#         db.refresh(db_analyzeResult)
#         return {
#                 "status_code": 200,
#                 "success": "success",
#                 "data": db_analyzeResult,
#         }
#     finally:
#         if os.path.exists(temp_input.name):
#             os.remove(temp_input.name)
#         if os.path.exists(temp_pdf_path) and temp_pdf_path != temp_input.name:
#             os.remove(temp_pdf_path)
#         shutil.rmtree(temp_dir, ignore_errors=True)