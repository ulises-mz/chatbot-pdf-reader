export default function MessageBubble({ content, type }) {
  return (
    <div className={`message ${type}`}>
      {content}
    </div>
  );
}
