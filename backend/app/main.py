from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional

from app.models.schemas import ChatRequest, ChatResponse
from app.repositories.sqlite_repo import SQLiteDatabase, SQLiteMealRepository, SQLiteUserRepository, SQLiteReminderRepository
from app.nutrition.service import NutritionService
from app.providers.mock_provider import LocalModelProvider
from app.tools.agent_tools import AgentTools
from app.agent.core import AgentCore
from app.services.vision_voice import VisionService, VoiceService
from app.services.reminders import ReminderService
from app.whatsapp.service import LocalSimulatorWhatsAppService

app = FastAPI(
    title="Nourish - WhatsApp AI Nutrition Agent API",
    description="Conversational AI agent for natural language food tracking, nutrition calculation, persistent memory, and personalized meal recommendations.",
    version="1.0.0"
)

# Enable CORS for local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Storage & Repositories
db = SQLiteDatabase("nourish.db")
meal_repo = SQLiteMealRepository(db)
user_repo = SQLiteUserRepository(db)
reminder_repo = SQLiteReminderRepository(db)

# Initialize Services & Core Agent
nutrition_service = NutritionService()
model_provider = LocalModelProvider()
agent_tools = AgentTools(nutrition_service, meal_repo, user_repo, reminder_repo)
agent_core = AgentCore(model_provider, agent_tools)

vision_service = VisionService()
voice_service = VoiceService()
reminder_service = ReminderService(reminder_repo)
whatsapp_service = LocalSimulatorWhatsAppService()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "Nourish WhatsApp AI Nutrition Agent",
        "mode": "Zero-AWS Local Execution Mode",
        "version": "1.0.0"
    }

@app.post("/api/chat", response_model=ChatResponse)
def handle_chat(req: ChatRequest):
    try:
        response = agent_core.process_message(req.message, req.user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/vision", response_model=ChatResponse)
def handle_vision_chat(req: ChatRequest):
    if not req.image_base64:
        raise HTTPException(status_code=400, detail="image_base64 is required")
    
    vision_res = vision_service.analyze_food_image(req.image_base64)
    foods_str = ", ".join([f"{item['quantity']} {item['unit']} {item['food_name']}" for item in vision_res["identified_foods"]])
    simulated_msg = f"I ate {foods_str}"
    
    response = agent_core.process_message(simulated_msg, req.user_id)
    response.reply_text = f"📷 Image Analyzed:\n{response.reply_text}"
    return response

@app.post("/api/chat/voice", response_model=ChatResponse)
def handle_voice_chat(req: ChatRequest):
    if not req.voice_base64:
        raise HTTPException(status_code=400, detail="voice_base64 is required")

    voice_res = voice_service.transcribe_audio(req.voice_base64)
    transcription = voice_res["transcription"]
    
    response = agent_core.process_message(transcription, req.user_id)
    response.reply_text = f"🎤 Voice Transcribed: \"{transcription}\"\n\n{response.reply_text}"
    return response

@app.get("/api/dashboard/{user_id}")
def get_dashboard_data(user_id: str = "demo_user"):
    summary = agent_tools.get_daily_summary(user_id)
    profile = agent_tools.get_user_profile(user_id)
    patterns = agent_tools.analyze_food_patterns(user_id)
    reminders = agent_tools.get_reminders(user_id)

    return {
        "user_id": user_id,
        "today_summary": summary,
        "user_profile": profile,
        "insights": patterns.get("insights", []),
        "reminders": reminders.get("reminders", [])
    }

@app.get("/api/reminders/{user_id}")
def get_reminders(user_id: str = "demo_user"):
    return agent_tools.get_reminders(user_id)

@app.post("/api/reminders/trigger")
def trigger_reminder(user_id: str = "demo_user"):
    msg = reminder_service.trigger_proactive_followup(user_id)
    return {
        "status": "triggered",
        "message": msg
    }

@app.post("/api/demo/reset")
def reset_demo_data(user_id: str = "demo_user"):
    meal_repo.delete_user_meals(user_id)
    user_repo.delete_user_profile(user_id)
    reminder_repo.delete_user_reminders(user_id)
    
    # Re-initialize default profile
    default_profile = user_repo.get_user_profile(user_id)
    return {
        "status": "success",
        "message": "Demo user data reset successfully.",
        "profile": default_profile.model_dump()
    }
