
import { useVoiceContext } from "../../context/VoiceContext";

export const VoiceOrb = () => {
  const { state } = useVoiceContext();
  
  // Mapping state to visual styles
  const getOrbStyles = () => {
    switch (state.voice) {
      case "listening":
        return "bg-sahistra-accent scale-110 shadow-[0_0_20px_rgba(217,108,91,0.5)]";
      case "thinking":
        return "bg-blue-400 scale-100 animate-pulse shadow-[0_0_15px_rgba(96,165,250,0.5)]";
      case "speaking":
        return "bg-green-500 scale-110 animate-bounce shadow-[0_0_20px_rgba(34,197,94,0.5)]";
      case "error":
        return "bg-red-500 scale-100";
      case "reconnecting":
        return "bg-orange-400 scale-95 opacity-70 animate-ping";
      case "idle":
      default:
        return "bg-sahistra-text/20 scale-100 hover:bg-sahistra-text/40";
    }
  };

  return (
    <div className="relative flex items-center justify-center w-12 h-12">
      <div 
        className={`w-4 h-4 rounded-full transition-all duration-500 ease-in-out ${getOrbStyles()}`} 
      />
      
      {/* Listening expanding rings */}
      {state.voice === "listening" && (
        <>
          <div className="absolute w-8 h-8 rounded-full border border-sahistra-accent animate-ping opacity-50" />
          <div className="absolute w-12 h-12 rounded-full border border-sahistra-accent animate-ping opacity-25" style={{ animationDelay: '0.2s' }} />
        </>
      )}
    </div>
  );
};
