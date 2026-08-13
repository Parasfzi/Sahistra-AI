import { useEffect, useRef, useCallback } from "react";
import { useVoiceContext } from "../context/VoiceContext";
import type { InboundMessage, OutboundMessage } from "../types/websocket";

export const useWebSocket = () => {
  const ws = useRef<WebSocket | null>(null);
  const { state, dispatch } = useVoiceContext();
  const activeTurnId = useRef<string | null>(null);

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return;

    const url = import.meta.env.VITE_SAHISTRA_WS_URL;
    const token = import.meta.env.VITE_SAHISTRA_WS_TOKEN;
    
    if (!url || !token) {
      console.error("Missing WebSocket configuration. Check .env variables.");
      return;
    }

    dispatch({ type: "SET_CONNECTION", payload: "connecting" });

    const socket = new WebSocket(`${url}?token=${token}`);

    socket.onopen = () => {
      dispatch({ type: "SET_CONNECTION", payload: "connected" });
      dispatch({ type: "SET_VOICE", payload: "idle" });
    };

    socket.onmessage = (event) => {
      try {
        const data: InboundMessage = JSON.parse(event.data);
        
        if (data.type === "response_start") {
          activeTurnId.current = data.turn_id;
          dispatch({ type: "SET_VOICE", payload: "thinking" });
          dispatch({
            type: "ADD_MESSAGE",
            payload: { id: data.turn_id, role: "assistant", content: "", isStreaming: true },
          });
        } 
        else if (data.type === "response_chunk") {
          dispatch({ type: "SET_VOICE", payload: "thinking" });
          if (data.delta && activeTurnId.current) {
            dispatch({
              type: "APPEND_CHUNK",
              payload: { id: activeTurnId.current, chunk: data.delta },
            });
          }
        } 
        else if (data.type === "response_end") {
          dispatch({ type: "SET_VOICE", payload: "idle" });
          if (activeTurnId.current) {
            dispatch({
              type: "FINISH_MESSAGE",
              payload: { id: activeTurnId.current, fullText: data.full_text },
            });
            activeTurnId.current = null;
          }
        } 
        else if (data.type === "error") {
          console.error("Backend Error:", data.message);
          dispatch({ type: "SET_VOICE", payload: "error" });
          if (activeTurnId.current) {
            dispatch({
              type: "FINISH_MESSAGE",
              payload: { id: activeTurnId.current },
            });
            activeTurnId.current = null;
          }
        }
      } catch (e) {
        console.error("Failed to parse WebSocket message", e);
      }
    };

    socket.onclose = () => {
      dispatch({ type: "SET_CONNECTION", payload: "disconnected" });
      dispatch({ type: "SET_VOICE", payload: "reconnecting" });
      // Reconnect logic can be added here
      setTimeout(connect, 3000);
    };

    socket.onerror = (error) => {
      console.error("WebSocket Error:", error);
      dispatch({ type: "SET_CONNECTION", payload: "disconnected" });
      dispatch({ type: "SET_VOICE", payload: "error" });
    };

    ws.current = socket;
  }, [dispatch]);

  useEffect(() => {
    connect();
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect]);

  const sendTranscript = useCallback((text: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      // Add user message to UI immediately
      const id = "user-" + Date.now().toString();
      dispatch({
        type: "ADD_MESSAGE",
        payload: { id, role: "user", content: text },
      });
      
      // Update voice state to thinking as requested
      dispatch({ type: "SET_VOICE", payload: "thinking" });

      const msg: OutboundMessage = { type: "transcript", text };
      ws.current.send(JSON.stringify(msg));
    }
  }, [dispatch]);

  const cancelGeneration = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      const msg: OutboundMessage = { type: "cancel" };
      ws.current.send(JSON.stringify(msg));
      dispatch({ type: "SET_VOICE", payload: "idle" });
      if (activeTurnId.current) {
        dispatch({ type: "FINISH_MESSAGE", payload: { id: activeTurnId.current }});
        activeTurnId.current = null;
      }
    }
  }, [dispatch]);

  return { sendTranscript, cancelGeneration };
};
