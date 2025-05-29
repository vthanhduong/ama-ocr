import openai
import json
from app.core.config import settings
from app.core.util.pdf_util import preprocess

openai.api_key = settings.OPENAI_API_KEY

async def o4_mini_doc_analyze(document):
    preprocessed_pdf = await preprocess(document)
    original = preprocessed_pdf["original_pdf"]
    original.seek(0)
    file = openai.files.create(
            file=(document.filename + '.pdf', original),
            purpose="user_data"
        )
    response = openai.responses.create(
        model="o4-mini",
        input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_file",
                            "file_id": file.id,
                        },
                        {
                            "type": "input_text",
                            "text": "\nBased on uploaded document, Provide the json string output only (follow by this structure and not an array interface Result {paragraphs: []//list of paragraphs string in document, tables: [[['cell',cell',...]]]//all tables in document}').",
                        },
                    ]
                }
            ],
    )
    obj = json.loads(response.output_text)
    output_response = {
        "full_content": "",
        "paragraphs": obj["paragraphs"],
        "tables": obj["tables"],
        "input_token": response.usage.input_tokens,
        "output_token": response.usage.output_tokens,
    }
    for paragraph in obj["paragraphs"]:
        output_response["full_content"] += paragraph + "\n"
    return output_response