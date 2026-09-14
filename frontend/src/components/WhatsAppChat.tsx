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
      {/* WhatsApp Chat Header */}
      <div style={{
        backgroundColor: '#202c33',
        padding: '12px 16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid #2a3942'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ position: 'relative' }}>
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.2rem',
              boxShadow: '0 0 10px rgba(16, 185, 129, 0.4)'
            }}>
              🥗
            </div>
            <span style={{
              position: 'absolute',
              bottom: '0',
              right: '0',
              width: '11px',
              height: '11px',
              backgroundColor: '#22c55e',
              border: '2px solid #202c33',
              borderRadius: '50%'
            }} />
          </div>

          <div>
            <div style={{ color: '#e9edef', fontWeight: 600, fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
              Nourish AI
              <span style={{ fontSize: '0.7rem', background: '#059669', color: '#ecfdf5', padding: '1px 6px', borderRadius: '4px' }}>
                WhatsApp Agent
              </span>
            </div>
            <div style={{ color: '#8696a0', fontSize: '0.75rem' }}>
              Your personal nutrition agent • Online
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={onSendVision}
            title="Scan Food Image (Multimodal Vision)"
            style={{
              background: 'rgba(255,255,255,0.08)',
              border: 'none',
              borderRadius: '50%',
              width: '36px',
              height: '36px',
              color: '#aebac1',
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
              background: 'rgba(255,255,255,0.08)',
              border: 'none',
              borderRadius: '50%',
              width: '36px',
              height: '36px',
              color: '#aebac1',
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
