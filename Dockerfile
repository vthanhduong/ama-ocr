FROM python:3.11-slim

WORKDIR /app


RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-vie \
    ghostscript

RUN pip install --upgrade pip

RUN pip install pytesseract && python3 -m pip install PyMySQL[rsa]

RUN apt-get update -y && apt-get install -y libreoffice libreoffice-writer libreoffice-calc

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]