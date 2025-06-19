import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# Configurar API Key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Memoria global para mantener el historial de conversación
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def setup_chatbot(pdf_path):
    # 1. Cargar y dividir el PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    
    # 2. Crear base de datos vectorial
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    vector_db = FAISS.from_documents(chunks, embeddings)
    
    # 3. Configurar sistema de recuperación
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    
    # 4. Guardar contenido inicial para preguntas meta
    intro_content = "\n".join([doc.page_content for doc in documents[:2]])[:1500]
    
    return retriever, intro_content

def generate_prompt_with_history(user_input, context=None, intro_content=None):
    # Obtener historial de conversación
    history = memory.load_memory_variables({})["chat_history"]
    
    # Construir mensajes de sistema con reglas estrictas
    system_content = (
        "Eres un asistente experto. Sigue estas reglas estrictamente:\n"
        "1. Responde saludos y preguntas generales de forma natural pero breve\n"
        "2. Para cualquier pregunta técnica o específica, usa SOLO la información del contexto proporcionado\n"
        "3. Si el contexto no contiene información relevante, responde: 'No tengo información sobre eso'\n"
        "4. Nunca menciones que tienes un documento, PDF o fuente externa\n"
        "5. Nunca inventes información que no esté en el contexto\n"
        "6. Para preguntas sobre tu conocimiento o alcance, usa la información introductoria\n"
        "7. Mantén un tono profesional y amable\n"
        "8. Considera el historial de conversación para dar respuestas coherentes"
    )
    
    messages = [SystemMessage(content=system_content)]
    
    # Agregar historial de conversación
    for msg in history:
        if isinstance(msg, HumanMessage):
            messages.append(HumanMessage(content=msg.content))
        elif isinstance(msg, AIMessage):
            messages.append(AIMessage(content=msg.content))
    
    # Manejar preguntas meta sobre el conocimiento
    if any(keyword in user_input.lower() for keyword in ["sobre qué tienes", "qué sabes", "alcance", "temas", "información tienes"]):
        messages.append(HumanMessage(
            content=f"Información introductoria: {intro_content}\n\nPregunta: {user_input}"
        ))
    # Manejar otras preguntas
    elif context:
        messages.append(HumanMessage(
            content=f"Información relevante: {context}\n\nPregunta: {user_input}"
        ))
    else:
        messages.append(HumanMessage(
            content=f"No hay información relevante disponible\n\nPregunta: {user_input}"
        ))
    
    return messages

def main():
    # Usar ruta segura multiplataforma
    pdf_path = os.path.join("backend", "docs", "PB_TravelAbility_DI-v3.pdf")
    
    # Configurar retriever y contenido introductorio
    knowledge_retriever, intro_content = setup_chatbot(pdf_path)
    
    # Obtener tema del documento para saludo personalizado
    doc_topic = os.path.basename(pdf_path).split('.')[0].replace('_', ' ')
    print(f"¡Hola! Soy tu asistente experto en {doc_topic}. ¿En qué puedo ayudarte?")
    
    while True:
        try:
            user_input = input("\nUsuario: ")
            if user_input.lower() in ["salir", "exit", "adiós", "bye"]:
                print("\nChatbot: ¡Hasta luego! Que tengas un buen día.")
                break
            
            # Guardar pregunta en memoria
            memory.chat_memory.add_user_message(user_input)
            
            # Manejar preguntas meta sin buscar en todo el documento
            if any(keyword in user_input.lower() for keyword in ["sobre qué tienes", "qué sabes", "alcance", "temas", "información tienes"]):
                context = None
            else:
                # Obtener conocimiento relevante para otras preguntas
                context_docs = knowledge_retriever.get_relevant_documents(user_input)
                context = "\n".join([doc.page_content[:500] + "..." for doc in context_docs])
            
            # Generar prompt con historial
            messages = generate_prompt_with_history(user_input, context, intro_content)
            
            # Generar respuesta usando el modelo
            llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0.2)
            response = llm.invoke(messages)
            
            # Guardar respuesta en memoria y mostrar
            memory.chat_memory.add_ai_message(response.content)
            print(f"\nChatbot: {response.content}")
        
        except KeyboardInterrupt:
            print("\n\nPrograma terminado por el usuario")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()