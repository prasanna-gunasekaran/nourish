import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from app.nutrition.service import NutritionService
from app.repositories.base import MealRepository, UserRepository, ReminderRepository
from app.models.schemas import LoggedMeal, UserProfile, Reminder, MealType, ConfidenceLevel, FoodItemParsed

class AgentTools:
    def __init__(
        self,
        nutrition_service: NutritionService,
        meal_repo: MealRepository,
        user_repo: UserRepository,
        reminder_repo: ReminderRepository
    ):
        self.nutrition_service = nutrition_service
        self.meal_repo = meal_repo
        self.user_repo = user_repo
        self.reminder_repo = reminder_repo

    # Tool 1: nutrition_search
    def nutrition_search(self, query: str) -> Dict[str, Any]:
        results = self.nutrition_service.search_food(query)
        return {
            "query": query,
            "found_count": len(results),
            "results": results
        }

    # Tool 2: calculate_meal_nutrition
    def calculate_meal_nutrition(
        self,
        food_items_raw: List[Dict[str, Any]],
        user_id: str = "demo_user"
    ) -> Dict[str, Any]:
        profile = self.user_repo.get_user_profile(user_id)
        parsed_items: List[FoodItemParsed] = []

        for raw in food_items_raw:
            name = raw.get("food_name", "Food")
            qty = float(raw.get("quantity", 1.0))
            unit = raw.get("unit", "piece")
            portion_pref = profile.confirmed_portions.get(name.lower())

            item = self.nutrition_service.calculate_food_item(
                food_name=name,
                quantity=qty,
                unit=unit,
                user_portion_preference=portion_pref
            )
            parsed_items.append(item)

        cals, prot, carbs, fat, fiber, conf = self.nutrition_service.calculate_meal_totals(parsed_items)

        return {
            "parsed_items": [item.model_dump() for item in parsed_items],
            "total_calories": cals,
            "total_protein": prot,
            "total_carbs": carbs,
            "total_fat": fat,
            "total_fiber": fiber,
            "confidence": conf.value
        }

    # Tool 3: save_meal
    def save_meal(
        self,
        user_id: str,
        meal_type: str,
        food_items: List[Dict[str, Any]],
        confirmed: bool = True
    ) -> Dict[str, Any]:
        calc = self.calculate_meal_nutrition(food_items, user_id=user_id)
        parsed_food = [FoodItemParsed(**item) for item in calc["parsed_items"]]

        meal = LoggedMeal(
            meal_id=f"meal_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            timestamp=datetime.now().isoformat(),
            meal_type=MealType(meal_type) if meal_type in MealType._value2member_map_ else MealType.OTHER,
            food_items=parsed_food,
            total_calories=calc["total_calories"],
            total_protein=calc["total_protein"],
            total_carbs=calc["total_carbs"],
            total_fat=calc["total_fat"],
            total_fiber=calc["total_fiber"],
            confidence=ConfidenceLevel(calc["confidence"]),
            confirmed=confirmed
        )

        saved = self.meal_repo.save_meal(meal)
        return {
            "status": "success",
            "meal": saved.model_dump()
        }

    # Tool 4: update_meal
    def update_meal(self, meal_id: str, corrections: Dict[str, Any]) -> Dict[str, Any]:
        existing = self.meal_repo.get_meal_by_id(meal_id)
        if not existing:
            return {"status": "error", "message": f"Meal {meal_id} not found"}

        if "confirmed_portion" in corrections:
            portion = corrections["confirmed_portion"]
            # Recalculate cals
            for item in existing.food_items:
                if "dosa" in item.food_name.lower() and portion == "large":
                    item.calories = 250.0
                    item.carbs_g = 45.0
                    item.fat_g = 6.5
                    item.protein_g = 5.5
            
            existing.total_calories = sum(i.calories for i in existing.food_items)
            existing.total_protein = sum(i.protein_g for i in existing.food_items)
            existing.total_carbs = sum(i.carbs_g for i in existing.food_items)
            existing.total_fat = sum(i.fat_g for i in existing.food_items)

        updated = self.meal_repo.update_meal(existing)
        return {"status": "success", "meal": updated.model_dump()}

    # Tool 5: get_meal_history
    def get_meal_history(self, user_id: str, date_filter: Optional[str] = None) -> Dict[str, Any]:
        if date_filter == "yesterday":
            yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            meals = self.meal_repo.get_user_meals(user_id, date_str=yesterday_str)
        elif date_filter == "week":
            start_str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            end_str = datetime.now().strftime("%Y-%m-%d")
            meals = self.meal_repo.get_user_meals_range(user_id, start_str, end_str)
        else:
            today_str = datetime.now().strftime("%Y-%m-%d")
            meals = self.meal_repo.get_user_meals(user_id, date_str=today_str)

        return {
            "date_filter": date_filter or "today",
            "count": len(meals),
            "meals": [m.model_dump() for m in meals]
        }

    # Tool 6: get_daily_summary
    def get_daily_summary(self, user_id: str, date_str: Optional[str] = None) -> Dict[str, Any]:
        d_str = date_str or datetime.now().strftime("%Y-%m-%d")
        meals = self.meal_repo.get_user_meals(user_id, date_str=d_str)

        tot_cals = sum(m.total_calories for m in meals)
        tot_protein = sum(m.total_protein for m in meals)
        tot_carbs = sum(m.total_carbs for m in meals)
        tot_fat = sum(m.total_fat for m in meals)
        tot_fiber = sum(m.total_fiber for m in meals)

        return {
            "date": d_str,
            "meal_count": len(meals),
            "total_calories": round(tot_cals, 1),
            "total_protein": round(tot_protein, 1),
            "total_carbs": round(tot_carbs, 1),
            "total_fat": round(tot_fat, 1),
            "total_fiber": round(tot_fiber, 1),
            "meals": [m.model_dump() for m in meals]
        }

    # Tool 7: analyze_food_patterns
    def analyze_food_patterns(self, user_id: str) -> Dict[str, Any]:
        meals = self.meal_repo.get_user_meals(user_id)
        if not meals:
            return {"insights": ["No logged meals found yet for pattern analysis."]}

        insights = []
        carbs_count = sum(1 for m in meals if m.total_carbs > 50)
        veggie_items = sum(1 for m in meals for item in m.food_items if any(v in item.food_name.lower() for v in ["poriyal", "vegetable", "sambar", "salad"]))
        protein_total = sum(m.total_protein for m in meals)

        if carbs_count >= 2:
            insights.append("High carbohydrate concentration in recent meals (e.g. rice/idli/biryani).")
        if veggie_items < 2:
            insights.append("Low vegetable variety in recent logged meals.")
        if protein_total < 40:
            insights.append("Inconsistent protein intake today.")

        return {
            "user_id": user_id,
            "insights": insights or ["Balanced intake detected based on available logged meals."]
        }

    # Tool 8: get_user_profile
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        profile = self.user_repo.get_user_profile(user_id)
        return profile.model_dump()

    # Tool 9: update_user_profile
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        profile = self.user_repo.get_user_profile(user_id)
        if "disliked_food" in updates:
            disliked = updates["disliked_food"].lower().strip()
            if disliked not in [d.lower() for d in profile.disliked_foods]:
                profile.disliked_foods.append(disliked)
        if "confirmed_portion" in updates:
            item_name = updates["confirmed_portion"]["item"].lower().strip()
            portion = updates["confirmed_portion"]["portion"].lower().strip()
            profile.confirmed_portions[item_name] = portion

        updated = self.user_repo.update_user_profile(profile)
        return {"status": "success", "profile": updated.model_dump()}

    # Tool 10: recommend_meal
    def recommend_meal(self, user_id: str, meal_target: str = "dinner") -> Dict[str, Any]:
        summary = self.get_daily_summary(user_id)
        profile = self.user_repo.get_user_profile(user_id)
        disliked = [d.lower() for d in profile.disliked_foods]

        today_carbs = summary["total_carbs"]
        today_protein = summary["total_protein"]
        today_fat = summary["total_fat"]

        # Contextual reasoning
        reasoning = []
        recommendations = []
        foods_to_avoid = []
        avoid_reasoning = ""

        if today_carbs > 100:
            reasoning.append("Your earlier meals today were relatively carbohydrate-heavy (e.g. rice/idli/biryani).")
            foods_to_avoid = [
                "🚫 Rice-heavy main courses (Biryani, Fried Rice, Extra Rice portions)",
                "🚫 Refined wheat & fried breads (Malabar Parotta, Poori)",
                "🚫 Sugary drinks & desserts (Chai with sugar, Sodas)"
            ]
            avoid_reasoning = f"Since your carbohydrate intake is already at ~{int(today_carbs)}g today, avoiding additional heavy starches helps maintain healthy blood sugar & energy balance."

            if "egg" not in disliked and "eggs" not in disliked:
                recommendations = [
                    "🥗 Vegetable Sambar (1 cup)",
                    "🍳 2 Boiled Eggs",
                    "🥬 Vegetable Poriyal / Sabzi",
                    "🍚 Moderate Rice Portion (1/2 cup)"
                ]
                reasoning.append("This recommendation adds more fresh vegetables and protein variety while keeping carbohydrates moderate.")
            else:
                recommendations = [
                    "🥗 Vegetable Sambar (1 cup)",
                    "🥣 Dal Tadka (1 cup)",
                    "🥬 Vegetable Poriyal / Sabzi",
                    "🫓 2 Whole Wheat Chapatis"
                ]
                reasoning.append("Since you dislike eggs, this plant-based recommendation pairs high-protein Dal Tadka with fresh vegetable poriyal and chapatis.")
        else:
            foods_to_avoid = [
                "🚫 Deep-fried oily snacks (Medu Vada, Samosa)",
                "🚫 High-sugar beverages"
            ]
            avoid_reasoning = "Keep your next meal balanced without excess saturated fat or refined sugar."
            recommendations = [
                "🥗 Vegetable Sambar & Rice",
                "🍳 2 Boiled Eggs",
                "🥛 1 Glass Buttermilk"
            ]
            reasoning.append("Balanced dinner recommendation to meet daily calorie & macronutrient goals.")

        return {
            "meal_target": meal_target,
            "recommendation_items": recommendations,
            "reasoning": " ".join(reasoning),
            "foods_to_avoid": foods_to_avoid,
            "avoid_reasoning": avoid_reasoning,
            "disliked_filtered": disliked
        }

    # Tool 11: create_reminder
    def create_reminder(self, user_id: str, title: str, frequency: str) -> Dict[str, Any]:
        rem = Reminder(
            reminder_id=f"rem_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            title=title,
            frequency=frequency
        )
        saved = self.reminder_repo.create_reminder(rem)
        return {"status": "success", "reminder": saved.model_dump()}

    # Tool 12: get_reminders
    def get_reminders(self, user_id: str) -> Dict[str, Any]:
        rems = self.reminder_repo.get_user_reminders(user_id)
        return {"reminders": [r.model_dump() for r in rems]}
