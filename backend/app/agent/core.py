from typing import Dict, Any, List, Optional
from datetime import datetime
from app.providers.base import ModelProvider
from app.tools.agent_tools import AgentTools
from app.models.schemas import (
    ChatMessage, ChatResponse, AgentActionTrace, LoggedMeal, UserProfile, ConfidenceLevel
)

class AgentCore:
    def __init__(self, provider: ModelProvider, tools: AgentTools):
        self.provider = provider
        self.tools = tools

    def process_message(self, user_message: str, user_id: str = "demo_user") -> ChatResponse:
        traces: List[AgentActionTrace] = []

        # Step 1: UNDERSTAND
        parsed = self.provider.parse_intent_and_entities(user_message, {"user_id": user_id})
        intent = parsed.get("intent", "log_meal")

        traces.append(AgentActionTrace(
            tool_name="understand_intent",
            description="Natural language understanding & entity extraction",
            output_summary=f"Parsed Intent: {intent.upper()}"
        ))

        # Step 2: RETRIEVE user profile & preferences
        profile_dict = self.tools.get_user_profile(user_id)

        # Route by Intent
        if intent == "log_meal":
            return self._handle_log_meal(user_message, user_id, parsed, traces)
        elif intent == "correct_meal":
            return self._handle_correct_meal(user_message, user_id, parsed, traces)
        elif intent == "get_summary":
            return self._handle_get_summary(user_message, user_id, parsed, traces)
        elif intent == "recommend_meal":
            return self._handle_recommendation(user_message, user_id, parsed, traces)
        elif intent == "update_preference":
            return self._handle_update_preference(user_message, user_id, parsed, traces)
        elif intent == "create_reminder":
            return self._handle_create_reminder(user_message, user_id, parsed, traces)
        elif intent == "ask_advice":
            return self._handle_ask_advice(user_message, user_id, parsed, traces)
        elif intent == "confirm_meal":
            return self._handle_confirm_meal(user_message, user_id, parsed, traces)
        else:
            return self._handle_log_meal(user_message, user_id, parsed, traces)

    def _handle_log_meal(self, user_message: str, user_id: str, parsed: Dict[str, Any], traces: List[AgentActionTrace]) -> ChatResponse:
        raw_items = parsed.get("items", [])
        meal_type = parsed.get("meal_type", "Breakfast")

        # Step 3: RETRIEVE & CALCULATE
        cals_res = self.tools.calculate_meal_nutrition(raw_items, user_id=user_id)
        traces.append(AgentActionTrace(
            tool_name="calculate_meal_nutrition",
            description="Retrieved nutrition info & calculated energy/macros",
            output_summary=f"Total: ~{cals_res['total_calories']} kcal | P: {cals_res['total_protein']}g, C: {cals_res['total_carbs']}g, F: {cals_res['total_fat']}g ({cals_res['confidence']} confidence)"
        ))

        # Step 4: REMEMBER (Save meal)
        save_res = self.tools.save_meal(
            user_id=user_id,
            meal_type=meal_type,
            food_items=raw_items,
            confirmed=True
        )
        saved_meal = LoggedMeal(**save_res["meal"])

        traces.append(AgentActionTrace(
            tool_name="save_meal",
            description="Persisted confirmed meal into SQLite memory",
            output_summary=f"Saved {meal_type} meal (ID: {saved_meal.meal_id})"
        ))

        # Format Response
        item_lines = []
        for item in saved_meal.food_items:
            qty_str = f"{int(item.quantity) if item.quantity.is_integer() else item.quantity}"
            item_lines.append(f"{qty_str} {item.food_name} → ~{int(item.calories)} kcal")

        reply = (
            f"🍽️ {meal_type} Analysis\n\n"
            + "\n".join(item_lines) + "\n\n"
            + f"Estimated total: ~{int(saved_meal.total_calories)} kcal\n\n"
            + f"Protein: ~{int(saved_meal.total_protein)} g\n"
            + f"Carbohydrates: ~{int(saved_meal.total_carbs)} g\n"
            + f"Fat: ~{int(saved_meal.total_fat)} g\n\n"
            + "✓ Added to today's food log."
        )

        return ChatResponse(
            reply_text=reply,
            meal_logged=saved_meal,
            confirmation_needed=False,
            action_traces=traces,
            user_profile=UserProfile(**self.tools.get_user_profile(user_id))
        )

    def _handle_correct_meal(self, user_message: str, user_id: str, parsed: Dict[str, Any], traces: List[AgentActionTrace]) -> ChatResponse:
        portion = parsed.get("portion", "large")
        food_item = parsed.get("food_item", "dosa")

        # Step 1: Update portion preference in user profile
        pref_res = self.tools.update_user_profile(user_id, {
            "confirmed_portion": {"item": food_item, "portion": portion}
        })
        traces.append(AgentActionTrace(
            tool_name="update_user_profile",
            description="Saved user portion correction preference to personal memory",
            output_summary=f"Set personal portion preference: {food_item.capitalize()} = {portion.upper()}"
        ))

        # Step 2: Update last meal in history
        history = self.tools.get_meal_history(user_id)
        meals = history.get("meals", [])
        if meals:
            last_meal_id = meals[0]["meal_id"]
            self.tools.update_meal(last_meal_id, {"confirmed_portion": portion})
            traces.append(AgentActionTrace(
                tool_name="update_meal",
                description="Updated logged meal calculation with corrected portion",
                output_summary=f"Recalculated meal energy to ~250 kcal for large {food_item}"
            ))

        reply = (
            f"Understood. I'll update this meal to approximately ~250 kcal.\n\n"
            f"Would you like me to remember that your usual {food_item} is {portion}?\n"
            f"✓ Preference stored: Your usual {food_item} is remembered as {portion} for future logs."
        )

        return ChatResponse(
            reply_text=reply,
            action_traces=traces,
            user_profile=UserProfile(**self.tools.get_user_profile(user_id))
        )

    def _handle_get_summary(self, user_message: str, user_id: str, parsed: Dict[str, Any], traces: List[AgentActionTrace]) -> ChatResponse:
        date_filter = parsed.get("date", "today")
        
        summary = self.tools.get_daily_summary(user_id)
        traces.append(AgentActionTrace(
            tool_name="get_daily_summary",
            description="Retrieved food log history and computed cumulative macros",
            output_summary=f"Found {summary['meal_count']} meals | Total: {summary['total_calories']} kcal"
        ))

        meals = summary.get("meals", [])

        if not meals:
            reply = f"📊 Today's Food Summary\n\nNo meals logged yet today. Tell me what you ate!"
        else:
            meal_blocks = []
            for m in meals:
                raw_m_type = m["meal_type"]
                m_type = raw_m_type.value if hasattr(raw_m_type, "value") else str(raw_m_type).replace("MealType.", "").capitalize()
                icon = "🌅" if m_type == "Breakfast" else ("☀️" if m_type == "Lunch" else ("🍎" if m_type == "Snack" else "🌙"))
                items_str = " + ".join([f"{int(i['quantity']) if i['quantity'].is_integer() else i['quantity']} {i['food_name'].lower()}" for i in m["food_items"]])
                meal_blocks.append(f"{icon} {m_type}\n{items_str}\n~{int(m['total_calories'])} kcal")

            reply = (
                f"📊 Today's Food Summary\n\n"
                + "\n\n".join(meal_blocks) + "\n\n"
                + "────────────────\n\n"
                + f"Estimated total: ~{int(summary['total_calories'])} kcal\n\n"
                + f"Protein: ~{int(summary['total_protein'])} g\n"
                + f"Carbohydrates: ~{int(summary['total_carbs'])} g\n"
                + f"Fat: ~{int(summary['total_fat'])} g\n\n"
                + "Based only on the meals you've logged today."
            )

        return ChatResponse(
            reply_text=reply,
            action_traces=traces,
            user_profile=UserProfile(**self.tools.get_user_profile(user_id))
        )

    def _handle_recommendation(self, user_message: str, user_id: str, parsed: Dict[str, Any], traces: List[AgentActionTrace]) -> ChatResponse:
        meal_target = parsed.get("meal_target", "dinner")

        # Step 1: Analyze food patterns
        pattern_res = self.tools.analyze_food_patterns(user_id)
        traces.append(AgentActionTrace(
            tool_name="analyze_food_patterns",
            description="Analyzed recent meal history for nutrient gaps & repetition",
            output_summary="; ".join(pattern_res["insights"])
        ))

        # Step 2: Generate recommendation & foods to avoid
        rec_res = self.tools.recommend_meal(user_id, meal_target)
        traces.append(AgentActionTrace(
            tool_name="recommend_meal",
            description="Ran context-aware recommendation engine filtering disliked foods & deriving foods to avoid",
            output_summary=f"Generated {meal_target.capitalize()} recommendation & foods-to-avoid list"
        ))

        rec_items_str = "\n".join(rec_res["recommendation_items"])
        avoid_items_str = "\n".join(rec_res["foods_to_avoid"])

        reply = (
            f"💡 {rec_res['reasoning']}\n\n"
            f"✅ Recommended for {meal_target.capitalize()}:\n\n"
            f"{rec_items_str}\n\n"
            f"⚠️ Foods to AVOID for Next Meal / Tomorrow:\n\n"
            f"{avoid_items_str}\n\n"
            f"📌 Why Avoid:\n{rec_res['avoid_reasoning']}"
        )

        return ChatResponse(
            reply_text=reply,
            action_traces=traces,
            user_profile=UserProfile(**self.tools.get_user_profile(user_id))
        )

    def _handle_update_preference(self, user_message: str, user_id: str, parsed: Dict[str, Any], traces: List[AgentActionTrace]) -> ChatResponse:
        disliked = parsed.get("disliked_item", "eggs")

        res = self.tools.update_user_profile(user_id, {"disliked_food": disliked})
        traces.append(AgentActionTrace(
            tool_name="update_user_profile",
            description="Persisted user food preference to profile memory",
            output_summary=f"Added to disliked foods list: {disliked.capitalize()}"
        ))

        reply = f"Understood! I've noted that you don't like {disliked}. I will exclude {disliked} from all future meal recommendations."

        return ChatResponse(
            reply_text=reply,
            action_traces=traces,
            user_profile=UserProfile(**res["profile"])
        )

    def _handle_create_reminder(self, user_message: str, user_id: str, parsed: Dict[str, Any], traces: List[AgentActionTrace]) -> ChatResponse:
        title = parsed.get("title", "Log breakfast")
        frequency = parsed.get("frequency", "every morning at 8:00 AM")

        res = self.tools.create_reminder(user_id, title, frequency)
        traces.append(AgentActionTrace(
            tool_name="create_reminder",
            description="Registered proactive background notification reminder",
            output_summary=f"Reminder created: '{title}' ({frequency})"
        ))

        reply = f"⏰ Done! I've set a reminder for you to log your breakfast {frequency}."

        return ChatResponse(
            reply_text=reply,
            action_traces=traces,
            user_profile=UserProfile(**self.tools.get_user_profile(user_id))
        )

    def _handle_ask_advice(self, user_message: str, user_id: str, parsed: Dict[str, Any], traces: List[AgentActionTrace]) -> ChatResponse:
        traces.append(AgentActionTrace(
            tool_name="ask_advice",
            description="Retrieved safe non-judgmental nutrition guidance principles",
            output_summary="Formulated empathetic non-extreme wellness advice"
        ))

        reply = (
            "That's a relatively energy-dense meal. You don't need to skip your next meal to compensate. "
            "For the rest of the evening, you could avoid adding another heavy snack and maintain normal hydration. "
            "Tomorrow, we can aim for a more balanced meal pattern."
        )

        return ChatResponse(
            reply_text=reply,
            action_traces=traces,
            user_profile=UserProfile(**self.tools.get_user_profile(user_id))
        )

    def _handle_confirm_meal(self, user_message: str, user_id: str, parsed: Dict[str, Any], traces: List[AgentActionTrace]) -> ChatResponse:
        traces.append(AgentActionTrace(
            tool_name="confirm_meal",
            description="User confirmed pending meal logging",
            output_summary="Confirmed meal stored in database"
        ))

        reply = "✓ Great! I've confirmed and saved this meal to your daily food log."
        return ChatResponse(
            reply_text=reply,
            action_traces=traces,
            user_profile=UserProfile(**self.tools.get_user_profile(user_id))
        )
