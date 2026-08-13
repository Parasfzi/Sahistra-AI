
import { useVoiceContext } from "../../context/VoiceContext";

export const StatusBar = () => {
  const { state } = useVoiceContext();

  return (
    <div className="absolute top-4 right-4 flex items-center gap-4 px-4 py-2 bg-sahistra-card/80 backdrop-blur-sm rounded-full text-xs font-medium text-sahistra-text/70">
      <div className="flex items-center gap-1.5">
        <div className={`w-2 h-2 rounded-full ${state.connection === 'connected' ? 'bg-green-500' : 'bg-red-500 animate-pulse'}`} />
        <span>{state.connection === 'connected' ? 'Connected' : 'Reconnecting...'}</span>
      </div>
      <div className="w-px h-3 bg-sahistra-text/10" />
      <div className="flex items-center gap-1.5 capitalize">
        <div className={`w-2 h-2 rounded-full ${state.voice === 'idle' ? 'bg-gray-400' : state.voice === 'thinking' ? 'bg-blue-400 animate-pulse' : state.voice === 'error' ? 'bg-red-500' : 'bg-green-500'}`} />
        <span>{state.voice}</span>
      </div>
    </div>
  );
};
