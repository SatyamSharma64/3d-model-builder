import { useState } from "react";
import { useDispatch } from "react-redux";
import { sendMessage } from "@/features/chat/chatSlice";
import { useSocketCommand } from "@/hooks/useSocketCommand";
import type { AppDispatch } from "@/app/store";

export default function PromptInput({projectId}: { projectId: string}) {
  const [input, setInput] = useState("");
  const [isCreatingProject, setIsCreatingProject] = useState(false);
  const dispatch = useDispatch<AppDispatch>();
  const { sendCommand } = useSocketCommand();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    try {
      dispatch(sendMessage({projectId, content: input}));
      sendCommand(projectId, input);
      setInput("");
    } catch (error) {
      console.error("Error creating project:", error);
      setIsCreatingProject(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        className="flex-1 border p-2 rounded"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Describe your 3D design task..."
        disabled={isCreatingProject}
      />
      <button 
        type="submit" 
        className="bg-blue-600 text-white px-4 rounded disabled:opacity-50"
        disabled={isCreatingProject}
      >
        {isCreatingProject ? "Creating..." : "Send"}
      </button>
    </form>
  );
}