from fastapi import FastAPI, UploadFile, File
from typing import List
import pytesseract
from PIL import Image
import io
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Aplicação FastAPI iniciada com sucesso!")
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/ocr")
async def ocr(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            text = pytesseract.image_to_string(image, lang='por',config='--psm 6 --oem 3')
            results.append({
                "filename": file.filename,
                "text": text
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": f"Erro ao processar o arquivo: {str(e)}"
            })
        finally:
            await file.close()
    return {"results": results}
