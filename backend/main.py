import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from backend.utils.chatbot_setup import setup_chatbot, generate_prompt_with_history, count_tokens_and_cost
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from fastapi.middleware.cors import CORSMiddleware

# Carga las variables de entorno desde .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Instancia principal de la aplicación FastAPI
app = FastAPI()

# Configuración de CORS para permitir llamadas desde el frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialización: carga el PDF, genera chunks y embeddings
pdf_path = os.path.join("backend", "docs", "PB_TravelAbility_DI-v3.pdf")
retriever, intro_content = setup_chatbot(pdf_path)

# Diccionario de sesiones activas, manejadas en memoria
sessions = {}  # { conversation_id: ConversationBufferMemory }

# Endpoint de prueba para verificar si el backend está activo
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Endpoint principal que maneja la conversación y devuelve respuestas por SSE
@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_input = body.get("message", "")
    conversation_id = body.get("conversation_id", "default")

    print(f"📨 Petición recibida — conversation_id: {conversation_id}")
    print(f"🗣️ Mensaje del usuario: {user_input}")

    # Detecta saludos comunes y responde sin invocar el modelo
    if user_input.strip().lower() in ["hola", "buenas", "hey", "hi"]:
        print("👋 Respuesta automática a saludo.")
        return StreamingResponse(
            iter([
                f"data: {json.dumps({'type': 'content', 'content': '¡Hola! Puedes preguntarme sobre el contenido del documento y con gusto te ayudaré.'})}\n\n",
                'data: {"type": "done"}\n\n'
            ]),
            media_type="text/event-stream"
        )

    # Si no existe una sesión, se crea una nueva
    if conversation_id not in sessions:
        print(f"🧠 Nueva sesión creada para: {conversation_id}")
        sessions[conversation_id] = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
    else:
        print(f"📂 Sesión existente usada para: {conversation_id}")

    memory = sessions[conversation_id]
    memory.chat_memory.add_user_message(user_input)

    # Imprime el historial actual de la conversación para debugging
    print("📜 Historial de conversación actual:")
    for msg in memory.chat_memory.messages:
        role = "👤 Usuario" if isinstance(msg, HumanMessage) else "🤖 Asistente"
        print(f"  {role}: {msg.content[:80]}")

    # Detecta si el usuario está pidiendo una descripción general
    meta_keywords = ["sobre qué tienes", "qué sabes", "temas", "información tienes", "de qué trata", "resumen", "alcance"]
    is_meta = any(kw in user_input.lower() for kw in meta_keywords)
    print(f"🔍 Es pregunta meta: {is_meta}")

    # Busca los fragmentos relevantes en el índice si no es meta
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

    # Si no hay contexto y no es pregunta meta, se evita llamar al modelo
    if not context and not is_meta:
        print("⛔ Sin contexto y no es meta → respuesta neutra.")
        return StreamingResponse(
            iter([
                f"data: {json.dumps({'type': 'content', 'content': 'No tengo información sobre eso.'})}\n\n",
                'data: {"type": "done"}\n\n'
            ]),
            media_type="text/event-stream"
        )

    # Construcción de mensajes para enviar al modelo, incluyendo contexto e historial
    messages = generate_prompt_with_history(user_input, context, intro_content, memory)
    print(f"🧾 Tokens enviados al modelo: {len(messages)} mensajes")

    # Inicializa el modelo con streaming habilitado
    llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0.2, streaming=True)

    # Generador asincrónico que produce la respuesta por SSE
    async def stream_response():
        response_accumulated = ""
        try:
            async for chunk in llm.astream(messages):
                if chunk.content:
                    response_accumulated += chunk.content
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk.content})}\n\n"

            # Guarda la respuesta completa en la memoria de la conversación
            if response_accumulated.strip():
                memory.chat_memory.add_ai_message(response_accumulated)

                # Calcula y envía el uso de tokens y el costo estimado
                usage_info = count_tokens_and_cost(messages, model="gpt-4-turbo")
                yield f"data: {json.dumps({'type': 'usage', 'tokens': usage_info})}\n\n"

            yield 'data: {"type": "done"}\n\n'

        except Exception as e:
            print(f"❌ Error durante streaming: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")

# Endpoint para depurar una sesión individual y obtener el historial completo
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

# Endpoint para listar todas las sesiones activas con su historial
@app.get("/debug/conversations")
def list_all_conversations():
    all_histories = []
    for conv_id, memory in sessions.items():
        chat = memory.chat_memory.messages
        history = []
        for msg in chat:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            history.append({ "role": role, "content": msg.content })

        all_histories.append({
            "conversation_id": conv_id,
            "message_count": len(history),
            "history": history
        })

    return {"conversations": all_histories}

# Endpoint para eliminar una sesión específica
@app.delete("/debug/conversations/{conversation_id}")
def delete_conversation(conversation_id: str):
    if conversation_id in sessions:
        del sessions[conversation_id]
        print(f"🗑️ Conversación '{conversation_id}' eliminada del backend.")
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Conversación no encontrada")
