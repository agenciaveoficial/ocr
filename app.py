from fastapi import FastAPI, UploadFile, File
from typing import List
import pytesseract
from PIL import Image
import io

app = FastAPI()

@app.post("/ocr")
async def ocr(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        text = pytesseract.image_to_string(image, lang='por')  # ou 'eng', etc.
        results.append({
            "filename": file.filename,
            "text": text
        })
    return {"results": results}
