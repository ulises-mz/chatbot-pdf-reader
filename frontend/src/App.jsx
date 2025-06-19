import ChatPage from "./pages/ChatPage";
import { useRef } from "react";

function App() {
  const conversationIdRef = useRef(crypto.randomUUID());

  return <ChatPage conversationId={conversationIdRef.current} />;
}

export default App;
