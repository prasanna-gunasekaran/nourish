# Nourish — WhatsApp AI Nutrition Agent

> **"Your personal nutrition agent, right where you chat."**

Nourish is a conversational AI nutrition agent designed for WhatsApp. Unlike traditional calorie counting apps that require cumbersome manual form inputs, Nourish allows users to naturally talk about what they ate in everyday language. Nourish parses foods and portion quantities, retrieves structured nutritional data, calculates energy and macronutrients, remembers personal food history and preferences, analyzes eating patterns, and provides adaptive personalized meal recommendations.

Nourish operates as a persistent personal nutrition agent following the core loop:

```
UNDERSTAND ➔ RETRIEVE ➔ CALCULATE ➔ REMEMBER ➔ ANALYZE ➔ RECOMMEND ➔ FOLLOW UP
```

---

## 🏗️ Architecture Overview

```
                      ┌──────────────────────────────────────────────┐
                      │          Web WhatsApp Simulator UI           │
                      │        (Chat Simulator + Dashboard)          │
                      └──────────────────────┬───────────────────────┘
                                             │ REST API (JSON)
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │            FastAPI Server (backend)          │
                      └──────┬──────────────────────────────┬────────┘
                             │                              │
                             ▼                              ▼
                  ┌────────────────────┐          ┌───────────────────┐
                  │  WhatsApp Service  │          │  Reminder Engine  │
                  │  (Local/Cloud API) │          │(Local/EventBridge)│
                  └──────────┬─────────┘          └─────────┬─────────┘
                             │                              │
                             ▼                              ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │                         Strands Core Agent Loop                          │
  │  ┌──────────────────┐   ┌───────────────────┐   ┌─────────────────────┐  │
  │  │  Model Provider  │   │   12 Agent Tools  │   │  Nutrition Engine   │  │
  │  │ (Local / Bedrock)│   │ (Search, Calc...) │   │ (50+ Foods + Calc)  │  │
  │  └──────────────────┘   └─────────┬─────────┘   └─────────────────────┘  │
  └───────────────────────────────────┼──────────────────────────────────────┘
                                      │
                                      ▼
                      ┌──────────────────────────────┐
                      │    Repository Abstractions   │
                      │  (SQLite Local / DynamoDB)   │
                      └──────────────────────────────┘
```

---

## ⚡ Zero-AWS Local Development Guarantee

This project runs 100% locally out-of-the-box without requiring AWS credentials or external cloud subscription keys.

It uses:
- **`SQLiteMealRepository`** for local persistent meal memory.
- **`LocalModelProvider`** for smart local NLP entity extraction, tool calling decisions, and natural response synthesis.
- **`LocalSimulatorWhatsAppService`** for the web chat interface.

All cloud services are decoupled behind clean provider abstractions (`BedrockModelProvider`, `DynamoDBMealRepository`, `WhatsAppCloudAPIService`) ready for immediate production deployment when AWS credentials are provided.

---

## ✨ Features

- **Natural Language Food Logging**: Parse complex phrasing like *"I ate 3 idlis, one vada and 2 eggs for breakfast"*.
- **Accurate Nutrition Calculation**: Structured calculation using a database of 50+ common foods (prioritized for South Indian & Indian cuisine) with serving conversions and macronutrient breakdown.
- **Confidence & Uncertainty Estimation**: Tag estimates as HIGH, MEDIUM, or LOW confidence based on portion specificity.
- **Correction & Learning Loop**: Remembers user portion adjustments (e.g. *"My dosa was large"* ➔ remembers user's usual dosa size).
- **Persistent Personal Memory**: Stores disliked foods (e.g. *"I don't like eggs"*) and filters them out of future recommendations.
- **Daily Food Summaries & Date-Aware History**: Retrieve daily totals or query history like *"What did I eat yesterday?"*.
- **Food Pattern Intelligence**: Identifies high carb concentration, vegetable deficiency, and protein inconsistency.
- **Adaptive Meal Recommendations**: Contextually recommends dinners based on today's logged intake while strictly excluding disliked foods.
- **"What Should I Do Now?" Guidance**: Empathetic, non-judgmental wellness advice after heavy energy-dense meals.
- **Proactive Reminders**: Background scheduler triggers opt-in meal logging reminders.
- **Multimodal Vision & Voice Architecture**: Prepared adapters for food image identification and speech-to-text audio logging.

---

## 🛠️ Local Setup & Running Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Start the FastAPI Backend
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Launch FastAPI application on http://localhost:8000
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Start the React Web Frontend
```bash
# Open a new terminal in the frontend directory
cd frontend

# Install Node modules
npm install

# Start Vite development server on http://localhost:5173
npm run dev
```

### 3. Run Automated Tests
```bash
# Run backend pytest suite (unit + integration + end-to-end hackathon demo test)
$env:PYTHONPATH="backend"; python -m pytest backend/tests
```

---

## 🎯 8-Step Hackathon Demo Flow

Use the top **Hackathon Demo Flow Stepper** bar in the web UI to trigger each step with 1-click:

| Step | Action | User Input | Agent behavior |
|--- |--- |--- |--- |
| **STEP 1** | Log Breakfast | `"I ate 3 idlis, one vada and 2 eggs for breakfast."` | Calculates 464 kcal, P: 20g, C: 55g, F: 18g. Persists to SQLite. |
| **STEP 2** | Log Lunch | `"For lunch I had chicken biryani and a glass of buttermilk."` | Calculates ~690 kcal, identifies portion uncertainty (MEDIUM confidence). |
| **STEP 3** | Daily Summary | `"What have I eaten today?"` | Retrieves stored meals and renders breakdown and daily macro totals. |
| **STEP 4** | Dinner Recommendation | `"What should I eat for dinner?"` | Analyzes earlier high-carb meals, suggests balanced dinner (Sambar + 2 Eggs + Poriyal). |
| **STEP 5** | Preference Update | `"I don't like eggs."` | Saves `eggs = disliked` into persistent user profile memory. |
| **STEP 6** | Adaptive Re-Suggestion | `"Suggest dinner again."` | Re-executes recommendation engine; replaces eggs with Dal Tadka & Chapatis. |
| **STEP 7** | Create Reminder | `"Remind me to log breakfast every morning."` | Schedules proactive reminder in `ReminderRepository`. |
| **STEP 8** | Proactive Trigger | *(Click "Simulate Next Morning")* | Agent sends proactive follow-up notification: *"Good morning! Would you like to log breakfast?"* |

---

## 🗺️ AWS Production Migration Roadmap

When AWS credentials become available, local components cleanly map to managed AWS infrastructure:

```
Local SQLite (`SQLiteMealRepository`)   ➔  Amazon DynamoDB
Local File Storage                      ➔  Amazon S3
Local Background Scheduler              ➔  Amazon EventBridge / SNS
Local Model (`LocalModelProvider`)      ➔  Amazon Bedrock (Claude 3.5 Sonnet / AWS Nova)
Local Agent Runtime                     ➔  AWS Strands Agents / AgentCore
Local Web Simulator                     ➔  WhatsApp Business Cloud API
```

---

## 🛡️ Safety & Medical Disclaimer

Nourish provides general energy and macronutrient estimates based on user-provided descriptions. **Nourish is not a medical diagnosis system** and does not provide medical advice or restrictive dieting regimes. Users are encouraged to consult certified nutritionists or medical professionals for individual medical conditions.
