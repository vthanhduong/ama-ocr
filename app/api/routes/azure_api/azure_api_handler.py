from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from app.core.config import settings
from app.core.util.pdf_util import preprocess
endpoint = settings.AZURE_RESOURCE_ENDPOINT
api_key = settings.AZURE_RESOURCE_API_KEY

async def azure_doc_read_analyze(document):
    preprocess_pdf = await preprocess(document)
    file_stream = preprocess_pdf["original_pdf"]
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key)
    )
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-read",
        file_stream
    )
    result = poller.result()
    response = {
        "pageCount": len(result["pages"]),
        "full_content": result["content"],
        "paragraphs": [p["content"] for p in result["paragraphs"]]
    }
    return response