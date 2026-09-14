import pytest
from app.repositories.sqlite_repo import SQLiteDatabase, SQLiteMealRepository, SQLiteUserRepository, SQLiteReminderRepository
from app.nutrition.service import NutritionService
from app.providers.mock_provider import LocalModelProvider
from app.tools.agent_tools import AgentTools
from app.agent.core import AgentCore

def test_full_agent_demo_flow(tmp_path):
    db_file = str(tmp_path / "demo_flow.db")
    db = SQLiteDatabase(db_file)
    meal_repo = SQLiteMealRepository(db)
    user_repo = SQLiteUserRepository(db)
    reminder_repo = SQLiteReminderRepository(db)

    nutrition_service = NutritionService()
    provider = LocalModelProvider()
    tools = AgentTools(nutrition_service, meal_repo, user_repo, reminder_repo)
    agent = AgentCore(provider, tools)

    user_id = "test_user_demo"

    # STEP 1: Log Breakfast
    resp1 = agent.process_message("I ate 3 idlis, one vada and 2 eggs for breakfast.", user_id)
    assert "~464" in resp1.reply_text or "464" in resp1.reply_text
    assert resp1.meal_logged is not None
    assert any(t.tool_name == "save_meal" for t in resp1.action_traces)

    # STEP 2: Log Lunch
    resp2 = agent.process_message("For lunch I had chicken biryani and a glass of buttermilk.", user_id)
    assert "biryani" in resp2.reply_text.lower()
    assert resp2.meal_logged is not None

    # STEP 3: Daily Summary Query
    resp3 = agent.process_message("What have I eaten today?", user_id)
    assert "Today's Food Summary" in resp3.reply_text
    assert "Breakfast" in resp3.reply_text
    assert "Lunch" in resp3.reply_text
    assert any(t.tool_name == "get_daily_summary" for t in resp3.action_traces)

    # STEP 4: Dinner Recommendation
    resp4 = agent.process_message("What should I eat for dinner?", user_id)
    assert "recommended for dinner" in resp4.reply_text.lower() or "suggest" in resp4.reply_text.lower()
    assert "avoid" in resp4.reply_text.lower()
    assert any(t.tool_name == "recommend_meal" for t in resp4.action_traces)

    # STEP 5: Update Preference (Dislike Eggs)
    resp5 = agent.process_message("I don't like eggs.", user_id)
    assert "eggs" in resp5.reply_text.lower()
    profile = user_repo.get_user_profile(user_id)
    assert "eggs" in profile.disliked_foods

    # STEP 6: Adaptive Recommendation (No Eggs)
    resp6 = agent.process_message("Suggest dinner again.", user_id)
    assert "eggs" not in resp6.reply_text.lower() or "dislike eggs" in resp6.reply_text.lower()

    # STEP 7: Create Reminder
    resp7 = agent.process_message("Remind me to log breakfast every morning.", user_id)
    assert "reminder" in resp7.reply_text.lower()
    rems = reminder_repo.get_user_reminders(user_id)
    assert len(rems) == 1
