import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# Cargar claves del entorno
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def setup_chatbot(pdf_path):
    # 1. Cargar y dividir el PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=400,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)

    # Añadir etiquetas por sección al inicio de cada chunk
    for i, chunk in enumerate(chunks):
        chunk.page_content = f"[Sección {i+1}]\n{chunk.page_content.strip()}"

    # 2. Crear base de datos vectorial
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    vector_db = FAISS.from_documents(chunks, embeddings)

    # 3. Configurar sistema de recuperación mejorado
    retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={
        "k": 8
    })

    # 4. Ampliar contenido introductorio (meta)
    intro_content = "\n".join([doc.page_content for doc in documents[:10]])[:8000]

    return retriever, intro_content

def generate_prompt_with_history(user_input, context=None, intro_content=None, memory=None):
    history = memory.load_memory_variables({})["chat_history"] if memory else []

    system_content = (
        "Eres un asistente experto. Sigue estas reglas estrictamente:\n"
        "1. Usa exclusivamente el CONTEXTO proporcionado y el historial completo de la conversación para entender la intención del usuario y construir tu respuesta.\n"
        "2. No debes usar conocimientos previos, entrenamiento general, ni información externa que no esté en el contexto o historial.\n"
        "3. Si no encuentras información relevante en el contexto ni en el historial, responde con exactitud: 'No tengo información sobre eso'.\n"
        "4. No inventes, infieras ni completes datos por tu cuenta. Si la información no está explícita, no la proporciones.\n"
        "5. Nunca menciones que estás trabajando con documentos, archivos, PDF u otras fuentes. Solo responde directamente al usuario.\n"
        "6. Mantén un tono profesional, claro, empático y responde siempre en el idioma original del usuario.\n"
        "7. Da respuestas coherentes con el historial, manteniendo continuidad en nombres, temas y contexto previo.\n"
        "8. Si el usuario hace una referencia vaga (como 'eso', 'más de eso', 'continúa'), intenta asociarla con la última respuesta válida del asistente.\n"
        "9. No des consejos, explicaciones técnicas o definiciones que no estén explícitamente respaldadas por el contexto o historial.\n"
    )


    messages = [SystemMessage(content=system_content)]

    for msg in history:
        messages.append(msg)

    # Construir contexto inteligente
    context_info = context.strip() if context else ""

    # Si no hay contexto del documento, intenta usar la última respuesta válida del asistente
    if not context_info:
        last_ai = next((m.content for m in reversed(history) if isinstance(m, AIMessage) and m.content.strip()), None)
        if last_ai:
            context_info = f"(Este texto proviene de la respuesta anterior del asistente)\n{last_ai.strip()}"

    # Validación final: si sigue sin haber contenido útil, retornar mensaje estándar
    if not context_info.strip():
        return [
            SystemMessage(content=system_content),
            HumanMessage(content="No tengo información sobre eso.")
        ]

    # Añadir mensaje final con contexto incluido
    messages.append(HumanMessage(content=f"""A continuación tienes el historial completo de la conversación y un contexto útil. Usa ambos para responder con precisión.

--- CONTEXTO ---
{context_info}
--- FIN DEL CONTEXTO ---

Pregunta del usuario: {user_input}
"""))

    return messages
