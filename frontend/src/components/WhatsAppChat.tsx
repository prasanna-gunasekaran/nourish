import React, { useState, useRef, useEffect } from 'react';
import { Send, Camera, Mic, CheckCheck, Wrench, Flame } from 'lucide-react';
import type { ChatMessage } from '../types';

interface WhatsAppChatProps {
  messages: ChatMessage[];
  onSendMessage: (text: string) => void;
  onSendVision: () => void;
  onSendVoice: () => void;
  isTyping: boolean;
}

export const WhatsAppChat: React.FC<WhatsAppChatProps> = ({
  messages,
  onSendMessage,
  onSendVision,
  onSendVoice,
  isTyping,
}) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isTyping) return;
    onSendMessage(inputText);
    setInputText('');
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      backgroundColor: '#0b141a',
      borderRight: '1px solid #1e293b',
      position: 'relative'
    }}>
      {/* WhatsApp Mobile Video Prototype Header */}
      <div style={{
        backgroundColor: '#008069',
        color: '#ffffff',
        padding: '8px 16px 12px 16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
        borderBottom: '1px solid rgba(0,0,0,0.1)'
      }}>
        {/* Smartphone Status Bar Simulation */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '0.72rem',
          fontWeight: 600,
          opacity: 0.95,
          paddingBottom: '4px'
        }}>
          <span>9:41</span>
          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
            <span>5G</span>
            <span>📶</span>
            <span>🔋 100%</span>
          </div>
        </div>

        {/* WhatsApp App Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ position: 'relative' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.25rem',
                boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
              }}>
                🥗
              </div>
              <span style={{
                position: 'absolute',
                bottom: '1px',
                right: '1px',
                width: '11px',
                height: '11px',
                backgroundColor: '#25D366',
                border: '2px solid #008069',
                borderRadius: '50%'
              }} />
            </div>

            <div>
              <div style={{ color: '#ffffff', fontWeight: 700, fontSize: '0.98rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                Nourish AI
                <span style={{ fontSize: '0.65rem', background: 'rgba(255,255,255,0.2)', color: '#ffffff', padding: '1px 6px', borderRadius: '4px', fontWeight: 600 }}>
                  OFFICIAL AGENT
                </span>
              </div>
              <div style={{ color: '#d1fae5', fontSize: '0.74rem' }}>
                WhatsApp Business • online
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={onSendVision}
              title="Scan Food Image (Multimodal Vision)"
              style={{
                background: 'rgba(255,255,255,0.15)',
                border: 'none',
                borderRadius: '50%',
                width: '36px',
                height: '36px',
                color: '#ffffff',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <Camera size={18} />
            </button>
            <button
              onClick={onSendVoice}
              title="Send Voice Message (Speech-to-Text)"
              style={{
                background: 'rgba(255,255,255,0.15)',
                border: 'none',
                borderRadius: '50%',
                width: '36px',
                height: '36px',
                color: '#ffffff',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <Mic size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* WhatsApp Chat Messages Area */}
      <div className="wa-chat-bg" style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px'
      }}>
        <div style={{
          textAlign: 'center',
          margin: '8px 0',
          fontSize: '0.72rem',
          color: '#8696a0',
          background: 'rgba(17, 27, 33, 0.7)',
          padding: '4px 12px',
          borderRadius: '8px',
          alignSelf: 'center'
        }}>
          🔒 Messages are encrypted & processed locally by Nourish Agent architecture.
        </div>

        {messages.map((msg) => {
          const isUser = msg.sender === 'user';
          return (
            <div
              key={msg.id}
              className="animate-fade-in"
              style={{
                alignSelf: isUser ? 'flex-end' : 'flex-start',
                maxWidth: '82%',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px'
              }}
            >
              {/* Tool Execution Trace Badge */}
              {!isUser && msg.action_traces && msg.action_traces.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '2px' }}>
                  {msg.action_traces.map((trace, idx) => (
                    <span key={idx} className="tool-badge" title={trace.description}>
                      <Wrench size={10} />
                      {trace.tool_name}: {trace.output_summary}
                    </span>
                  ))}
                </div>
              )}

              {/* Message Bubble */}
              <div style={{
                backgroundColor: isUser ? '#005c4b' : '#202c33',
                color: '#e9edef',
                padding: '10px 14px',
                borderRadius: isUser ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                boxShadow: '0 1px 2px rgba(0,0,0,0.3)',
                whiteSpace: 'pre-wrap',
                fontSize: '0.9rem',
                lineHeight: 1.45
              }}>
                {msg.text}

                {/* Logged Meal Card Overlay */}
                {msg.meal_data && (
                  <div style={{
                    marginTop: '10px',
                    padding: '8px 12px',
                    background: 'rgba(0,0,0,0.25)',
                    borderRadius: '8px',
                    borderLeft: '3px solid #10b981',
                    fontSize: '0.8rem'
                  }}>
                    <div style={{ fontWeight: 600, color: '#6ee7b7', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Flame size={14} color="#f59e0b" />
                      Logged: {msg.meal_data.meal_type} (~{msg.meal_data.total_calories} kcal)
                    </div>
                    <div style={{ color: '#94a3b8', fontSize: '0.72rem', marginTop: '2px' }}>
                      P: {msg.meal_data.total_protein}g | C: {msg.meal_data.total_carbs}g | F: {msg.meal_data.total_fat}g
                    </div>
                  </div>
                )}

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'flex-end',
                  gap: '4px',
                  fontSize: '0.68rem',
                  color: '#8696a0',
                  marginTop: '4px'
                }}>
                  {msg.timestamp.split('T')[1]?.substring(0, 5) || 'Just now'}
                  {isUser && <CheckCheck size={14} color="#53bdeb" />}
                </div>
              </div>
            </div>
          );
        })}

        {isTyping && (
          <div style={{
            alignSelf: 'flex-start',
            backgroundColor: '#202c33',
            padding: '10px 16px',
            borderRadius: '12px 12px 12px 2px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <span style={{ fontSize: '0.75rem', color: '#8696a0' }}>Nourish is reasoning</span>
            <div style={{ display: 'flex', gap: '3px' }}>
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <form onSubmit={handleSubmit} style={{
        backgroundColor: '#202c33',
        padding: '10px 12px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        borderTop: '1px solid #2a3942'
      }}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Type a message e.g. 'I ate 3 idlis and one vada for breakfast'..."
          style={{
            flex: 1,
            backgroundColor: '#2a3942',
            border: 'none',
            borderRadius: '8px',
            padding: '10px 14px',
            color: '#e9edef',
            fontSize: '0.9rem',
            outline: 'none'
          }}
        />

        <button
          type="submit"
          disabled={!inputText.trim() || isTyping}
          style={{
            backgroundColor: inputText.trim() ? '#00a884' : '#2a3942',
            border: 'none',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            color: '#ffffff',
            cursor: inputText.trim() ? 'pointer' : 'default',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'background-color 0.2s'
          }}
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
};
