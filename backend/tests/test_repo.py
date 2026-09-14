import pytest
import os
from app.repositories.sqlite_repo import SQLiteDatabase, SQLiteMealRepository, SQLiteUserRepository, SQLiteReminderRepository
from app.models.schemas import LoggedMeal, UserProfile, Reminder, MealType, ConfidenceLevel, FoodItemParsed

def test_sqlite_repositories(tmp_path):
    db_file = str(tmp_path / "test_nourish.db")
    db = SQLiteDatabase(db_file)
    meal_repo = SQLiteMealRepository(db)
    user_repo = SQLiteUserRepository(db)
    reminder_repo = SQLiteReminderRepository(db)

    # User profile test
    profile = user_repo.get_user_profile("user_1")
    assert profile.user_id == "user_1"
    profile.disliked_foods.append("eggs")
    user_repo.update_user_profile(profile)

    updated_p = user_repo.get_user_profile("user_1")
    assert "eggs" in updated_p.disliked_foods

    # Meal test
    meal = LoggedMeal(
        meal_id="m1",
        user_id="user_1",
        meal_type=MealType.BREAKFAST,
        food_items=[
            FoodItemParsed(food_name="Idli", quantity=3, unit="piece", calories=174, protein_g=6, carbs_g=36, fat_g=0.6)
        ],
        total_calories=174,
        total_protein=6,
        total_carbs=36,
        total_fat=0.6,
        confidence=ConfidenceLevel.HIGH
    )
    meal_repo.save_meal(meal)

    retrieved = meal_repo.get_user_meals("user_1")
    assert len(retrieved) == 1
    assert retrieved[0].total_calories == 174

    # Reminder test
    rem = Reminder(reminder_id="r1", user_id="user_1", title="Log breakfast", frequency="every morning")
    reminder_repo.create_reminder(rem)
    rems = reminder_repo.get_user_reminders("user_1")
    assert len(rems) == 1
    assert rems[0].title == "Log breakfast"
