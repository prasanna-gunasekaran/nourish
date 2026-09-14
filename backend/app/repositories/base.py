from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.schemas import LoggedMeal, UserProfile, Reminder

class MealRepository(ABC):
    @abstractmethod
    def save_meal(self, meal: LoggedMeal) -> LoggedMeal:
        pass

    @abstractmethod
    def update_meal(self, meal: LoggedMeal) -> LoggedMeal:
        pass

    @abstractmethod
    def get_meal_by_id(self, meal_id: str) -> Optional[LoggedMeal]:
        pass

    @abstractmethod
    def get_user_meals(self, user_id: str, date_str: Optional[str] = None) -> List[LoggedMeal]:
        pass

    @abstractmethod
    def get_user_meals_range(self, user_id: str, start_date: str, end_date: str) -> List[LoggedMeal]:
        pass

    @abstractmethod
    def delete_user_meals(self, user_id: str) -> bool:
        pass

class UserRepository(ABC):
    @abstractmethod
    def get_user_profile(self, user_id: str) -> UserProfile:
        pass

    @abstractmethod
    def update_user_profile(self, profile: UserProfile) -> UserProfile:
        pass

    @abstractmethod
    def delete_user_profile(self, user_id: str) -> bool:
        pass

class ReminderRepository(ABC):
    @abstractmethod
    def create_reminder(self, reminder: Reminder) -> Reminder:
        pass

    @abstractmethod
    def get_user_reminders(self, user_id: str) -> List[Reminder]:
        pass

    @abstractmethod
    def delete_user_reminders(self, user_id: str) -> bool:
        pass
