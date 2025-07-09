import { useSelector } from "react-redux";
import { selectMessagesForProject, selectLoadingForProject } from "@/features/chat/chatSelectors";
import type { RootState } from "@/app/store";

export default function MessageList({projectId}: { projectId: string}) {
  const messages = useSelector((state: RootState) => selectMessagesForProject(state, projectId!));
  const loading = useSelector((state: RootState) => selectLoadingForProject(state, projectId!));

  return (
    <div className="h-40 overflow-y-auto mb-2 space-y-2">
      {messages.map((msg, idx) => (
        <div
          key={idx}
          className={`text-sm p-2 rounded ${
            msg.sender === "user" ? "bg-blue-100 text-blue-900" : "bg-gray-200"
          }`}
        >
          <strong>{msg.sender === "user" ? "You" : msg.sender === "ai" ? "AI" : "System"}:</strong> {msg.content}
        </div>
      ))}
      {loading && <p className="text-sm italic text-gray-500">Thinking...</p>}
    </div>
  );
}
