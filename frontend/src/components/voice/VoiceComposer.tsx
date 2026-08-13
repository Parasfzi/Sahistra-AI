import { useState } from "react";
import { Send, Mic, Square } from "lucide-react";
import { useVoiceContext } from "../../context/VoiceContext";
import { VoiceOrb } from "./VoiceOrb";
import { Waveform } from "./Waveform";

export const VoiceComposer = ({ 
  onSendMessage, 
  onCancel 
}: { 
  onSendMessage: (text: string) => void;
  onCancel: () => void;
}) => {
  const [text, setText] = useState("");
  const { state } = useVoiceContext();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim() && state.connection === "connected") {
      onSendMessage(text);
      setText("");
    }
  };

  const getStatusText = () => {
    switch(state.voice) {
      case "listening": return "Listening...";
      case "thinking": return "Thinking...";
      case "speaking": return "Speaking...";
      case "reconnecting": return "Reconnecting to Brain...";
      case "error": return "Connection error";
      case "idle":
      default: return "Talk to Sahistra...";
    }
  };

  return (
    <div className="absolute bottom-0 left-0 right-0 bg-linear-to-t from-sahistra-bg via-sahistra-bg to-transparent pt-12 pb-8 px-6 md:px-12 lg:px-32">
      <div className="max-w-3xl mx-auto">
        <form 
          onSubmit={handleSubmit}
          className="flex items-center gap-3 bg-sahistra-card rounded-full p-2 pr-4 shadow-sm border border-sahistra-text/5 focus-within:border-sahistra-text/20 transition-colors"
        >
          {/* Orb replaces standard mic icon in minimal UI */}
          <button 
            type="button" 
            className="shrink-0 relative group"
            title="Voice is controlled by desktop agent"
          >
            <VoiceOrb />
          </button>
          
          <div className="flex-1 flex flex-col justify-center">
            {state.voice === 'listening' || state.voice === 'speaking' ? (
              <div className="flex items-center gap-4 h-10 px-2">
                <span className="text-sm font-medium text-sahistra-text/60 animate-pulse">
                  {getStatusText()}
                </span>
                <Waveform />
              </div>
            ) : (
              <input
                type="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder={getStatusText()}
                disabled={state.connection !== "connected"}
                className="w-full h-10 bg-transparent outline-none text-sahistra-text placeholder-sahistra-text/40 text-sm md:text-base px-2 disabled:opacity-50"
              />
            )}
          </div>

          <div className="shrink-0 flex items-center gap-2">
            {(state.voice === 'thinking' || state.voice === 'speaking') && (
              <button
                type="button"
                onClick={onCancel}
                className="p-2 text-sahistra-text/40 hover:text-red-500 transition-colors"
              >
                <Square size={20} className="fill-current" />
              </button>
            )}
            
            {text.trim() && (
              <button
                type="submit"
                disabled={state.connection !== "connected"}
                className="p-2 text-sahistra-bg bg-sahistra-text rounded-full hover:bg-sahistra-text/90 transition-transform active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
              >
                <Send size={16} />
              </button>
            )}
            
            {!text.trim() && state.voice === 'idle' && (
              <button
                type="button"
                className="p-2 text-sahistra-text/40 hover:text-sahistra-accent transition-colors cursor-default"
                title="Microphone is controlled by the Python desktop agent"
              >
                <Mic size={20} />
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};


