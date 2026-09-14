import React from 'react';
import { Play, RotateCcw, Sparkles } from 'lucide-react';

interface DemoFlowBarProps {
  onExecuteStep: (stepNumber: number, stepText: string) => void;
  onResetData: () => void;
  isProcessing: boolean;
}

const DEMO_STEPS = [
  { num: 1, label: "1. Log Breakfast", text: "I ate 3 idlis, one vada and 2 eggs for breakfast." },
  { num: 2, label: "2. Log Lunch", text: "For lunch I had chicken biryani and a glass of buttermilk." },
  { num: 3, label: "3. Today Summary", text: "What have I eaten today?" },
  { num: 4, label: "4. Dinner Rec", text: "What should I eat for dinner?" },
  { num: 5, label: "5. Dislike Eggs", text: "I don't like eggs." },
  { num: 6, label: "6. Re-Suggest", text: "Suggest dinner again." },
  { num: 7, label: "7. Set Reminder", text: "Remind me to log breakfast every morning." },
  { num: 8, label: "8. Next Morning", text: "SIMULATE_NEXT_MORNING" },
];

export const DemoFlowBar: React.FC<DemoFlowBarProps> = ({ onExecuteStep, onResetData, isProcessing }) => {
  return (
    <div style={{
      background: 'linear-gradient(90deg, #0f172a 0%, #1e1b4b 100%)',
      borderBottom: '1px solid #312e81',
      padding: '8px 16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '12px',
      overflowX: 'auto'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 'max-content' }}>
        <Sparkles size={18} color="#a78bfa" />
        <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#c7d2fe', letterSpacing: '0.5px' }}>
          HACKATHON DEMO FLOW:
        </span>
      </div>

      <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '2px' }}>
        {DEMO_STEPS.map((step) => (
          <button
            key={step.num}
            disabled={isProcessing}
            onClick={() => onExecuteStep(step.num, step.text)}
            style={{
              background: '#312e81',
              color: '#e0e7ff',
              border: '1px solid #4338ca',
              borderRadius: '6px',
              padding: '4px 10px',
              fontSize: '0.75rem',
              fontWeight: 500,
              cursor: isProcessing ? 'not-allowed' : 'pointer',
              whiteSpace: 'nowrap',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              transition: 'all 0.2s ease',
              opacity: isProcessing ? 0.6 : 1
            }}
            onMouseOver={(e) => (e.currentTarget.style.background = '#3730a3')}
            onMouseOut={(e) => (e.currentTarget.style.background = '#312e81')}
          >
            <Play size={10} color="#818cf8" fill="#818cf8" />
            {step.label}
          </button>
        ))}
      </div>

      <button
        disabled={isProcessing}
        onClick={onResetData}
        style={{
          background: 'rgba(244, 63, 94, 0.15)',
          color: '#fda4af',
          border: '1px solid rgba(244, 63, 94, 0.4)',
          borderRadius: '6px',
          padding: '4px 10px',
          fontSize: '0.75rem',
          fontWeight: 600,
          cursor: 'pointer',
          whiteSpace: 'nowrap',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px'
        }}
      >
        <RotateCcw size={12} />
        Reset Demo Data
      </button>
    </div>
  );
};
