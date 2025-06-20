export default function InputBar({ input, setInput, onSend, loading }) {
  return (
    <div className="input-bar">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && onSend()}
        placeholder="Type your message..."
        disabled={loading}
      />
      <button onClick={onSend} disabled={loading}>
        Send
      </button>
    </div>
  );
}
