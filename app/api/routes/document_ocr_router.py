import uuid
from fastapi import APIRouter, UploadFile, HTTPException, File, Depends, Query
from app.models import AnalyzeResult
from app.core.config import settings
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from app.database.connector import get_db
import json
from enum import Enum
from app.core.util import response_converter
from app.api.routes.google_api.google_ai_api_handler import google_gemini_20_flash
from app.api.routes.local_extractor_api.local_extractor_api_handler import local_extract
from app.api.routes.azure_api.azure_api_handler import azure_doc_read_analyze
from app.api.routes.openai_api.openai_api_handler import o4_mini_doc_analyze

class Model(str, Enum):
    openai_o4_mini = 'openai/o4-mini'
    azure_prebuilt_read = 'azure/prebuilt-read'
    gemini_20_flash = 'google/gemini-20-flash'
    local_extractor = 'ama/local-extractor'

document_ocr_router = APIRouter(prefix='/document-ocr', tags=['Document OCR'])

async def google_gemini(document, db):
    obj = await google_gemini_20_flash(document)
    converted = response_converter.convertResponse(obj, 0)
    file_name = document.filename
    file_size = document.size
    file_extension = '.' + document.filename.split('.')[-1]
    db_analyzeResult = AnalyzeResult(
        id=str(uuid.uuid4()),
        file_name=file_name,
        file_size=file_size,
        api_version=settings.API_VERSION,
        file_extension=file_extension,
        model="google/gemini-20-flash",
        output_data=json.dumps(converted, ensure_ascii=False),
        input_token=obj['input_token'],
        output_token=obj['output_token'],
        estimated_cost=obj['input_token'] *  0.0000001 + obj['output_token'] * 0.0000004
    )
    db.add(db_analyzeResult)
    db.commit()
    db.refresh(db_analyzeResult)
    return {
        "status_code": 200,
        "success": "success",
        "data": db_analyzeResult,
    }

async def local_extractor(document, db):
    file_name = document.filename
    file_size = document.size
    file_extension = '.' + document.filename.split('.')[-1]
    obj = local_extract(document)
    db_analyzeResult = AnalyzeResult(
        id=str(uuid.uuid4()),
        api_version=settings.API_VERSION,
        file_name=file_name,
        file_size=file_size,
        file_extension=file_extension,
        model="ama/local-extractor",
        output_data=json.dumps(obj, ensure_ascii=False),
        input_token= 0,
        output_token= 0,
        estimated_cost=0.0
    )
    db.add(db_analyzeResult)
    db.commit()
    db.refresh(db_analyzeResult)
    return {
            "status_code": 200,
            "success": "success",
            "data": db_analyzeResult,
    }

async def openai_o4_mini_ocr(document, db):
    response = await o4_mini_doc_analyze(document)
    file_name = document.filename
    file_size = document.size
    file_extension = '.' + document.filename.split('.')[-1]
    db_analyzeResult = AnalyzeResult(
        id=str(uuid.uuid4()),
        file_name=file_name,
        file_size=file_size,
        file_extension=file_extension,
        model="openai/o4-mini",
        output_data=json.dumps(response, ensure_ascii=False),
        input_token=response.usage.input_tokens,
        output_token=response.usage.output_tokens,
        estimated_cost=(0.0000011 * response.usage.input_tokens) + (0.0000044 * response.usage.output_tokens)
    )
    db.add(db_analyzeResult)
    db.commit()
    db.refresh(db_analyzeResult)
    return {
        "status_code": 200,
        "success": "success",
        "data": db_analyzeResult,
    }

async def azure_prebuilt_read_ocr(document, db):
        response = await azure_doc_read_analyze(document)
        file_name = document.filename
        file_size = document.size
        file_extension = '.' + document.filename.split(".")[-1]
        db_analyzeResult = AnalyzeResult(
            id=str(uuid.uuid4()),
            file_name=file_name,
            file_size=file_size,
            file_extension=file_extension,
            model="azure/prebuilt-read",
            output_data=json.dumps(response, ensure_ascii=False),
            input_token=0,
            output_token=0,
            estimated_cost=(1.5/1000) * response["pageCount"]
        )
        db.add(db_analyzeResult)
        db.commit()
        db.refresh(db_analyzeResult)
        return {
            "status_code": 200,
            "success": "success",
            "data": db_analyzeResult
        }

@document_ocr_router.get("/")
async def get_all_analyze_result(db: Session = Depends(get_db)):
    """
    Get All Analyze Result
    """
    try:
        results = db.query(AnalyzeResult).order_by(desc(AnalyzeResult.created_at)).all()
        return {
            "status_code": 200,
            "success": "success",
            "data": results
        }
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
@document_ocr_router.get("/output-data/{id}")
async def get_output_data_by_analyze_result_id(id: str, db: Session = Depends(get_db)):
    """
    Get Output data by Analyze Result Id
    """
    try:
        result = db.query(AnalyzeResult).filter(AnalyzeResult.id == id, AnalyzeResult.model == 'openai/o4-mini').first()
        if not result:
            return HTTPException(status_code=404, detail="Not found")
        return {
            "status_code": 200,
            "success": "success",
            "data": json.loads(result.output_data)
        }
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
@document_ocr_router.get("/{id}")
async def get_analyze_result_by_id(id: str, db: Session = Depends(get_db)):
    """
    Get Analyze Result by Id
    """
    try:
        result = db.query(AnalyzeResult).filter(AnalyzeResult.id == id, AnalyzeResult.model == 'openai/o4-mini').first()
        if not result:
            return HTTPException(status_code=404, detail="Not found")
        return {
            "status_code": 200,
            "success": "success",
            "data": result
        }
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
@document_ocr_router.delete('/{id}')
async def delete_analyze_result_by_id(id: str, db: Session = Depends(get_db)):
    """
    Delete Analyze Result by Id
    """
    try:
        result = db.query(AnalyzeResult).filter(AnalyzeResult.id == id).first()
        if not result:
            return HTTPException(status_code=404, detail="Not found")
        db.delete(result)
        db.commit()
        return {
            "status_code": 200,
            "success": "success",
            "message": f"Delete analyze result with id {id} successfully"
        }
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@document_ocr_router.post("/analyze")
async def analyze_document(model: Model = Query(..., description="Chooose a model"), document: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Analyze document
    """
    print(model)
    try:
        if model == 'openai/o4-mini':
            return await openai_o4_mini_ocr(document, db)
        elif model == 'azure/prebuilt-read':
            return await azure_prebuilt_read_ocr(document, db)
        elif model == 'google/gemini-20-flash':
            return await google_gemini(document, db)
        elif model == 'ama/local-extractor':
            return await local_extractor(document, db)
        return {
                "status_code": 404,
                "success": "success",
                "message": "Model not found"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))