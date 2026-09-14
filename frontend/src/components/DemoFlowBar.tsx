import React from 'react';
import { Play, RotateCcw, Sparkles, Smartphone, Monitor } from 'lucide-react';

interface DemoFlowBarProps {
  onExecuteStep: (stepNumber: number, stepText: string) => void;
  onResetData: () => void;
  isProcessing: boolean;
  viewMode: 'split' | 'phone';
  onToggleViewMode: () => void;
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

export const DemoFlowBar: React.FC<DemoFlowBarProps> = ({
  onExecuteStep,
  onResetData,
  isProcessing,
  viewMode,
  onToggleViewMode
}) => {
  return (
    <div style={{
      background: 'linear-gradient(90deg, #090e17 0%, #064e3b 100%)',
      borderBottom: '1px solid rgba(255,255,255,0.1)',
      padding: '8px 16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '12px',
      overflowX: 'auto'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 'max-content' }}>
        <Sparkles size={18} color="#34d399" />
        <span style={{ fontWeight: 700, fontSize: '0.85rem', color: '#ecfdf5', letterSpacing: '0.5px' }}>
          NOURISH DEMO FLOW:
        </span>
      </div>

      <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '2px' }}>
        {DEMO_STEPS.map((step) => (
          <button
            key={step.num}
            disabled={isProcessing}
            onClick={() => onExecuteStep(step.num, step.text)}
            style={{
              background: '#065f46',
              color: '#ecfdf5',
              border: '1px solid #047857',
              borderRadius: '6px',
              padding: '4px 10px',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: isProcessing ? 'not-allowed' : 'pointer',
              whiteSpace: 'nowrap',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              transition: 'all 0.2s ease',
              opacity: isProcessing ? 0.6 : 1
            }}
            onMouseOver={(e) => (e.currentTarget.style.background = '#047857')}
            onMouseOut={(e) => (e.currentTarget.style.background = '#065f46')}
          >
            <Play size={10} color="#34d399" fill="#34d399" />
            {step.label}
          </button>
        ))}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <button
          onClick={onToggleViewMode}
          title="Toggle Mobile Video Recording View"
          style={{
            background: viewMode === 'phone' ? '#10b981' : 'rgba(255,255,255,0.1)',
            color: '#ffffff',
            border: '1px solid rgba(255,255,255,0.2)',
            borderRadius: '6px',
            padding: '4px 10px',
            fontSize: '0.75rem',
            fontWeight: 600,
            cursor: 'pointer',
            whiteSpace: 'nowrap',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '5px'
          }}
        >
          {viewMode === 'phone' ? <Monitor size={14} /> : <Smartphone size={14} />}
          {viewMode === 'phone' ? 'Split View' : '📱 Mobile Video Mode'}
        </button>

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
    </div>
  );
};
