export async function streamChatMessage(message, conversationId, onChunk, onDone, onError) {
  try {
    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        conversation_id: conversationId, // ✅ usamos el valor dinámico
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
        const payload = JSON.parse(line.replace("data: ", ""));
        if (payload.type === "content") {
          accumulated += payload.content;
          onChunk(accumulated);
        } else if (payload.type === "done") {
          onDone();
        }
      }
    }
  } catch (err) {
    onError(err);
  }
}
