# /Users/surfiniaburger/Desktop/app/security.py
import logging
import os
from functools import lru_cache
from typing import Dict, Any, Optional

from google.api_core.exceptions import GoogleAPICallError
from google.cloud import modelarmor_v1

logger = logging.getLogger(__name__)

# --- Model Armor Configuration ---
MODEL_ARMOR_PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
MODEL_ARMOR_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
MODEL_ARMOR_TEMPLATE_ID = "alora-ma-template" # As per the user's example

@lru_cache(maxsize=1)
def get_model_armor_client() -> Optional[modelarmor_v1.ModelArmorAsyncClient]:
    """
    Initializes and returns a singleton ModelArmorAsyncClient instance.
    Caches the client to avoid re-initialization on every call.
    """
    try:
        logging.info("Initializing ModelArmorAsyncClient...")
        # The endpoint needs to be specified for the REST transport
        client_options = {"api_endpoint": f"modelarmor.{MODEL_ARMOR_LOCATION}.rep.googleapis.com"}
        # Use AsyncClient. Transport 'rest' might not be available for Async, defaults to grpc-async usually.
        # But let's try allowing default transport or specify 'grpc_async' if needed. 
        # Safest is to let library decide or stick to rest if supported, but typically async prefers grpc.
        # However, for Cloud Run/REST compatibility, let's try leaving transport auto-negotiated or 'rest' if known valid.
        # The 'google-cloud-modelarmor' 0.3.0 might have specific support. 
        # Let's trust the default for async client.
        client = modelarmor_v1.ModelArmorAsyncClient(client_options=client_options) 
        logging.info("ModelArmorAsyncClient initialized successfully.")
        return client
    except Exception as e:
        logging.error(f"Failed to initialize ModelArmorAsyncClient: {e}", exc_info=True)
        return None

async def sanitize_prompt_with_model_armor(prompt: str) -> Dict[str, Any]:
    """
    Uses Google Cloud Model Armor to check a prompt for safety violations.
    Async version.
    """
    client = get_model_armor_client()
    if not client:
        logging.error("Model Armor client is not available. Failing closed for security.")
        return {"is_safe": False, "reason": "Client unavailable"}

    try:
        user_prompt_data = modelarmor_v1.DataItem(text=prompt)
        template_path = f"projects/{MODEL_ARMOR_PROJECT_ID}/locations/{MODEL_ARMOR_LOCATION}/templates/{MODEL_ARMOR_TEMPLATE_ID}"
        request = modelarmor_v1.SanitizeUserPromptRequest(name=template_path, user_prompt_data=user_prompt_data)
        
        # Await the async call
        response = await client.sanitize_user_prompt(request=request)

        # Iterate through all configured filters (PI/Jailbreak, Malicious URI, RAI, SDP, etc.)
        for filter_key, filter_result in response.sanitization_result.filter_results.items():
            # Check specific sub-result match_state using key-based lookup (e.g. pi_and_jailbreak -> pi_and_jailbreak_filter_result)
            # This handles the nested structure seen in previous revisions.
            sub_field_name = f"{filter_key}_filter_result"
            match_state = modelarmor_v1.FilterMatchState.NO_MATCH_FOUND # Default
            
            if hasattr(filter_result, sub_field_name):
                 match_state = getattr(filter_result, sub_field_name).match_state
            elif hasattr(filter_result, "match_state"):
                 # Fallback for simple filters or if structure simplifies
                 match_state = filter_result.match_state
            
            if match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
                logging.warning(f"Model Armor Security Violation: {filter_key} triggered.")
                return {"is_safe": False, "reason": f"{filter_key} detected"}

        return {"is_safe": True, "reason": "Passed security check"}
    except GoogleAPICallError as e:
        logging.error(f"Model Armor API call failed: {e}", exc_info=True)
        # Fail closed is safer.
        return {"is_safe": False, "reason": f"API Error: {e}"}
    except Exception as e:
        logging.error(f"An unexpected error occurred during prompt sanitization: {e}", exc_info=True)
        return {"is_safe": False, "reason": f"Unexpected Error: {e}"}