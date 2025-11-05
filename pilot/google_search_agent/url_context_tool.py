
import os
from google import genai
from google.genai.types import GenerateContentConfig
from google.adk.tools import FunctionTool

def get_info_from_url(url: str, query: str) -> dict:
    """
    Uses Gemini to get information from the content of a given URL based on a query.

    Args:
        url: The URL of the page to get information from.
        query: The query or question to ask about the URL's content.

    Returns:
        A dictionary containing the answer or an error message.
    """
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        # The client will fail, but let's provide a clearer error.
        return {"error": "GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set."}

    try:
        client = genai.Client()
        model_id = "gemini-2.5-flash"

        tools = [
            {"url_context": {}},
        ]

        prompt = f"{query} from the following URL: {url}"

        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=GenerateContentConfig(
                tools=tools,
            )
        )

        answer = "".join([part.text for part in response.candidates[0].content.parts])
        return {"answer": answer}

    except Exception as e:
        return {"error": str(e)}

url_context_tool = FunctionTool(
    func=get_info_from_url,
)
