
import os
from google import genai
from google.genai.types import GenerateContentConfig
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def run_url_context_test():
    """
    Tests the Gemini URL context tool by summarizing a sample URL.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Please set the GEMINI_API_KEY environment variable in your .env file.")
        return

    try:

        client = genai.Client()
        model_id = "gemini-2.5-flash"

        tools = [
            {"url_context": {}},
        ]

        # Using one of the Toyota URLs from context.md for the test
        test_url = "https://www.toyota.com/owners/warranty-owners-manuals/digital/article/bz4x/2024/om42e95u/ch02se010401"

        prompt = f"Summarize the main topic of the content at the following URL: {test_url}"

        print(f"--- Sending prompt to {model_id} ---")
        print(f"Prompt: {prompt}")

        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=GenerateContentConfig(
                tools=tools,
            )
        )

        print("\n--- Model Response ---")
        for part in response.candidates[0].content.parts:
            print(part.text)

        print("\n--- Verification Metadata ---")
        print(response.candidates[0].url_context_metadata)

    except Exception as e:
        print(f"\n--- An error occurred ---")
        print(e)

if __name__ == "__main__":
    run_url_context_test()
