import React, { createContext, useContext, useReducer, ReactNode } from "react";
import type { ConnectionState, VoiceState, ConversationTurn } from "../types/websocket";

interface State {
  connection: ConnectionState;
  voice: VoiceState;
  conversation: ConversationTurn[];
}

type Action =
  | { type: "SET_CONNECTION"; payload: ConnectionState }
  | { type: "SET_VOICE"; payload: VoiceState }
  | { type: "ADD_MESSAGE"; payload: ConversationTurn }
  | { type: "APPEND_CHUNK"; payload: { id: string; chunk: string } }
  | { type: "FINISH_MESSAGE"; payload: { id: string; fullText?: string } }
  | { type: "CLEAR_CONVERSATION" };

const initialState: State = {
  connection: "disconnected",
  voice: "idle",
  conversation: [],
};

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "SET_CONNECTION":
      return { ...state, connection: action.payload };
    case "SET_VOICE":
      return { ...state, voice: action.payload };
    case "ADD_MESSAGE":
      return { ...state, conversation: [...state.conversation, action.payload] };
    case "APPEND_CHUNK":
      return {
        ...state,
        conversation: state.conversation.map((msg) =>
          msg.id === action.payload.id
            ? { ...msg, content: msg.content + action.payload.chunk }
            : msg
        ),
      };
    case "FINISH_MESSAGE":
      return {
        ...state,
        conversation: state.conversation.map((msg) =>
          msg.id === action.payload.id
            ? { ...msg, content: action.payload.fullText ?? msg.content, isStreaming: false }
            : msg
        ),
      };
    case "CLEAR_CONVERSATION":
      return { ...state, conversation: [] };
    default:
      return state;
  }
}

const VoiceContext = createContext<{
  state: State;
  dispatch: React.Dispatch<Action>;
} | null>(null);

export const VoiceProvider = ({ children }: { children: ReactNode }) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <VoiceContext.Provider value={{ state, dispatch }}>
      {children}
    </VoiceContext.Provider>
  );
};

export const useVoiceContext = () => {
  const context = useContext(VoiceContext);
  if (!context) {
    throw new Error("useVoiceContext must be used within a VoiceProvider");
  }
  return context;
};
