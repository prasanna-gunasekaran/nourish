from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import os
import httpx

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

# ---------------------------------------------------------
# LIVE WHATSAPP INTEGRATION ENDPOINTS (Meta Cloud API & Twilio)
# ---------------------------------------------------------

# 1. Meta WhatsApp Cloud API Verification Webhook (GET)
@app.get("/webhook")
@app.get("/api/whatsapp/webhook")
def verify_meta_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    expected_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "nourish_verify_token")

    if mode == "subscribe" and token == expected_token:
        return Response(content=challenge, media_type="text/plain")
    
    raise HTTPException(status_code=403, detail="Verification token mismatch")

# 2. Meta WhatsApp Cloud API Inbound Webhook (POST)
@app.post("/webhook")
@app.post("/api/whatsapp/webhook")
async def handle_meta_whatsapp_inbound(request: Request):
    payload = await request.json()
    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return {"status": "ok", "detail": "No message body"}

        message = messages[0]
        from_phone = message.get("from")  # Sender's WhatsApp Phone Number
        msg_text = message.get("text", {}).get("body", "")

        if msg_text and from_phone:
            # Execute Core Agent Loop with sender's phone number as user_id
            response = agent_core.process_message(msg_text, user_id=from_phone)

            # Send reply back via Meta Cloud API if credentials exist
            access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
            phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

            if access_token and phone_number_id:
                async with httpx.AsyncClient() as client:
                    url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
                    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
                    data = {
                        "messaging_product": "whatsapp",
                        "to": from_phone,
                        "type": "text",
                        "text": {"body": response.reply_text}
                    }
                    await client.post(url, json=data, headers=headers)

            return {"status": "processed", "reply": response.reply_text}

    except Exception as e:
        print(f"Meta Webhook Error: {e}")

    return {"status": "ok"}

# 3. Twilio WhatsApp Webhook (POST)
@app.post("/api/whatsapp/twilio")
async def handle_twilio_whatsapp_inbound(request: Request):
    form_data = await request.form()
    from_phone = form_data.get("From", "whatsapp_user")
    msg_text = form_data.get("Body", "")

    response = agent_core.process_message(msg_text, user_id=from_phone)

    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response.reply_text}</Message>
</Response>"""
    return Response(content=twiml_response, media_type="application/xml")

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
