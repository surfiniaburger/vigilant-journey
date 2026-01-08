import pytest
from unittest.mock import MagicMock, patch
import os

# We need to mock the environment variable BEFORE importing AudioService
# because it initializes clients in __init__
@patch.dict(os.environ, {"ELEVENLABS_API_KEY": "fake-key", "AUDIO_BUCKET_NAME": "test-bucket"})
@patch("services.audio_service.ElevenLabs")
@patch("services.audio_service.storage.Client")
def test_audio_service_generate_and_upload(mock_storage_client, mock_elevenlabs):
    # 1. Setup Mocks
    mock_eleven_instance = mock_elevenlabs.return_value
    # Mock text_to_speech.convert returning a generator
    mock_eleven_instance.text_to_speech.convert.return_value = (b"chunk1", b"chunk2")
    
    mock_storage_instance = mock_storage_client.return_value
    mock_bucket = MagicMock()
    mock_storage_instance.bucket.return_value = mock_bucket
    # Assume bucket exists for simple path
    mock_bucket.exists.return_value = True
    
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_blob.public_url = "https://storage.googleapis.com/test-bucket/audio.mp3"
    
    # 2. Import Service (after patches are active)
    from services.audio_service import AudioService
    service = AudioService()
    
    # 3. Act
    url = service.generate_and_upload(text="Hello world", voice_id="test-voice")
    
    # 4. Assert
    assert url == "https://storage.googleapis.com/test-bucket/audio.mp3"
    
    # Check ElevenLabs call
    mock_eleven_instance.text_to_speech.convert.assert_called_once_with(
        text="Hello world",
        voice_id="test-voice",
        model_id="eleven_turbo_v2_5"
    )
    
    # Check GCS Upload
    # The data should be joined
    mock_blob.upload_from_string.assert_called_once_with(b"chunk1chunk2", content_type="audio/mpeg")
    mock_blob.make_public.assert_called_once()

@patch.dict(os.environ, {"ELEVENLABS_API_KEY": "fake-key", "AUDIO_BUCKET_NAME": "test-bucket"})
@patch("services.audio_service.ElevenLabs")
@patch("services.audio_service.storage.Client")
def test_audio_service_bucket_creation(mock_storage_client, mock_elevenlabs):
    # Test bucket creation logic if it doesn't exist
    mock_storage_instance = mock_storage_client.return_value
    mock_bucket = MagicMock()
    # First call to bucket() returns the object, but we need to mock exists() on it
    mock_storage_instance.bucket.return_value = mock_bucket
    mock_bucket.exists.return_value = False
    
    # create_bucket returns the NEW bucket object
    mock_new_bucket = MagicMock()
    mock_storage_instance.create_bucket.return_value = mock_new_bucket
    
    mock_blob = MagicMock()
    mock_new_bucket.blob.return_value = mock_blob
    mock_blob.public_url = "http://new-bucket/audio.mp3"

    mock_eleven_instance = mock_elevenlabs.return_value
    mock_eleven_instance.text_to_speech.convert.return_value = (b"data",)

    from services.audio_service import AudioService
    service = AudioService()
    
    service.generate_and_upload("text")
    
    # Verify create_bucket was called
    mock_storage_instance.create_bucket.assert_called_with("test-bucket", location="US")
    # Verify policy update
    mock_new_bucket.set_iam_policy.assert_called()
