# Chatbot PDF Reader

Una aplicación web que responde preguntas basadas en el contenido de un archivo PDF usando OpenAI y FastAPI.

---

## 🚀 Características

- 🧠 Respuestas con contexto del PDF cargado
- 💬 Chat multi-sesión con historial y exportación
- ⏱️ Streaming de respuestas en tiempo real (SSE)
- 📊 Cálculo de tokens y costo estimado por mensaje
- 📎 Exportación a Markdown

---

## 🗂️ Estructura del proyecto

```
chatbot-pdf-reader/
├── backend/
│   ├── main.py
│   ├── utils/
│   ├── docs/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── .env.example
└── README.md
```

---

## ⚙️ Requisitos

- Node.js (>= 16)
- Python 3.10 o superior
- Cuenta de OpenAI + API Key

---

## 🔧 Instalación y ejecución local

### 1. Backend (FastAPI + OpenAI)

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Asegúrate de tener un archivo `.env` con tus variables reales, basado en `.env.example`.

---

### 2. Frontend (React)

```bash
cd frontend
npm install
npm start
```

Esto abrirá la app en [http://localhost:3000](http://localhost:3000)

---

## 🧪 Endpoints útiles

- `GET /health` – Health check
- `POST /chat` – Enviar mensaje y obtener respuesta
- `GET /debug/chat/{conversation_id}` – Ver historial de una conversación
- `DELETE /debug/conversations/{conversation_id}` – Eliminar sesión

---

## 🔐 Variables de entorno (`.env.example`)

### Backend `.env.example`

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PDF_PATH=backend/docs/PB_TravelAbility_DI-v3.pdf
```

### Frontend `.env.example` (opcional, si usas variables para configurar la URL del backend)

```env
REACT_APP_API_URL=http://localhost:8000
```

---

## 📦 Instalación de dependencias

### Backend `requirements.txt`

```txt
fastapi
uvicorn
python-multipart
python-dotenv
openai
langchain
langchain-community
langchain-openai
tiktoken
PyPDF2
faiss-cpu
numpy
```

### Frontend `package.json` (fragmento)

```json
"dependencies": {
  "axios": "^1.6.0",
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-markdown": "^9.0.0",
  "react-scripts": "5.0.1"
}
```

---

## 📝 Notas

- El archivo PDF se carga al iniciar el backend, no es necesario subirlo manualmente.
- El chatbot **solo responderá preguntas relacionadas al contenido del PDF**.
- Las respuestas usan **Markdown** para mejorar el formato y legibilidad.

---

## ✅ Estado del proyecto

✅ Funcional en local  
✅ Compatible con despliegue en VPS o servicios como Render  
✅ Modular y listo para mejoras

---

## 📄 Licencia

MIT © 2025
