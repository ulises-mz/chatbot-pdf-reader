# Chatbot PDF Reader (React + FastAPI)

Una aplicación web que responde preguntas basadas en el contenido de un archivo PDF usando OpenAI y FastAPI.

---

## 🖼 Vista previa de la interfaz

![Vista previa de la app](Preview.png)

---

## 🚀 Características

- 🧠 Respuestas con contexto del PDF cargado
- 💬 Chat multi-sesión con historial y exportación
- ⏱️ Streaming de respuestas en tiempo real (SSE)
- 📊 Cálculo de tokens y costo estimado por mensaje
- 📎 Exportación a Markdown
- 🧾 Markdown rendering para respuestas AI

---

## 🧪 Endpoints útiles

- `GET /health` – Verifica que el backend esté funcionando
- `POST /chat` – Enviar mensaje y obtener respuesta
- `GET /debug/chat/{conversation_id}` – Ver historial de conversación
- `DELETE /debug/conversations/{conversation_id}` – Eliminar sesión

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

## 🔐 Variables de entorno

### Backend `.env.example`

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PDF_PATH=backend/docs/PB_TravelAbility_DI-v3.pdf
```

### Frontend `.env.example` (opcional)

```env
REACT_APP_API_URL=http://localhost:8000
```

---

## 📦 Dependencias principales

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

### Frontend `package.json`

```json
"dependencies": {
  "@testing-library/dom": "^10.4.0",
  "@testing-library/jest-dom": "^6.6.3",
  "@testing-library/react": "^16.3.0",
  "@testing-library/user-event": "^13.5.0",
  "react": "^19.1.0",
  "react-dom": "^19.1.0",
  "react-icons": "^5.5.0",
  "react-markdown": "^10.1.0",
  "react-scripts": "5.0.1",
  "web-vitals": "^2.1.4"
},
"devDependencies": {
  "autoprefixer": "^10.4.21",
  "postcss": "^8.5.6",
  "tailwindcss": "^4.1.10"
}
```

---

## 📝 Notas

- Para cambiar el archivo PDF de contexto, reemplaza el documento ubicado en `backend/docs`.

- El archivo PDF se carga al iniciar el backend.
- El chatbot **solo responde preguntas relacionadas con el contenido del PDF**.
- Las respuestas usan **formato Markdown** para mayor legibilidad.
- La memoria de conversación se maneja en memoria (sin base de datos).

---

## ✅ Estado del proyecto

✅ Funcional en local  
✅ Compatible con VPS o Render  
✅ Modular y extensible

---

## 📄 Licencia

MIT © 2025
