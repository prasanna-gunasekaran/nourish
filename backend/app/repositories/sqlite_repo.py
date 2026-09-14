import sqlite3
import json
from typing import List, Optional
from pathlib import Path
from app.models.schemas import LoggedMeal, UserProfile, Reminder, MealType, ConfidenceLevel, FoodItemParsed
from app.repositories.base import MealRepository, UserRepository, ReminderRepository

class SQLiteDatabase:
    def __init__(self, db_path: str = "nourish.db"):
        self.db_path = db_path
        self._init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS meals (
                meal_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                food_items TEXT NOT NULL,
                total_calories REAL NOT NULL,
                total_protein REAL NOT NULL,
                total_carbs REAL NOT NULL,
                total_fat REAL NOT NULL,
                total_fiber REAL NOT NULL,
                confidence TEXT NOT NULL,
                confirmed INTEGER NOT NULL,
                metadata TEXT
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                disliked_foods TEXT NOT NULL,
                food_preferences TEXT NOT NULL,
                dietary_preferences TEXT NOT NULL,
                confirmed_portions TEXT NOT NULL,
                calorie_goal INTEGER NOT NULL,
                protein_goal INTEGER NOT NULL,
                carbs_goal INTEGER NOT NULL,
                fat_goal INTEGER NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                reminder_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                frequency TEXT NOT NULL,
                active INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );
            """)
            conn.commit()

class SQLiteMealRepository(MealRepository):
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save_meal(self, meal: LoggedMeal) -> LoggedMeal:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            food_items_json = json.dumps([item.model_dump() for item in meal.food_items])
            metadata_json = json.dumps(meal.metadata)
            cursor.execute("""
            INSERT OR REPLACE INTO meals (
                meal_id, user_id, timestamp, meal_type, food_items,
                total_calories, total_protein, total_carbs, total_fat, total_fiber,
                confidence, confirmed, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                meal.meal_id, meal.user_id, meal.timestamp, meal.meal_type.value,
                food_items_json, meal.total_calories, meal.total_protein,
                meal.total_carbs, meal.total_fat, meal.total_fiber,
                meal.confidence.value, 1 if meal.confirmed else 0, metadata_json
            ))
            conn.commit()
        return meal

    def update_meal(self, meal: LoggedMeal) -> LoggedMeal:
        return self.save_meal(meal)

    def get_meal_by_id(self, meal_id: str) -> Optional[LoggedMeal]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM meals WHERE meal_id = ?", (meal_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_meal(row)

    def get_user_meals(self, user_id: str, date_str: Optional[str] = None) -> List[LoggedMeal]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if date_str:
                cursor.execute(
                    "SELECT * FROM meals WHERE user_id = ? AND timestamp LIKE ? ORDER BY timestamp DESC",
                    (user_id, f"{date_str}%")
                )
            else:
                cursor.execute(
                    "SELECT * FROM meals WHERE user_id = ? ORDER BY timestamp DESC",
                    (user_id,)
                )
            rows = cursor.fetchall()
            return [self._row_to_meal(r) for r in rows]

    def get_user_meals_range(self, user_id: str, start_date: str, end_date: str) -> List[LoggedMeal]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM meals WHERE user_id = ? AND timestamp >= ? AND timestamp <= ? ORDER BY timestamp DESC",
                (user_id, start_date, end_date + "T23:59:59")
            )
            rows = cursor.fetchall()
            return [self._row_to_meal(r) for r in rows]

    def delete_user_meals(self, user_id: str) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM meals WHERE user_id = ?", (user_id,))
            conn.commit()
        return True

    def _row_to_meal(self, row) -> LoggedMeal:
        raw_items = json.loads(row["food_items"])
        food_items = [FoodItemParsed(**item) for item in raw_items]
        return LoggedMeal(
            meal_id=row["meal_id"],
            user_id=row["user_id"],
            timestamp=row["timestamp"],
            meal_type=MealType(row["meal_type"]),
            food_items=food_items,
            total_calories=row["total_calories"],
            total_protein=row["total_protein"],
            total_carbs=row["total_carbs"],
            total_fat=row["total_fat"],
            total_fiber=row["total_fiber"],
            confidence=ConfidenceLevel(row["confidence"]),
            confirmed=bool(row["confirmed"]),
            metadata=json.loads(row["metadata"]) if row["metadata"] else {}
        )

class SQLiteUserRepository(UserRepository):
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def get_user_profile(self, user_id: str) -> UserProfile:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                # Default profile
                profile = UserProfile(user_id=user_id)
                self.update_user_profile(profile)
                return profile
            return UserProfile(
                user_id=row["user_id"],
                disliked_foods=json.loads(row["disliked_foods"]),
                food_preferences=json.loads(row["food_preferences"]),
                dietary_preferences=json.loads(row["dietary_preferences"]),
                confirmed_portions=json.loads(row["confirmed_portions"]),
                calorie_goal=row["calorie_goal"],
                protein_goal=row["protein_goal"],
                carbs_goal=row["carbs_goal"],
                fat_goal=row["fat_goal"]
            )

    def update_user_profile(self, profile: UserProfile) -> UserProfile:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO user_profiles (
                user_id, disliked_foods, food_preferences, dietary_preferences,
                confirmed_portions, calorie_goal, protein_goal, carbs_goal, fat_goal
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile.user_id,
                json.dumps(profile.disliked_foods),
                json.dumps(profile.food_preferences),
                json.dumps(profile.dietary_preferences),
                json.dumps(profile.confirmed_portions),
                profile.calorie_goal,
                profile.protein_goal,
                profile.carbs_goal,
                profile.fat_goal
            ))
            conn.commit()
        return profile

    def delete_user_profile(self, user_id: str) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_profiles WHERE user_id = ?", (user_id,))
            conn.commit()
        return True

class SQLiteReminderRepository(ReminderRepository):
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def create_reminder(self, reminder: Reminder) -> Reminder:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO reminders (reminder_id, user_id, title, frequency, active, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                reminder.reminder_id, reminder.user_id, reminder.title,
                reminder.frequency, 1 if reminder.active else 0, reminder.created_at
            ))
            conn.commit()
        return reminder

    def get_user_reminders(self, user_id: str) -> List[Reminder]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reminders WHERE user_id = ? AND active = 1", (user_id,))
            rows = cursor.fetchall()
            return [
                Reminder(
                    reminder_id=r["reminder_id"],
                    user_id=r["user_id"],
                    title=r["title"],
                    frequency=r["frequency"],
                    active=bool(r["active"]),
                    created_at=r["created_at"]
                ) for r in rows
            ]

    def delete_user_reminders(self, user_id: str) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reminders WHERE user_id = ?", (user_id,))
            conn.commit()
        return True
