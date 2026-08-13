import { useEffect, useRef } from "react";
import { useVoiceContext } from "../../context/VoiceContext";
import { UserMessage } from "./UserMessage";
import { AssistantMessage } from "./AssistantMessage";

export const ChatContainer = () => {
  const { state } = useVoiceContext();
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [state.conversation, state.voice]);

  return (
    <div className="flex-1 overflow-y-auto px-6 py-8 md:px-12 lg:px-32 scroll-smooth">
      <div className="max-w-3xl mx-auto space-y-8 pb-32">
        {state.conversation.length === 0 ? (
          <div className="h-full flex items-center justify-center text-sahistra-text/40 pt-32">
            <p className="text-center">How can I help you today?</p>
          </div>
        ) : (
          state.conversation.map((msg) =>
            msg.role === "user" ? (
              <UserMessage key={msg.id} content={msg.content} />
            ) : (
              <AssistantMessage key={msg.id} content={msg.content} isStreaming={msg.isStreaming} />
            )
          )
        )}
        
        {state.voice === "thinking" && !state.conversation[state.conversation.length - 1]?.isStreaming && (
          <div className="flex items-center gap-2 text-sahistra-text/40 text-sm ml-4">
            <div className="w-1.5 h-1.5 rounded-full bg-sahistra-accent animate-bounce" />
            <div className="w-1.5 h-1.5 rounded-full bg-sahistra-accent animate-bounce" style={{ animationDelay: '0.2s' }} />
            <div className="w-1.5 h-1.5 rounded-full bg-sahistra-accent animate-bounce" style={{ animationDelay: '0.4s' }} />
          </div>
        )}
        
        <div ref={endOfMessagesRef} />
      </div>
    </div>
  );
};


