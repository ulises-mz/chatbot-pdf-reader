import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import tiktoken

# Carga variables del entorno (.env)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Tarifas por token según el modelo (en USD)
TOKEN_PRICES = {
    "gpt-4-turbo": 0.01 / 1000,
    "gpt-3.5-turbo": 0.0015 / 1000
}

def count_tokens_and_cost(messages, model="gpt-4-turbo"):
    """
    Calcula el total de tokens usados en los mensajes y estima el costo en USD.
    """
    encoding = tiktoken.encoding_for_model(model)

    def message_tokens(message):
        content = message.content if hasattr(message, "content") else ""
        return len(encoding.encode(content))

    total_tokens = sum(message_tokens(msg) for msg in messages)
    cost = round(total_tokens * TOKEN_PRICES.get(model, 0), 6)
    return {
        "total_tokens": total_tokens,
        "estimated_cost_usd": cost
    }

def setup_chatbot(pdf_path):
    """
    Procesa el PDF, lo divide en fragmentos con solapamiento, genera embeddings
    y devuelve el retriever FAISS y el contenido inicial del documento.
    """
    # Cargar y dividir el PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=400,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)

    # Agregar etiquetas para facilitar trazabilidad por sección
    for i, chunk in enumerate(chunks):
        chunk.page_content = f"[Sección {i+1}]\n{chunk.page_content.strip()}"

    # Calcular embeddings y construir la base vectorial
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_db = FAISS.from_documents(chunks, embeddings)

    # Configurar retriever con búsqueda por similitud
    retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 8})

    # Extraer contenido inicial del PDF (primeras páginas)
    intro_content = "\n".join([doc.page_content for doc in documents[:10]])[:8000]

    return retriever, intro_content

def generate_prompt_with_history(user_input, context=None, intro_content=None, memory=None):
    """
    Construye la lista de mensajes para el modelo, usando instrucciones del sistema,
    historial de conversación y contexto relevante del PDF.
    """
    history = memory.load_memory_variables({})["chat_history"] if memory else []

    system_content = (
        "Eres un asistente experto. Sigue estas reglas estrictamente:\n"
        "1. Usa exclusivamente el CONTEXTO proporcionado y el historial completo de la conversación para entender la intención del usuario y construir tu respuesta.\n"
        "2. No debes usar conocimientos previos, entrenamiento general ni información externa que no esté en el contexto o historial.\n"
        "3. Si no encuentras información relevante en el contexto ni en el historial, responde exactamente: 'No tengo información sobre eso'.\n"
        "4. No inventes, infieras ni completes datos por tu cuenta. Si la información no está explícita, no la proporciones.\n"
        "5. Nunca menciones que estás trabajando con documentos, archivos, PDF u otras fuentes. Solo responde directamente al usuario.\n"
        "6. Mantén un tono profesional, claro, empático y responde siempre en el idioma original del usuario.\n"
        "7. Da respuestas coherentes con el historial, manteniendo continuidad en nombres, temas y contexto previo.\n"
        "8. Si el usuario hace una referencia vaga (como 'eso', 'más de eso', 'continúa'), intenta asociarla con la última respuesta válida del asistente.\n"
        "9. No des consejos, explicaciones técnicas ni definiciones que no estén explícitamente respaldadas por el contexto o historial.\n"
        "10. Toda respuesta debe estar en formato **Markdown válido** y estructurado:\n"
        "    - Usa títulos (`#`, `##`, `###`) si aplican.\n"
        "    - Usa listas (`-`, `*`, `1.`) para pasos o elementos.\n"
        "    - Usa negritas (`**texto**`) o itálicas (`*texto*`) según el énfasis.\n"
        "    - Usa bloques de código (```) para fragmentos técnicos o textuales.\n"
        "    - Evita emojis, adornos innecesarios o respuestas con tono informal.\n"
    )

    messages = [SystemMessage(content=system_content)]

    # Agregar historial de conversación previo
    for msg in history:
        messages.append(msg)

    # Obtener contexto del PDF o de la última respuesta válida del asistente
    context_info = context.strip() if context else ""
    if not context_info:
        last_ai = next((m.content for m in reversed(history) if isinstance(m, AIMessage) and m.content.strip()), None)
        if last_ai:
            context_info = f"(Este texto proviene de la respuesta anterior del asistente)\n{last_ai.strip()}"

    # Si sigue sin haber contexto, se devuelve mensaje estándar
    if not context_info.strip():
        return [
            SystemMessage(content=system_content),
            HumanMessage(content="No tengo información sobre eso.")
        ]

    # Inyectar pregunta del usuario junto con contexto
    messages.append(HumanMessage(content=f"""A continuación tienes el historial completo de la conversación y un contexto útil. Usa ambos para responder con precisión.

--- CONTEXTO ---
{context_info}
--- FIN DEL CONTEXTO ---

Pregunta del usuario: {user_input}
"""))

    return messages
