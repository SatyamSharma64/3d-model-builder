import { useEffect, useRef, useState, useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { receiveMessage } from "../features/chat/chatSlice";
import type { RootState } from "@/app/store";
import { setPreviewUrl } from "@/features/projects/projectSlice";

const MAX_RECONNECT_ATTEMPTS = 5;

interface JobStartedMessage {
  type: "job_started";
  job_id: string;
  project_id: string;
}

interface JobInProgressMessage{
    type: "agent_tool_call",
    job_id: string,
    tool: string,
    input: any,
    output: any,
    project_id: string
}
interface JobCompletedMessage {
  type: "job_completed";
  job_id: string;
  project_id: string;
  result: any;
  base64data: string;
}

interface JobFailedMessage {
  type: "job_failed";
  job_id: string;
  project_id: string;
  error: string;
}

type WebSocketMessage = JobStartedMessage | JobInProgressMessage | JobCompletedMessage | JobFailedMessage;

export const useSocketCommand = () => {
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  const dispatch = useDispatch();
  const user = useSelector((state: RootState) => state.auth.user);

  const [isConnected, setIsConnected] = useState(false);
  const [socketError, setSocketError] = useState<Event | null>(null);

  const cleanup = () => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
    setIsConnected(false);
    setSocketError(null);
  };

  const handleWebSocketMessage = useCallback((rawData: string) => {
    try {
      const data: WebSocketMessage = JSON.parse(rawData);
      console.log("WS recieved data:", data);
      switch (data.type) {
        case "job_started": {
          const { job_id, project_id } = data;
          console.log(`Job Started: ${job_id}`);
          dispatch(receiveMessage({
            projectId: project_id,
            message: {
            sender: "system", 
            content: `Job started: ${job_id}`,
            timestamp: new Date().toISOString() 
          }}));
          break;
        }

        case "agent_tool_call": {
          const { job_id, project_id, tool, input, output } = data;
          console.log(`Job in progress: ${job_id}`);
          dispatch(receiveMessage({
            projectId: project_id,
            message: {
            sender: "ai",
            content: `Tool: ${tool}, Input: ${input}, Output: ${output}`,
            timestamp: new Date().toISOString() 
          }}));
          break;
        }

        case "job_completed": {
          const { job_id, project_id, result, base64data } = data;
          console.log(`Job Completed: ${job_id}`);
          dispatch(receiveMessage({
            projectId: project_id,
            message: {
            sender: "ai",
            content: `Result: ${result}`,
            timestamp: new Date().toISOString() 
          }}));

          dispatch(
            setPreviewUrl({
              projectId: project_id,
              url: base64data,
            }));
        
          break;
        }

        case "job_failed": {
          const { job_id, project_id, error } = data;
          console.log(`Job Failed: ${job_id}`);
          dispatch(receiveMessage({
            projectId: project_id,
            message: { 
            sender: "system", 
            content: error,
            timestamp: new Date().toISOString() 
          }}));
          break;
        }

        default:
          console.warn("Unknown message type:", data);
      }
    } catch (e) {
      console.error("Failed to parse WebSocket message:", e);
    }
  }, [dispatch])

  const connect = useCallback(() => {
    if (!user?._id) return;

    const userId = user._id;
    console.log("from useSocket line 32:",userId);

    if (
      socketRef.current &&
      socketRef.current.readyState !== WebSocket.CLOSED &&
      socketRef.current.readyState !== WebSocket.CLOSING
    ) {
      console.log("WebSocket already open or opening, skipping connect.");
      return;
    }

    const socket = new WebSocket(`${process.env.WS_URL}${userId}`);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("MCP WebSocket connected");
      reconnectAttempts.current = 0;
      setIsConnected(true);
      setSocketError(null);
    };

    socket.onmessage = (event) => {
      console.log("WebSocket message received:", event.data);
      handleWebSocketMessage(event.data);
    };

    socket.onclose = (event) => {
      console.warn("WebSocket closed:", event.reason);
      setIsConnected(false);
      if (!event.wasClean) attemptReconnect();
    };

    socket.onerror = (event) => {
      console.error("WebSocket error:", event);
      setSocketError(event);
      socket.close(); 
    };
  }, [dispatch, user?._id]);

  const attemptReconnect = () => {
    if (reconnectAttempts.current >= MAX_RECONNECT_ATTEMPTS) {
      console.warn("Max reconnect attempts reached. Giving up.");
      return;
    }

    const timeout = Math.pow(2, reconnectAttempts.current) * 1000; 
    reconnectAttempts.current += 1;

    console.log(`Reconnecting in ${timeout / 1000}s... (Attempt ${reconnectAttempts.current})`);

    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }

    reconnectTimeout.current = setTimeout(() => {
      connect();
    }, timeout);
  };

  useEffect(() => {
    console.log("trying to connect to ws on line 98", user);
    const delay = setTimeout(() => {
      if (user?._id) {
        console.log("sent for connection line 101");
        connect();
      }
    }, 500); 

    return () => {
      clearTimeout(delay);
    };
  }, [connect, user?._id]);

  useEffect(() => {
    return () => {
      cleanup();
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, []);

  const sendCommand = useCallback((projectId: any, command: any) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const payload = {
      project_id: projectId,
      prompt: command,
    };
    socketRef.current.send(JSON.stringify(payload));
    } else {
      console.warn("WebSocket not open. Cannot send:", command);
    }
  }, []);

  return {
    socket: socketRef.current,
    isConnected,
    socketError,
    sendCommand,
  };
};
