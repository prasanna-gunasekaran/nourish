from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class MealType(str, Enum):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    SNACK = "Snack"
    DINNER = "Dinner"
    OTHER = "Other"

class FoodItemParsed(BaseModel):
    food_name: str
    quantity: float
    unit: str
    preparation: Optional[str] = None
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float = 0.0
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    db_item_id: Optional[str] = None

class LoggedMeal(BaseModel):
    meal_id: str
    user_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    meal_type: MealType
    food_items: List[FoodItemParsed]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_fiber: float = 0.0
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    confirmed: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class UserProfile(BaseModel):
    user_id: str
    disliked_foods: List[str] = Field(default_factory=list)
    food_preferences: List[str] = Field(default_factory=list)
    dietary_preferences: List[str] = Field(default_factory=list)
    confirmed_portions: Dict[str, str] = Field(default_factory=dict) # e.g. {"dosa": "large"}
    calorie_goal: int = 2000
    protein_goal: int = 70
    carbs_goal: int = 220
    fat_goal: int = 65

class Reminder(BaseModel):
    reminder_id: str
    user_id: str
    title: str
    frequency: str # e.g. "every morning at 8:00 AM"
    active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class AgentActionTrace(BaseModel):
    tool_name: str
    description: str
    input_data: Optional[Dict[str, Any]] = None
    output_summary: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ChatMessage(BaseModel):
    id: str
    sender: str  # "user" | "nourish" | "system"
    text: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    meal_data: Optional[LoggedMeal] = None
    confirmation_required: bool = False
    pending_meal: Optional[LoggedMeal] = None
    action_traces: List[AgentActionTrace] = Field(default_factory=list)

class ChatRequest(BaseModel):
    user_id: str = "demo_user"
    message: str
    image_base64: Optional[str] = None
    voice_base64: Optional[str] = None

class ChatResponse(BaseModel):
    reply_text: str
    meal_logged: Optional[LoggedMeal] = None
    confirmation_needed: bool = False
    pending_meal: Optional[LoggedMeal] = None
    action_traces: List[AgentActionTrace] = Field(default_factory=list)
    user_profile: Optional[UserProfile] = None
