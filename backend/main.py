import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from backend.utils.chatbot_setup import setup_chatbot, generate_prompt_with_history
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from fastapi.middleware.cors import CORSMiddleware

# Cargar claves y entorno
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Habilitar CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar conocimiento al iniciar
pdf_path = os.path.join("backend", "docs", "PB_TravelAbility_DI-v3.pdf")
retriever, intro_content = setup_chatbot(pdf_path)

# Manejo de sesiones
sessions = {}  # { conversation_id: ConversationBufferMemory }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_input = body.get("message", "")
    conversation_id = body.get("conversation_id", "default")

    print(f"📨 Petición recibida — conversation_id: {conversation_id}")
    print(f"🗣️ Mensaje del usuario: {user_input}")

    # Saludo directo
    if user_input.strip().lower() in ["hola", "buenas", "hey", "hi"]:
        print("👋 Respuesta automática a saludo.")
        return StreamingResponse(
            iter([
                f"data: {json.dumps({'type': 'content', 'content': '¡Hola! Puedes preguntarme sobre el contenido del documento y con gusto te ayudaré.'})}\n\n",
                'data: {"type": "done"}\n\n'
            ]),
            media_type="text/event-stream"
        )

    # Obtener o crear memoria para esta sesión
    if conversation_id not in sessions:
        print(f"🧠 Nueva sesión creada para: {conversation_id}")
        sessions[conversation_id] = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
    else:
        print(f"📂 Sesión existente usada para: {conversation_id}")

    memory = sessions[conversation_id]
    memory.chat_memory.add_user_message(user_input)

    # Mostrar historial actual
    print("📜 Historial de conversación actual:")
    for msg in memory.chat_memory.messages:
        role = "👤 Usuario" if isinstance(msg, HumanMessage) else "🤖 Asistente"
        print(f"  {role}: {msg.content[:80]}")

    # Revisar si es una pregunta meta
    meta_keywords = ["sobre qué tienes", "qué sabes", "temas", "información tienes", "de qué trata", "resumen", "alcance"]
    is_meta = any(kw in user_input.lower() for kw in meta_keywords)
    print(f"🔍 Es pregunta meta: {is_meta}")

    # Recuperar documentos relevantes y limpiar texto
    context_docs = retriever.get_relevant_documents(user_input) if not is_meta else []
    context_chunks = [
        doc.page_content.strip()[:500] + "..." for doc in context_docs if doc.page_content.strip()
    ]
    context = "\n".join(context_chunks)
    context = context if context and len(context.strip()) > 50 else None

    if context:
        print(f"📚 Fragmentos contextuales encontrados: {len(context_chunks)}")
    else:
        print("⚠️ No se encontró contexto relevante suficiente.")

    # Bloqueo de respuestas fuera del documento
    if not context and not is_meta:
        print("⛔ Sin contexto y no es meta → respuesta neutra.")
        return StreamingResponse(
            iter([
                f"data: {json.dumps({'type': 'content', 'content': 'No tengo información sobre eso.'})}\n\n",
                'data: {"type": "done"}\n\n'
            ]),
            media_type="text/event-stream"
        )

    # Generar mensajes para el modelo
    messages = generate_prompt_with_history(user_input, context, intro_content, memory)
    print(f"🧾 Tokens enviados al modelo: {len(messages)} mensajes")

    # Modelo de lenguaje
    llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0.2, streaming=True)

    async def stream_response():
        response_accumulated = ""
        try:
            async for chunk in llm.astream(messages):
                if chunk.content:
                    response_accumulated += chunk.content
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk.content})}\n\n"

            # ✅ Guardar respuesta completa solo una vez
            if response_accumulated.strip():
                memory.chat_memory.add_ai_message(response_accumulated)

            yield 'data: {"type": "done"}\n\n'
        except Exception as e:
            print(f"❌ Error durante streaming: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")
@app.get("/debug/chat/{conversation_id}")
def debug_chat(conversation_id: str):
    memory = sessions.get(conversation_id)
    if not memory:
        return {"status": "not_found", "history": []}

    chat = memory.chat_memory.messages
    history = []
    for msg in chat:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        history.append({ "role": role, "content": msg.content })

    return {
        "conversation_id": conversation_id,
        "message_count": len(history),
        "history": history
    }
