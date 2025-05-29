
def convertResponse(response, page_count):
    return {
       "full_content": response['full_content'],
       "page_count": page_count,
       "paragraphs": response['paragraphs'],
       "tables": response['tables']
    }