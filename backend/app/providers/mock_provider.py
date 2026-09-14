import re
from typing import Dict, Any, List, Optional
from app.providers.base import ModelProvider

class LocalModelProvider(ModelProvider):
    """
    Local Smart NLP Model Provider.
    Extracts intents and entities using robust regex/rule-based NLP parsing.
    Operates 100% offline without AWS or external cloud dependencies.
    """
    def parse_intent_and_entities(self, user_message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        msg_lower = user_message.lower().strip()

        # 1. Update preference intent
        if re.search(r"(don't|do not|dislike|hate|avoid) (eat|like|have)?\s*([a-zA-Z\s]+)", msg_lower):
            match = re.search(r"(don't|do not|dislike|hate|avoid) (eat|like|have)?\s*([a-zA-Z\s]+)", msg_lower)
            disliked = match.group(3).strip() if match else "eggs"
            disliked = re.sub(r"\b(anymore|at all|please)\b", "", disliked).strip()
            return {
                "intent": "update_preference",
                "disliked_item": disliked
            }

        # 2. Meal Correction (e.g. "My dosa was large", "it was large")
        if re.search(r"(dosa|meal|portion|was|is)\s+(large|small|medium|big)", msg_lower) or msg_lower.startswith("my dosa was"):
            portion = "large" if "large" in msg_lower or "big" in msg_lower else ("small" if "small" in msg_lower else "medium")
            return {
                "intent": "correct_meal",
                "food_item": "dosa",
                "portion": portion
            }

        # 3. Create reminder intent
        if re.search(r"\bremind\b", msg_lower):
            frequency = "every morning at 8:00 AM"
            if "night" in msg_lower or "evening" in msg_lower:
                frequency = "every evening at 8:00 PM"
            return {
                "intent": "create_reminder",
                "title": "Log breakfast",
                "frequency": frequency
            }

        # 4. Recommendation intent
        if re.search(r"(suggest|recommend|what should i eat|what to eat)", msg_lower):
            meal_target = "dinner"
            if "lunch" in msg_lower:
                meal_target = "lunch"
            elif "breakfast" in msg_lower:
                meal_target = "breakfast"
            elif "snack" in msg_lower:
                meal_target = "snack"
            return {
                "intent": "recommend_meal",
                "meal_target": meal_target
            }

        # 5. Daily summary / History intent
        if re.search(r"(what (have|did) i (eat|eaten)|today|yesterday|this week|last 7 days|history)", msg_lower):
            target_date = "today"
            if "yesterday" in msg_lower:
                target_date = "yesterday"
            elif "week" in msg_lower or "7 days" in msg_lower:
                target_date = "week"
            return {
                "intent": "get_summary",
                "date": target_date
            }

        # 6. Advice / "What should I do now?" intent
        if re.search(r"(what should i do|what to do now|overate|heavy meal)", msg_lower):
            return {
                "intent": "ask_advice"
            }

        # 7. Confirmation intent ("yes", "confirm", "add it")
        if msg_lower in ["yes", "yeah", "sure", "add it", "confirm", "save"]:
            return {
                "intent": "confirm_meal"
            }

        # 8. Log meal intent (Default for food entries)
        items = self._extract_food_items(msg_lower)
        meal_type = self._detect_meal_type(msg_lower)

        return {
            "intent": "log_meal",
            "items": items,
            "meal_type": meal_type
        }

    def _detect_meal_type(self, text: str) -> str:
        if "breakfast" in text or "morning" in text:
            return "Breakfast"
        elif "lunch" in text or "afternoon" in text:
            return "Lunch"
        elif "snack" in text or "evening" in text or "tea" in text:
            return "Snack"
        elif "dinner" in text or "night" in text:
            return "Dinner"
        return "Other"

    def _extract_food_items(self, text: str) -> List[Dict[str, Any]]:
        # Word-to-number dictionary
        word_to_num = {
            "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "half": 0.5, "glass of": 1, "plate of": 1, "one plate": 1
        }

        # Known food patterns
        known_foods = [
            "idli", "idlis", "idly", "vada", "vadai", "egg", "eggs", "dosa", "dosai",
            "chicken biryani", "biryani", "biriyani", "buttermilk", "moru", "chaas",
            "pongal", "upma", "rice", "sambar", "rasam", "curd", "chapati", "roti",
            "parotta", "paratha", "dal", "vegetable poriyal", "chicken", "fish", "banana",
            "bananas", "apple", "orange", "milk", "tea", "coffee", "nuts", "bread", "biscuits", "pizza"
        ]

        extracted = []
        # Clause splits (e.g. "3 idlis, one vada and 2 eggs")
        clauses = re.split(r"[,+&]| and ", text)

        for clause in clauses:
            clause_str = clause.strip()
            if not clause_str:
                continue

            found_food = None
            for food in known_foods:
                if re.search(r"\b" + re.escape(food) + r"\b", clause_str):
                    found_food = food
                    break

            if found_food:
                # Quantity extraction
                qty = 1.0
                unit = "piece"
                num_match = re.search(r"(\d+(\.\d+)?)", clause_str)
                if num_match:
                    qty = float(num_match.group(1))
                else:
                    for word, val in word_to_num.items():
                        if re.search(r"\b" + re.escape(word) + r"\b", clause_str):
                            qty = val
                            break

                # Unit detection
                if "glass" in clause_str:
                    unit = "glass"
                elif "plate" in clause_str or "biryani" in found_food:
                    unit = "plate"
                elif "cup" in clause_str:
                    unit = "cup"
                elif "slice" in clause_str:
                    unit = "slice"

                extracted.append({
                    "food_name": found_food,
                    "quantity": qty,
                    "unit": unit
                })

        if not extracted:
            # Fallback single food extraction
            extracted.append({
                "food_name": text.replace("i ate", "").replace("i had", "").strip(),
                "quantity": 1.0,
                "unit": "serving"
            })

        return extracted

    def generate_response(
        self,
        intent: str,
        user_message: str,
        tool_results: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> str:
        # Handled dynamically by agent core based on tool results & format requirements
        return ""
