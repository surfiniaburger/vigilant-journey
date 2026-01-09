import logging
from typing import Annotated
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

async def get_recent_audio_context(
    ctx: ToolContext,
    limit: Annotated[int, "Number of recent interactions to retrieve"] = 5
) -> str:
    """
    Retrieves the most recent transcripts of user verbal commands from the session history.
    Use this to 'remember' what the user just said if you need to cross-reference it with telemetry or vision.
    """
    try:
        # Access session history directly from the tool context
        events = ctx.invocation_context.session.events
        
        # Filter for user messages that contain text
        user_transcripts = []
        for event in reversed(events):
            if event.author == "user" and event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        user_transcripts.append(part.text)
                        if len(user_transcripts) >= limit:
                            break
            if len(user_transcripts) >= limit:
                break
        
        if not user_transcripts:
            return "No recent audio or text context found in session history."
        
        # Format as a chronological list
        transcript_history = "\n".join([f"- {t}" for t in reversed(user_transcripts)])
        return f"Recent user interactions (transcripts):\n{transcript_history}"
        
    except Exception as e:
        logger.error(f"Error retrieving audio context: {e}")
        return f"Error: Could not retrieve audio context. {str(e)}"

# Alias for easy tool registration
audio_context_tool = get_recent_audio_context
