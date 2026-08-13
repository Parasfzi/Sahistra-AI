
import { VoiceProvider } from './context/VoiceContext';
import { MainLayout } from './components/layout/MainLayout';
import { Sidebar } from './components/sidebar/Sidebar';
import { ChatContainer } from './components/chat/ChatContainer';
import { VoiceComposer } from './components/voice/VoiceComposer';
import { StatusBar } from './components/status/StatusBar';
import { useWebSocket } from './hooks/useWebSocket';

// Internal component that uses the context
const SahistraApp = () => {
  const { sendTranscript, cancelGeneration } = useWebSocket();

  return (
    <MainLayout
      sidebar={<Sidebar />}
      main={
        <>
          <StatusBar />
          <ChatContainer />
          <VoiceComposer 
            onSendMessage={sendTranscript} 
            onCancel={cancelGeneration} 
          />
        </>
      }
    />
  );
};

// Root component that provides the context
function App() {
  return (
    <VoiceProvider>
      <SahistraApp />
    </VoiceProvider>
  );
}

export default App;
