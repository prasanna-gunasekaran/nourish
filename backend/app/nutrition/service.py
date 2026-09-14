import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from app.models.schemas import FoodItemParsed, ConfidenceLevel

class NutritionService:
    def __init__(self, data_path: Optional[str] = None):
        if not data_path:
            data_path = str(Path(__file__).parent.parent.parent / "data" / "nutrition_data.json")
        self.data_path = data_path
        self.food_db: List[Dict[str, Any]] = []
        self._load_data()

    def _load_data(self):
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.food_db = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load nutrition data from {self.data_path}: {e}")
            self.food_db = []

    def search_food(self, query: str) -> List[Dict[str, Any]]:
        query_clean = query.lower().strip()
        results = []
        for item in self.food_db:
            if query_clean in item["id"].lower() or query_clean in item["name"].lower():
                results.append(item)
                continue
            for alias in item.get("aliases", []):
                if query_clean in alias.lower() or alias.lower() in query_clean:
                    results.append(item)
                    break
        return results

    def get_best_match(self, food_name: str) -> Optional[Dict[str, Any]]:
        matches = self.search_food(food_name)
        if matches:
            return matches[0]
        
        # Word token matching
        tokens = food_name.lower().split()
        for token in tokens:
            if len(token) > 2:
                for item in self.food_db:
                    if token in item["name"].lower() or any(token in a.lower() for a in item.get("aliases", [])):
                        return item
        return None

    def calculate_food_item(
        self,
        food_name: str,
        quantity: float = 1.0,
        unit: Optional[str] = None,
        user_portion_preference: Optional[str] = None
    ) -> FoodItemParsed:
        db_match = self.get_best_match(food_name)

        if not db_match:
            # Fallback estimation for unknown food
            return FoodItemParsed(
                food_name=food_name.capitalize(),
                quantity=quantity,
                unit=unit or "serving",
                calories=round(200.0 * quantity, 1),
                protein_g=round(5.0 * quantity, 1),
                carbs_g=round(25.0 * quantity, 1),
                fat_g=round(8.0 * quantity, 1),
                fiber_g=round(2.0 * quantity, 1),
                confidence=ConfidenceLevel.LOW,
                db_item_id=None
            )

        # Check if user has a confirmed portion preference (e.g., dosa -> large)
        if "dosa" in db_match["id"].lower() and user_portion_preference == "large":
            large_match = self.get_best_match("dosa large")
            if large_match:
                db_match = large_match

        base_cals = db_match["calories_per_unit"]
        base_protein = db_match["protein_g"]
        base_carbs = db_match["carbs_g"]
        base_fat = db_match["fat_g"]
        base_fiber = db_match.get("fiber_g", 0.0)

        # Multiplier based on unit if different
        multiplier = quantity
        confidence = ConfidenceLevel.HIGH

        if unit:
            u_clean = unit.lower()
            if u_clean in ["plate", "bowl"] and db_match["serving_unit"] in ["piece", "cup"]:
                multiplier = quantity * 1.5
                confidence = ConfidenceLevel.MEDIUM
            elif u_clean in ["half", "half a", "half plate"]:
                multiplier = 0.5
                confidence = ConfidenceLevel.MEDIUM

        if db_match["id"] in ["chicken_biryani", "south_indian_thali", "pizza_slice"] and confidence != ConfidenceLevel.LOW:
            confidence = ConfidenceLevel.MEDIUM  # High oil/portion variability

        return FoodItemParsed(
            food_name=db_match["name"],
            quantity=quantity,
            unit=unit or db_match["serving_unit"],
            calories=round(base_cals * multiplier, 1),
            protein_g=round(base_protein * multiplier, 1),
            carbs_g=round(base_carbs * multiplier, 1),
            fat_g=round(base_fat * multiplier, 1),
            fiber_g=round(base_fiber * multiplier, 1),
            confidence=confidence,
            db_item_id=db_match["id"]
        )

    def calculate_meal_totals(self, items: List[FoodItemParsed]) -> Tuple[float, float, float, float, float, ConfidenceLevel]:
        tot_cals = sum(item.calories for item in items)
        tot_protein = sum(item.protein_g for item in items)
        tot_carbs = sum(item.carbs_g for item in items)
        tot_fat = sum(item.fat_g for item in items)
        tot_fiber = sum(item.fiber_g for item in items)

        confidences = [item.confidence for item in items]
        if ConfidenceLevel.LOW in confidences:
            overall_conf = ConfidenceLevel.LOW
        elif ConfidenceLevel.MEDIUM in confidences:
            overall_conf = ConfidenceLevel.MEDIUM
        else:
            overall_conf = ConfidenceLevel.HIGH

        return (
            round(tot_cals, 1),
            round(tot_protein, 1),
            round(tot_carbs, 1),
            round(tot_fat, 1),
            round(tot_fiber, 1),
            overall_conf
        )
