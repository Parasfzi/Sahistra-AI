export type MessageType = "transcript" | "response_start" | "response_chunk" | "response_end" | "error";

export interface OutboundMessage {
  type: "transcript" | "cancel";
  text?: string;
  session_id?: string;
}

export interface InboundMessage {
  type: MessageType;
  turn_id: string;
  delta?: string;
  full_text?: string;
  code?: string;
  message?: string;
}

export type ConnectionState = "disconnected" | "connecting" | "connected";
export type VoiceState = "idle" | "listening" | "thinking" | "speaking" | "error" | "reconnecting";

export interface ConversationTurn {
  id: string;
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}



