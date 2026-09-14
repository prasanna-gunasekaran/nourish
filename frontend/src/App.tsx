import { useState, useEffect } from 'react';
import { DemoFlowBar } from './components/DemoFlowBar';
import { WhatsAppChat } from './components/WhatsAppChat';
import { Dashboard } from './components/Dashboard';
import type { ChatMessage, DashboardData, AgentActionTrace } from './types';

const API_BASE = 'http://localhost:8000/api';
const USER_ID = 'demo_user';

export function App() {
  const [viewMode, setViewMode] = useState<'split' | 'phone'>('split');
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init_1',
      sender: 'nourish',
      text: "👋 Hi! I'm Nourish, your personal AI nutrition agent right inside WhatsApp.\n\nYou can tell me naturally what you ate (e.g., 'I ate 3 idlis and one vada for breakfast'), ask what you should eat next, or manage your food preferences!",
      timestamp: new Date().toISOString()
    }
  ]);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [recentActionTraces, setRecentActionTraces] = useState<AgentActionTrace[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const fetchDashboard = async () => {
    try {
      const res = await fetch(`${API_BASE}/dashboard/${USER_ID}`);
      if (res.ok) {
        const data = await res.json();
        setDashboardData(data);
      }
    } catch (e) {
      console.warn('Dashboard fetch error:', e);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleSendMessage = async (userText: string) => {
    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      sender: 'user',
      text: userText,
      timestamp: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsProcessing(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: USER_ID, message: userText })
      });

      if (!res.ok) throw new Error('API Error');
      const data = await res.json();

      const agentMsg: ChatMessage = {
        id: `agent_${Date.now()}`,
        sender: 'nourish',
        text: data.reply_text,
        timestamp: new Date().toISOString(),
        meal_data: data.meal_logged,
        confirmation_required: data.confirmation_needed,
        action_traces: data.action_traces
      };

      setMessages((prev) => [...prev, agentMsg]);
      if (data.action_traces) {
        setRecentActionTraces(data.action_traces);
      }

      await fetchDashboard();
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          sender: 'nourish',
          text: '⚠️ Network connection issue. Please ensure the backend server is running on http://localhost:8000.',
          timestamp: new Date().toISOString()
        }
      ]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSendVision = async () => {
    const userMsg: ChatMessage = {
      id: `user_cam_${Date.now()}`,
      sender: 'user',
      text: '📷 [Scanned Food Image: Chicken Biryani & Buttermilk]',
      timestamp: new Date().toISOString()
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsProcessing(true);

    try {
      const res = await fetch(`${API_BASE}/chat/vision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: USER_ID, message: 'image', image_base64: 'sample_base64' })
      });
      if (!res.ok) throw new Error('Vision API error');
      const data = await res.json();

      const agentMsg: ChatMessage = {
        id: `agent_cam_${Date.now()}`,
        sender: 'nourish',
        text: data.reply_text,
        timestamp: new Date().toISOString(),
        meal_data: data.meal_logged,
        action_traces: data.action_traces
      };
      setMessages((prev) => [...prev, agentMsg]);
      if (data.action_traces) setRecentActionTraces(data.action_traces);
      await fetchDashboard();
    } catch (e) {
      console.error(e);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSendVoice = async () => {
    const userMsg: ChatMessage = {
      id: `user_voice_${Date.now()}`,
      sender: 'user',
      text: '🎤 [Voice Audio Message Recorded]',
      timestamp: new Date().toISOString()
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsProcessing(true);

    try {
      const res = await fetch(`${API_BASE}/chat/voice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: USER_ID, message: 'voice', voice_base64: 'sample_voice' })
      });
      if (!res.ok) throw new Error('Voice API error');
      const data = await res.json();

      const agentMsg: ChatMessage = {
        id: `agent_voice_${Date.now()}`,
        sender: 'nourish',
        text: data.reply_text,
        timestamp: new Date().toISOString(),
        meal_data: data.meal_logged,
        action_traces: data.action_traces
      };
      setMessages((prev) => [...prev, agentMsg]);
      if (data.action_traces) setRecentActionTraces(data.action_traces);
      await fetchDashboard();
    } catch (e) {
      console.error(e);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExecuteDemoStep = (stepNum: number, text: string) => {
    if (text === 'SIMULATE_NEXT_MORNING') {
      handleTriggerReminder();
    } else {
      handleSendMessage(text);
    }
  };

  const handleTriggerReminder = async () => {
    setIsProcessing(true);
    try {
      const res = await fetch(`${API_BASE}/reminders/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [
          ...prev,
          {
            id: `rem_proactive_${Date.now()}`,
            sender: 'nourish',
            text: `⏰ Proactive Agent Notification:\n\n${data.message}`,
            timestamp: new Date().toISOString()
          }
        ]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleResetDemoData = async () => {
    setIsProcessing(true);
    try {
      await fetch(`${API_BASE}/demo/reset?user_id=${USER_ID}`, { method: 'POST' });
      setMessages([
        {
          id: 'init_reset',
          sender: 'nourish',
          text: '🔄 Demo data has been reset to a clean state. Tell me what you ate today!',
          timestamp: new Date().toISOString()
        }
      ]);
      setRecentActionTraces([]);
      await fetchDashboard();
    } catch (e) {
      console.error(e);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden', backgroundColor: '#080c14' }}>
      {/* Hackathon Demo Flow & View Mode Bar */}
      <DemoFlowBar
        onExecuteStep={handleExecuteDemoStep}
        onResetData={handleResetDemoData}
        isProcessing={isProcessing}
        viewMode={viewMode}
        onToggleViewMode={() => setViewMode(prev => prev === 'split' ? 'phone' : 'split')}
      />

      {/* Main Workspace View */}
      {viewMode === 'phone' ? (
        /* Smartphone Video Prototype Recording View */
        <div style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#05080f',
          padding: '20px'
        }}>
          <div style={{
            width: '410px',
            height: '840px',
            borderRadius: '44px',
            border: '10px solid #1e293b',
            boxShadow: '0 25px 60px rgba(0, 0, 0, 0.8), 0 0 30px rgba(16, 185, 129, 0.2)',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            position: 'relative',
            backgroundColor: '#0b141a'
          }}>
            {/* Phone Notch */}
            <div style={{
              position: 'absolute',
              top: '0',
              left: '50%',
              transform: 'translateX(-50%)',
              width: '120px',
              height: '24px',
              backgroundColor: '#1e293b',
              borderBottomLeftRadius: '14px',
              borderBottomRightRadius: '14px',
              zIndex: 100
            }} />

            <WhatsAppChat
              messages={messages}
              onSendMessage={handleSendMessage}
              onSendVision={handleSendVision}
              onSendVoice={handleSendVoice}
              isTyping={isProcessing}
            />
          </div>
        </div>
      ) : (
        /* Split View (Desktop Web Simulator + Live Dashboard) */
        <div style={{ display: 'grid', gridTemplateColumns: '440px 1fr', flex: 1, overflow: 'hidden' }}>
          <WhatsAppChat
            messages={messages}
            onSendMessage={handleSendMessage}
            onSendVision={handleSendVision}
            onSendVoice={handleSendVoice}
            isTyping={isProcessing}
          />

          <Dashboard
            data={dashboardData}
            actionTraces={recentActionTraces}
            onTriggerReminder={handleTriggerReminder}
          />
        </div>
      )}
    </div>
  );
}

export default App;
