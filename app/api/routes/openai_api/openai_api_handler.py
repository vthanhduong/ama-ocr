import openai
from app.core.config import settings
import json

openai.api_key = settings.OPENAI_API_KEY

async def o4_mini_doc_analyze(document):
    file = openai.files.create(
            file=(document.filename, document.file),
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
        text_format={
            "type": "json_object"
        }    
    )
    obj = json.loads(response.output_text)
    output_response = {
        "full_content": "",
        "paragraphs": obj["paragraphs"],
        "tables": obj["tables"]
    }
    for paragraph in obj["paragraphs"]:
        output_response["full_content"] += paragraph + "\n"
    return output_response