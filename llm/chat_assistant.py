import json
import logging
from database.db_manager import DBManager
from llm.openai_client import OpenAIClient
from llm.prompts import CHAT_SYSTEM_PROMPT, WBR_SYSTEM_PROMPT, WBR_USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

class ChatAssistant:
    """
    Orchestrates context injection and chat execution for the AI Chat Assistant
    and AI Weekly Business Review (WBR) Generator.
    """
    def __init__(self, db_manager: DBManager, openai_client: OpenAIClient):
        self.db = db_manager
        self.llm = openai_client

    def _get_serialized_database_state(self) -> str:
        """Queries all core tables and converts them to a structured JSON string."""
        tables = ['revenue', 'employees', 'partners', 'projects', 'clients', 'api_metrics']
        db_state = {}
        
        for table in tables:
            try:
                df = self.db.get_table_dataframe(table)
                # Convert DataFrame to dictionary records
                db_state[table] = df.to_dict(orient='records')
            except Exception as e:
                logger.error(f"Failed to serialize table {table}: {e}")
                db_state[table] = []
                
        return json.dumps(db_state, indent=2)

    def ask_assistant(self, question: str) -> str:
        """
        Fetches database context, builds prompt, and queries LLM.
        """
        db_context = self._get_serialized_database_state()
        system_prompt = CHAT_SYSTEM_PROMPT.format(database_snapshot=db_context)
        
        # Call LLM completion
        response = self.llm.generate_completion(
            system_prompt=system_prompt,
            user_prompt=question
        )
        return response

    def generate_wbr(self, author_name: str) -> str:
        """
        Generates a fresh Weekly Business Review using OpenAI.
        Saves the generated report history in the database.
        """
        db_context = self._get_serialized_database_state()
        system_prompt = WBR_SYSTEM_PROMPT
        user_prompt = WBR_USER_PROMPT_TEMPLATE.format(database_json=db_context)
        
        # Call LLM completion
        response = self.llm.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        # Save generated report to SQLite database
        try:
            self.db.save_wbr_report(response, author_name)
        except Exception as e:
            logger.error(f"Failed to archive WBR report: {e}")
            
        return response
