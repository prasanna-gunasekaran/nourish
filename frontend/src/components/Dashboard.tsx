import React from 'react';
import type { DashboardData, AgentActionTrace } from '../types';
import { Flame, PieChart, Brain, Clock, Bell, User, Wrench, AlertTriangle } from 'lucide-react';

interface DashboardProps {
  data: DashboardData | null;
  actionTraces: AgentActionTrace[];
  onTriggerReminder: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ data, actionTraces, onTriggerReminder }) => {
  if (!data) {
    return (
      <div style={{ padding: '32px', color: '#94a3b8', textAlign: 'center', fontSize: '0.9rem' }}>
        Loading Nourish Agent Intelligence Dashboard...
      </div>
    );
  }

  const { today_summary, user_profile, insights, reminders } = data;
  const calsPct = Math.min(100, Math.round((today_summary.total_calories / user_profile.calorie_goal) * 100));
  const proteinPct = Math.min(100, Math.round((today_summary.total_protein / user_profile.protein_goal) * 100));
  const carbsPct = Math.min(100, Math.round((today_summary.total_carbs / user_profile.carbs_goal) * 100));
  const fatPct = Math.min(100, Math.round((today_summary.total_fat / user_profile.fat_goal) * 100));

  // Determine smart foods to avoid based on current intake
  const foodsToAvoidList = [];
  let avoidReason = "";

  if (today_summary.total_carbs > 100) {
    foodsToAvoidList.push("🚫 Rice-heavy main courses (Biryani, Fried Rice, Extra Rice)");
    foodsToAvoidList.push("🚫 Refined wheat breads (Malabar Parotta, Poori)");
    foodsToAvoidList.push("🚫 Sugary beverages & desserts (Chai with sugar, Sodas)");
    avoidReason = `Carbohydrate intake is high (~${Math.round(today_summary.total_carbs)}g). Avoid additional starches for your next meal or tomorrow morning.`;
  } else if (today_summary.total_fat > 40) {
    foodsToAvoidList.push("🚫 Deep-fried snacks (Medu Vada, Samosa, Crispy Fish Fry)");
    foodsToAvoidList.push("🚫 Heavy cream gravies");
    avoidReason = `Fat intake is high (~${Math.round(today_summary.total_fat)}g). Avoid fried foods for your next meal.`;
  } else {
    foodsToAvoidList.push("🚫 High-sugar sodas & deep-fried snacks");
    avoidReason = "Keep your next meal light & rich in vegetables & lean protein.";
  }

  return (
    <div style={{
      height: '100%',
      overflowY: 'auto',
      backgroundColor: '#080c14',
      padding: '24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '20px'
    }}>
      {/* High-Class Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#f8fafc', letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <PieChart size={24} color="#10b981" />
            Nutrition & Agent Intelligence
          </h2>
          <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginTop: '2px' }}>
            Real-time telemetry, memory state & predictive guidance for <span style={{ color: '#38bdf8', fontWeight: 600 }}>{data.user_id}</span>
          </p>
        </div>
      </div>

      {/* Today's Calorie & Macro Target Progress */}
      <div className="glass-panel" style={{ padding: '18px', borderRadius: '16px' }}>
        <div style={{ fontSize: '0.88rem', fontWeight: 600, color: '#e2e8f0', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Flame size={18} color="#fbbf24" />
          Today's Calorie & Macronutrient Progress
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '12px' }}>
          {/* Calorie Card */}
          <div style={{ background: '#101726', padding: '14px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)' }}>
            <div style={{ fontSize: '0.74rem', color: '#94a3b8', fontWeight: 500 }}>Energy / Calories</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fbbf24', marginTop: '4px' }}>
              {Math.round(today_summary.total_calories)} <span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#64748b' }}>/ {user_profile.calorie_goal} kcal</span>
            </div>
            <div style={{ height: '6px', width: '100%', background: '#1e293b', borderRadius: '3px', marginTop: '10px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${calsPct}%`, background: 'linear-gradient(90deg, #f59e0b, #fbbf24)', borderRadius: '3px', transition: 'width 0.5s ease' }} />
            </div>
          </div>

          {/* Protein Card */}
          <div style={{ background: '#101726', padding: '14px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)' }}>
            <div style={{ fontSize: '0.74rem', color: '#94a3b8', fontWeight: 500 }}>Protein</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#38bdf8', marginTop: '4px' }}>
              {Math.round(today_summary.total_protein)}g <span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#64748b' }}>/ {user_profile.protein_goal}g</span>
            </div>
            <div style={{ height: '6px', width: '100%', background: '#1e293b', borderRadius: '3px', marginTop: '10px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${proteinPct}%`, background: 'linear-gradient(90deg, #0284c7, #38bdf8)', borderRadius: '3px', transition: 'width 0.5s ease' }} />
            </div>
          </div>

          {/* Carbs Card */}
          <div style={{ background: '#101726', padding: '14px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)' }}>
            <div style={{ fontSize: '0.74rem', color: '#94a3b8', fontWeight: 500 }}>Carbohydrates</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#c084fc', marginTop: '4px' }}>
              {Math.round(today_summary.total_carbs)}g <span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#64748b' }}>/ {user_profile.carbs_goal}g</span>
            </div>
            <div style={{ height: '6px', width: '100%', background: '#1e293b', borderRadius: '3px', marginTop: '10px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${carbsPct}%`, background: 'linear-gradient(90deg, #9333ea, #c084fc)', borderRadius: '3px', transition: 'width 0.5s ease' }} />
            </div>
          </div>

          {/* Fat Card */}
          <div style={{ background: '#101726', padding: '14px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)' }}>
            <div style={{ fontSize: '0.74rem', color: '#94a3b8', fontWeight: 500 }}>Fat</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f43f5e', marginTop: '4px' }}>
              {Math.round(today_summary.total_fat)}g <span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#64748b' }}>/ {user_profile.fat_goal}g</span>
            </div>
            <div style={{ height: '6px', width: '100%', background: '#1e293b', borderRadius: '3px', marginTop: '10px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${fatPct}%`, background: 'linear-gradient(90deg, #e11d48, #f43f5e)', borderRadius: '3px', transition: 'width 0.5s ease' }} />
            </div>
          </div>
        </div>
      </div>

      {/* NEW FEATURE CARD: Foods to Avoid for Next Meal / Tomorrow */}
      <div className="glass-panel" style={{ padding: '18px', borderRadius: '16px', borderLeft: '4px solid #f43f5e' }}>
        <div style={{ fontSize: '0.88rem', fontWeight: 600, color: '#fecdd3', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={18} color="#f43f5e" />
          Foods to AVOID (Next Meal / Tomorrow)
        </div>
        <p style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '12px' }}>
          {avoidReason}
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {foodsToAvoidList.map((item, i) => (
            <div key={i} style={{
              background: 'rgba(244, 63, 94, 0.1)',
              border: '1px solid rgba(244, 63, 94, 0.25)',
              padding: '8px 12px',
              borderRadius: '8px',
              fontSize: '0.8rem',
              color: '#fda4af',
              fontWeight: 500
            }}>
              {item}
            </div>
          ))}
        </div>
      </div>

      {/* Meal Timeline */}
      <div className="glass-panel" style={{ padding: '18px', borderRadius: '16px' }}>
        <div style={{ fontSize: '0.88rem', fontWeight: 600, color: '#e2e8f0', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Clock size={18} color="#38bdf8" />
          Today's Logged Meal Timeline
        </div>

        {today_summary.meals.length === 0 ? (
          <div style={{ fontSize: '0.8rem', color: '#64748b', fontStyle: 'italic' }}>
            No meals logged in database yet today.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {today_summary.meals.map((meal) => (
              <div key={meal.meal_id} style={{
                background: '#101726',
                padding: '12px 14px',
                borderRadius: '10px',
                borderLeft: '3px solid #10b981',
                border: '1px solid rgba(255,255,255,0.05)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div>
                  <div style={{ fontSize: '0.86rem', fontWeight: 600, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {meal.meal_type}
                    <span style={{ fontSize: '0.68rem', background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', padding: '2px 8px', borderRadius: '9999px', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
                      {meal.confidence} Confidence
                    </span>
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginTop: '3px' }}>
                    {meal.food_items.map(i => `${i.quantity} ${i.food_name}`).join(', ')}
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fbbf24' }}>
                    ~{Math.round(meal.total_calories)} kcal
                  </div>
                  <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '2px' }}>
                    P:{meal.total_protein}g | C:{meal.total_carbs}g | F:{meal.total_fat}g
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Eating Patterns & User Profile Memory */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        {/* Pattern Intelligence Card */}
        <div className="glass-panel" style={{ padding: '18px', borderRadius: '16px' }}>
          <div style={{ fontSize: '0.88rem', fontWeight: 600, color: '#e2e8f0', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Brain size={18} color="#c084fc" />
            Pattern Intelligence
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {insights.map((insight, idx) => (
              <div key={idx} style={{ fontSize: '0.78rem', color: '#e9d5ff', background: 'rgba(192, 132, 252, 0.1)', padding: '8px 12px', borderRadius: '8px', border: '1px solid rgba(192, 132, 252, 0.2)' }}>
                💡 {insight}
              </div>
            ))}
          </div>
        </div>

        {/* User Memory & Preference Drawer */}
        <div className="glass-panel" style={{ padding: '18px', borderRadius: '16px' }}>
          <div style={{ fontSize: '0.88rem', fontWeight: 600, color: '#e2e8f0', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <User size={18} color="#34d399" />
            Persistent Memory State
          </div>

          <div style={{ fontSize: '0.78rem', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div>
              <span style={{ color: '#94a3b8' }}>Disliked Foods: </span>
              {user_profile.disliked_foods.length === 0 ? (
                <span style={{ color: '#64748b' }}>None</span>
              ) : (
                user_profile.disliked_foods.map(df => (
                  <span key={df} style={{ background: 'rgba(244, 63, 94, 0.2)', color: '#fda4af', padding: '2px 8px', borderRadius: '6px', marginRight: '4px', border: '1px solid rgba(244,63,94,0.3)' }}>
                    ❌ {df}
                  </span>
                ))
              )}
            </div>

            <div>
              <span style={{ color: '#94a3b8' }}>Confirmed Portions: </span>
              {Object.keys(user_profile.confirmed_portions).length === 0 ? (
                <span style={{ color: '#64748b' }}>None</span>
              ) : (
                Object.entries(user_profile.confirmed_portions).map(([item, size]) => (
                  <span key={item} style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#7dd3fc', padding: '2px 8px', borderRadius: '6px', marginRight: '4px', border: '1px solid rgba(56,189,248,0.3)' }}>
                    📏 {item}: {size}
                  </span>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Proactive Reminders & Agent Telemetry */}
      <div className="glass-panel" style={{ padding: '18px', borderRadius: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
          <div style={{ fontSize: '0.88rem', fontWeight: 600, color: '#e2e8f0', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Bell size={18} color="#fbbf24" />
            Active Proactive Reminders ({reminders.length})
          </div>

          <button
            onClick={onTriggerReminder}
            style={{
              background: 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              padding: '5px 12px',
              fontSize: '0.74rem',
              fontWeight: 600,
              cursor: 'pointer',
              boxShadow: '0 2px 10px rgba(16,185,129,0.3)'
            }}
          >
            Trigger Follow-Up
          </button>
        </div>

        {reminders.length === 0 ? (
          <div style={{ fontSize: '0.78rem', color: '#64748b' }}>No reminders scheduled yet. Say "Remind me to log breakfast..."</div>
        ) : (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {reminders.map(r => (
              <span key={r.reminder_id} style={{ background: '#101726', border: '1px solid rgba(251, 191, 36, 0.3)', color: '#fbbf24', padding: '5px 10px', borderRadius: '8px', fontSize: '0.76rem' }}>
                ⏰ {r.title} ({r.frequency})
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Agent Activity Trace Logs */}
      <div className="glass-panel" style={{ padding: '18px', borderRadius: '16px' }}>
        <div style={{ fontSize: '0.88rem', fontWeight: 600, color: '#e2e8f0', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Wrench size={18} color="#38bdf8" />
          Agent Telemetry & Action Execution Feed
        </div>

        {actionTraces.length === 0 ? (
          <div style={{ fontSize: '0.78rem', color: '#64748b' }}>No tool traces logged in current turn yet.</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '200px', overflowY: 'auto' }}>
            {actionTraces.map((t, idx) => (
              <div key={idx} style={{ fontSize: '0.76rem', background: '#090e17', padding: '8px 12px', borderRadius: '8px', borderLeft: '3px solid #38bdf8', border: '1px solid rgba(255,255,255,0.04)' }}>
                <span style={{ color: '#38bdf8', fontWeight: 600 }}>[{t.tool_name}]</span> <span style={{ color: '#e2e8f0' }}>{t.description}</span> → <span style={{ color: '#34d399' }}>{t.output_summary}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
