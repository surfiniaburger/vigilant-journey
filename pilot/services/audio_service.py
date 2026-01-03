import os
import uuid
import logging
from elevenlabs.client import ElevenLabs
from google.cloud import storage

logger = logging.getLogger(__name__)

class AudioService:
    def __init__(self):
        raw_key = os.environ.get("ELEVENLABS_API_KEY", "")
        self.bucket_name = os.environ.get("AUDIO_BUCKET_NAME", "vigilant-journey-assets")
        # Robust Sanitization: Strip whitespace, newlines, and potential quotes
        self.api_key = raw_key.strip().strip("\"'")

        # Remove common copy-paste artifacts if present
        if self.api_key.startswith("ELEVENLABS_API_KEY="):
            self.api_key = self.api_key.split("=", 1)[1].strip()

        if self.api_key:
            try:
                self.client = ElevenLabs(api_key=self.api_key)
            except Exception as e:
                 logger.error(f"Failed to init ElevenLabs client: {e}")
        else:
            logger.warning("ELEVENLABS_API_KEY not set or empty.")

        try:
            self.storage_client = storage.Client()
        except Exception as e:
             logger.warning(f"Failed to init GCS client: {e}")

    def generate_and_upload(self, text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb") -> str:
        """
        Generates speech, uploads to GCS, returns public URL.
        Default Voice: George (British, Scientific)
        """
        if not self.client or not self.storage_client:
            raise RuntimeError("AudioService dependencies not ready.")

        # 1. Generate
        # Use stream=False to get full bytes (or iterate generator)
        # Use text_to_speech.convert instead of generate
        response = self.client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_turbo_v2_5"
        )
        
        # Responses from .generate can be a generator. Collect it.
        audio_data = b"".join(response)

        # 2. Upload
        filename = f"audio_assets/{uuid.uuid4()}.mp3"
        bucket = self.storage_client.bucket(self.bucket_name)
        if not bucket.exists():
            try:
                bucket = self.storage_client.create_bucket(self.bucket_name, location="US")
                # Make bucket public
                policy = bucket.get_iam_policy(requested_policy_version=3)
                policy.bindings.append(
                    {"role": "roles/storage.objectViewer", "members": ["allUsers"]}
                )
                bucket.set_iam_policy(policy)
                logger.info(f"Created public bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to create bucket {self.bucket_name}: {e}")
                raise

        blob = bucket.blob(filename)
        
        blob.upload_from_string(audio_data, content_type="audio/mpeg")
        
        # 3. Make Public (try/catch)
        try:
            blob.make_public()
        except Exception as e:
            logger.warning(f"Could not make blob public (check bucket permissions): {e}")

        return blob.public_url

audio_service = AudioService()
