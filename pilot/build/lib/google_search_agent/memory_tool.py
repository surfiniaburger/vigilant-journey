import logging
from typing import List

from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content, Part

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_memory_tools(memory_service):
    """
    Factory function to create memory tool instances that are aware of the memory service.
    """

    async def save_memory(tool_context: ToolContext, fact: str) -> dict:
        """
        Saves a specific, self-contained fact to the user's long-term memory.

        Args:
            fact: The specific piece of information to remember.
        """
        try:
            logger.info(f"Attempting to save fact to memory: '{fact}'")
            
            # SOLUTION: Use the add_session_to_memory method as intended by the ADK.
            # We will temporarily add the new fact to the session's event history
            # so the memory service can process it.
            
            # Get the current session
            session = tool_context.session
            
            # Create a temporary user event with the fact to be saved
            fact_event = {
                "content": Content(role="user", parts=[Part(text=fact)])._pb
            }
            
            # Append the temporary event to the session's history
            session.events.append(fact_event)

            # Now, call the memory service with the updated session.
            # The ADK will handle sending the new information to the Memory Bank.
            await memory_service.add_session_to_memory(session)
            
            # Optional: Remove the temporary event if you don't want it in the
            # main conversation history for the next turn.
            session.events.pop()

            response = {"status": "success", "message": f"Successfully triggered memory save for: {fact}"}
            logger.info(response)
            return response
        except Exception as e:
            error_message = f"Failed to save memory: {e}"
            logger.error(error_message, exc_info=True)
            return {"status": "error", "message": error_message}

    async def recall_memory(tool_context: ToolContext, query: str) -> dict:
        """
        Recalls relevant information from the user's long-term memory.

        Args:
            query: The question to ask the memory bank.
        """
        try:
            logger.info(f"Attempting to recall memory for query: '{query}'")
            
            search_results = await memory_service.search_memory(
                app_name=tool_context.session.app_name,
                user_id=tool_context.session.user_id,
                query=query,
            )

            if not search_results or not search_results.memories:
                response = {"status": "success", "memories": "No relevant memories found."}
                logger.info(response)
                return response

            formatted_memories = "\n".join([f"- {entry.content.parts[0].text}" for entry in search_results.memories])
            response = {"status": "success", "memories": formatted_memories}
            logger.info(f"Found memories: {formatted_memories}")
            return response
        except Exception as e:
            error_message = f"Failed to recall memory: {e}"
            logger.error(error_message, exc_info=True)
            return {"status": "error", "message": error_message}

    save_memory_tool = FunctionTool(
        func=save_memory,
 
    )
    
    recall_memory_tool = FunctionTool(
        func=recall_memory,

    )

    return save_memory_tool, recall_memory_tool