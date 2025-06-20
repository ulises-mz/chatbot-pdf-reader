export function exportConversationToMarkdown(messages, filename = "chat.md") {
  const content = messages
    .map((msg) => {
      const role =
        msg.type === "user" || msg.role === "user"
          ? "Usuario"
          : "Asistente";
      return `**${role}:**\n${msg.content}\n`;
    })
    .join("\n---\n\n");

  const blob = new Blob([content], { type: "text/markdown;charset=utf-8;" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
