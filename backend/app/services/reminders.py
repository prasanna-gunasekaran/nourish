import time
import threading
from typing import List, Dict, Any, Callable
from app.repositories.base import ReminderRepository

class ReminderService:
    """
    Local Reminder Scheduler Service.
    Runs background check for pending proactive agent reminders.
    Prepared for AWS EventBridge / SNS scheduler integration.
    """
    def __init__(self, reminder_repo: ReminderRepository):
        self.reminder_repo = reminder_repo

    def get_active_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        rems = self.reminder_repo.get_user_reminders(user_id)
        return [r.model_dump() for r in rems]

    def trigger_proactive_followup(self, user_id: str = "demo_user") -> str:
        return "Good morning! ☀️ Would you like to log your breakfast today?"
