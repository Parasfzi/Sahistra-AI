
import { useVoiceContext } from "../../context/VoiceContext";

export const Waveform = () => {
  const { state } = useVoiceContext();
  
  if (state.voice !== "listening" && state.voice !== "speaking") {
    return null;
  }
  
  // Decorative visual representation only, no real audio binding.
  return (
    <div className="flex items-center gap-1 h-6">
      {[1, 2, 3, 4, 5].map((i) => (
        <div 
          key={i} 
          className={`w-1 rounded-full ${state.voice === 'speaking' ? 'bg-green-500' : 'bg-sahistra-accent'}`}
          style={{
            height: `${Math.max(20, Math.random() * 100)}%`,
            animation: `pulse ${0.5 + (i * 0.1)}s infinite alternate ease-in-out`
          }}
        />
      ))}
    </div>
  );
};
