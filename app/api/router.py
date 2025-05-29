from fastapi import APIRouter
from app.api.routes.document_ocr_router import document_ocr_router
router = APIRouter()
router.include_router(document_ocr_router)
