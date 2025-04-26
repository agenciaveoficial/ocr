from fastapi import FastAPI, UploadFile, File
from typing import List
import pytesseract
from PIL import Image
import io
import re
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Aplicação FastAPI iniciada com sucesso!")
    yield

app = FastAPI(lifespan=lifespan)

def corrigir_texto(texto: str) -> str:
    substituicoes = {
        "ugldL": "µg/dL",
        "pgtdl": "µg/dL",
        "pgidl": "µg/dL",
        "meUlimL": "mCUl/mL",
        "meUl/mL": "mCUl/mL",
        "meUliml": "mCUl/mL",
        "pg/dl": "µg/dL",
        "pg/dL": "µg/dL",
        "ugldl": "µg/dL"
    }
    for errado, certo in substituicoes.items():
        texto = texto.replace(errado, certo)
    return texto

def extrair_exames(texto: str) -> List[dict]:
    exames = []
    # Regex para encontrar padrões tipo "Cortisol 8,52 µg/dL" ou "Insulina Jejum 4,9 mCUl/mL"
    padrao = re.compile(r'([\w\s]+)[\s:]*([\d,.]+)\s*(µg/dL|mCUl/mL|meUl/mL|meUlimL|mcUl/mL)?', re.IGNORECASE)
    for match in padrao.finditer(texto):
        nome_exame = match.group(1).strip()
        valor = match.group(2).replace(",", ".")
        unidade = match.group(3) if match.group(3) else None
        exames.append({
            "exame": nome_exame,
            "valor": valor,
            "unidade": unidade
        })
    return exames

@app.post("/ocr")
async def ocr(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))

            # OCR melhorado
            raw_text = pytesseract.image_to_string(
                image,
                lang='por',
                config='--psm 6 --oem 3'
            )

            # Correção automática do texto
            texto_corrigido = corrigir_texto(raw_text)

            # Extração de exames estruturados
            exames_extraidos = extrair_exames(texto_corrigido)

            results.append({
                "filename": file.filename,
                "text": texto_corrigido,
                "exames": exames_extraidos
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": f"Erro ao processar o arquivo: {str(e)}"
            })
        finally:
            await file.close()
    return {"results": results}
