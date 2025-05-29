from google import genai
from google.genai import types
from app.core.config import settings
from app.core.util.pdf_util import split_pdf
import json
google_api_key=settings.GOOGLE_GEMINI_API_KEY
async def google_gemini_20_flash(document):
    client = genai.Client(api_key=google_api_key)
    print('Document too long, splitting...')
    pdf_parts = split_pdf(document.file)
    print('Document splitted, iterating documents...')
    responseOutput = {
        "full_content": "",
        "paragraphs": [],
        "tables": [],
        "input_token": 0,
        "output_token": 0,
    }
    for pdf in pdf_parts:
        print("Start analyze document part...")
        prompt = "Based on uploaded document, Provide the json string output only (follow by this structure and not an array interface Result {paragraphs: []//list of paragraphs string in document, tables: [[['cell',cell',...]]]//all tables in document}')."
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[types.Part.from_bytes(data=pdf.getvalue(), mime_type="application/pdf"), prompt],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=8192,
                    response_mime_type="application/json"
                )
            )
            output = json.loads(response.text)
            for paragraph in output['paragraphs']:
                responseOutput["full_content"] += paragraph + '\n'
                responseOutput["paragraphs"].append(paragraph)
            for table in output['tables']:
                responseOutput["tables"].append(table)
            print("Document part analyzed...")
            responseOutput['input_token'] += response.usage_metadata.prompt_token_count
            responseOutput['output_token'] += response.usage_metadata.candidates_token_count
        except Exception as e:
            print('An error has occurred. Continue sending APIs...', str(e))
    return responseOutput