from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from backend.utils.pdf_loader import load_pdf_text_chunks
from backend.utils.embeddings import get_embedding, cosine_similarity
import os, json
import numpy as np
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Cargar y embeddizar el PDF
pdf_path = os.getenv("PDF_PATH", "")
chunks = load_pdf_text_chunks(pdf_path)
chunk_embeddings = [get_embedding(chunk) for chunk in chunks]

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/chat")
async def chat(request: Request):
    try:
        body = await request.body()
        data = json.loads(body.decode("utf-8"))
        user_message = data.get("message", "")
        user_embedding = get_embedding(user_message)

        # Calcular similitud
        scores = [cosine_similarity(user_embedding, emb) for emb in chunk_embeddings]
        top_chunks = [chunks[i] for i in np.argsort(scores)[-3:][::-1]]  # top 3

        # Crear prompt
        prompt = f"Contexto relevante del PDF:\n{''.join(top_chunks)}\n\nUsuario: {user_message}\nIA:"

        def generate():
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield f"data: {chunk.choices[0].delta.content}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        return {"error": str(e)}
