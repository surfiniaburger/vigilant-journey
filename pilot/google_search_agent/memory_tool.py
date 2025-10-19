import logging
from typing import List
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import FunctionTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_memory(tool_context: ToolContext, fact: str, topics: List[str]) -> dict:
    """
    Saves a specific fact to the user's long-term memory in the specified topics.

    Args:
        fact: The specific piece of information to remember.
        topics: A list of topics to categorize the memory under (e.g., ['user_preferences']).
    """
    try:
        logger.info(f"Attempting to save fact to memory: '{fact}' under topics: {topics}")
        tool_context.memory_service.add_memory(
            user_id=tool_context.session.user_id,
            session_id=tool_context.session.id,
            app_name=tool_context.session.app_name,
            content=fact,
            topics=topics,
        )
        response = {"status": "success", "message": f"Successfully remembered: {fact}"}
        logger.info(response)
        return response
    except Exception as e:
        error_message = f"Failed to save memory: {e}"
        logger.error(error_message)
        return {"status": "error", "message": error_message}

def recall_memory(tool_context: ToolContext, query: str) -> dict:
    """
    Recalls information from the user's long-term memory based on a query.

    Args:
        query: The question to ask the memory bank.
    """
    try:
        logger.info(f"Attempting to recall memory for query: '{query}'")
        search_results = tool_context.memory_service.search_memory(
            user_id=tool_context.session.user_id,
            session_id=tool_context.session.id,
            app_name=tool_context.session.app_name,
            query=query,
        )
        
        if not search_results:
            response = {"status": "success", "memories": "No relevant memories found."}
            logger.info(response)
            return response

        formatted_memories = "\n".join([f"- {result.content}" for result in search_results])
        response = {"status": "success", "memories": formatted_memories}
        logger.info(f"Found memories: {formatted_memories}")
        return response
    except Exception as e:
        error_message = f"Failed to recall memory: {e}"
        logger.error(error_message)
        return {"status": "error", "message": error_message}

save_memory_tool = FunctionTool(func=save_memory)

recall_memory_tool = FunctionTool(func=recall_memory)
