from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class ModelProvider(ABC):
    @abstractmethod
    def parse_intent_and_entities(self, user_message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses user message into intent (log_meal, get_summary, recommend_meal, update_preference, create_reminder, ask_advice)
        and extracted parameters.
        """
        pass

    @abstractmethod
    def generate_response(
        self,
        intent: str,
        user_message: str,
        tool_results: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> str:
        """
        Synthesizes a helpful, natural language response based on tool execution results.
        """
        pass
