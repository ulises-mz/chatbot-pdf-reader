/**
 * Envía un mensaje al backend y procesa la respuesta por streaming (SSE).
 *
 * @param {string} message - Mensaje del usuario.
 * @param {string} conversationId - ID de la conversación activa.
 * @param {function} onChunk - Callback que recibe cada fragmento parcial acumulado.
 * @param {function} onDone - Callback cuando finaliza la respuesta.
 * @param {function} onError - Callback en caso de error durante la conexión.
 */
export async function streamChatMessage(
  message,
  conversationId,
  onChunk,
  onDone,
  onError
) {
  try {
    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let accumulated = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        onDone();
        break;
      }

      const text = decoder.decode(value, { stream: true });
      const lines = text.split("\n").filter((line) => line.startsWith("data:"));

      for (const line of lines) {
        const jsonStr = line.replace("data: ", "").trim();
        if (!jsonStr) continue;

        let payload;
        try {
          payload = JSON.parse(jsonStr);
        } catch (err) {
          console.error("❌ Error parsing stream JSON:", err, jsonStr);
          continue;
        }

        if (payload.type === "content") {
          // Se acumula el texto parcial y se envía al frontend
          accumulated += payload.content;
          onChunk(accumulated);
        } else if (payload.type === "usage") {
          // Enviar el payload completo como string para visualización
          onChunk(JSON.stringify(payload));
        } else if (payload.type === "done") {
          onDone();
        }
      }
    }
  } catch (err) {
    onError(err);
  }
}

/**
 * Consulta todas las conversaciones almacenadas en el backend.
 *
 * @returns {Promise<Array>} - Lista de conversaciones con su historial.
 */
export async function fetchAllConversations() {
  const response = await fetch("http://localhost:8000/debug/conversations");
  const data = await response.json();
  return data.conversations; // contiene [{ conversation_id, history, ... }, ...]
}

/**
 * Elimina una conversación específica del backend.
 *
 * @param {string} conversationId - ID de la conversación a eliminar.
 * @throws {Error} - Lanza error si no fue posible eliminarla.
 */
export async function deleteConversation(conversationId) {
  const res = await fetch(
    `http://localhost:8000/debug/conversations/${conversationId}`,
    {
      method: "DELETE",
    }
  );
  if (!res.ok) {
    throw new Error("No se pudo eliminar la conversación.");
  }
}
