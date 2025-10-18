import os
import json
import asyncio
import base64
import warnings

from pathlib import Path
from dotenv import load_dotenv

import vertexai
from sqlalchemy import create_engine

# New imports for Firebase Admin
import firebase_admin
from firebase_admin import auth, credentials

# New imports for OpenTelemetry Tracing
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.gcp.trace import GcpSpanExporter
from opentelemetry.resourcedetector.gcp_resource_detector import GcpResourceDetector
from opentelemetry.sdk.resources import Resource

# New imports required for the database connection
from google.adk.sessions import DatabaseSessionService
from google.cloud.sql.connector import Connector
from google.genai.types import (
    Part,
    Content,
    Blob,
)

from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.genai import types
from google.adk.memory import VertexAiMemoryBankService

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from google_search_agent.agent import root_agent

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

#
# ADK Streaming
#

# Load Gemini API Key
load_dotenv()

APP_NAME = "Alora"


# Make sure to import vertexai
import vertexai

def initialize_services():
    """Initializes the services needed for the agent."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION")
    if not all([project_id, location]):
        raise ValueError(
            "Missing one or more required Google Cloud environment variables: "
            "GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION"
        )
    vertexai.init(project=project_id, location=location)

    # --- Tracing Configuration ---
    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create().merge(GcpResourceDetector().detect()))
    )
    tracer_provider = trace.get_tracer_provider()
    tracer_provider.add_span_processor(BatchSpanProcessor(GcpSpanExporter()))

    # Initialize Firebase Admin SDK
    if not firebase_admin._apps:
        firebase_project_id = os.environ.get("FIREBASE_PROJECT_ID", "studio-l13dd")
        firebase_admin.initialize_app(credentials.ApplicationDefault(), {
            'projectId': firebase_project_id,
        })
        print(f"Firebase Admin SDK initialized for project '{firebase_project_id}'.")

    # --- Database Connection Setup ---

    # 1. Get database credentials from environment variables
    db_user = os.environ.get("DB_USER")
    db_pass = os.environ.get("DB_PASS")
    db_name = os.environ.get("DB_NAME")
    instance_connection_name = os.environ.get("INSTANCE_CONNECTION_NAME")

    if not all([db_user, db_pass, db_name, instance_connection_name]):
        raise ValueError(
            "Missing one or more required database environment variables: "
            "DB_USER, DB_PASS, DB_NAME, INSTANCE_CONNECTION_NAME"
        )

    # 2. Initialize the Cloud SQL Connector
    connector = Connector()

    # 3. Define a function to get the database connection
    def getconn():
        conn = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=os.environ.get("DB_IP_TYPE", "public")
        )
        return conn

    # 4. Initialize the DatabaseSessionService
    session_service = DatabaseSessionService(
        db_url="postgresql+pg8000://",
        creator=getconn
    )

    agent_engine_id = os.environ.get("AGENT_ENGINE_ID")
    if not agent_engine_id:
        client = vertexai.Client(project=project_id, location=location)
        agent_engine_config = {
            "context_spec": {
                "memory_bank_config": {
                    "generation_config": {
                        "model": f"projects/{project_id}/locations/{location}/publishers/google/models/gemini-2.5-flash"
                    }
                }
            }
        }
        agent_engine = client.agent_engines.create(config=agent_engine_config)
        agent_engine_id = agent_engine.api_resource.name.split("/")[-1]
        print(f"Created new agent engine: {agent_engine_id}")
        print("Set AGENT_ENGINE_ID in your .env file to reuse it.")

    memory_service = VertexAiMemoryBankService(
        project=project_id,
        location=location,
        agent_engine_id=agent_engine_id,
    )

    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
        memory_service=memory_service,
    )
    return runner

runner = None

async def start_agent_session(user_id, is_audio=False):
    """Starts an agent session"""
    # Create a Session
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
    )

    # Set response modality
    modality = "AUDIO" if is_audio else "TEXT"
    run_config = RunConfig(
        response_modalities=[modality],
        session_resumption=types.SessionResumptionConfig()
    )

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    # Start agent session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue

async def agent_to_client_messaging(websocket, live_events):
    """Agent to client communication"""
    async for event in live_events:

        # If the turn complete or interrupted, send it
        if event.turn_complete or event.interrupted:
            message = {
                "turn_complete": event.turn_complete,
                "interrupted": event.interrupted,
            }
            await websocket.send_text(json.dumps(message))
            print(f"[AGENT TO CLIENT]: {message}")
            continue

        # Read the Content and its first Part
        part: Part = (
            event.content and event.content.parts and event.content.parts[0]
        )
        if not part:
            continue

        # If it's audio, send Base64 encoded audio data
        is_audio = part.inline_data and part.inline_data.mime_type.startswith("audio/pcm")
        if is_audio:
            audio_data = part.inline_data and part.inline_data.data
            if audio_data:
                message = {
                    "mime_type": "audio/pcm",
                    "data": base64.b64encode(audio_data).decode("ascii")
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                continue

        # If it's text and a partial text, send it
        if part.text and event.partial:
            message = {
                "mime_type": "text/plain",
                "data": part.text
            }
            await websocket.send_text(json.dumps(message))
            print(f"[AGENT TO CLIENT]: text/plain: {message}")


async def client_to_agent_messaging(websocket, live_request_queue):
    """Client to agent communication"""
    while True:
        # Decode JSON message
        message_json = await websocket.receive_text()
        message = json.loads(message_json)
        mime_type = message["mime_type"]
        data = message["data"]

        # Send the message to the agent
        if mime_type == "text/plain":
            # Send a text message
            content = Content(role="user", parts=[Part.from_text(text=data)])
            live_request_queue.send_content(content=content)
            print(f"[CLIENT TO AGENT]: {data}")
        elif mime_type == "audio/pcm":
            # Send an audio data
            decoded_data = base64.b64decode(data)
            live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
        else:
            raise ValueError(f"Mime type not supported: {mime_type}")


#
# FastAPI web app
#
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes the agent runner when the app starts."""
    global runner
    if os.environ.get("APP_ENV") != "test":
        runner = initialize_services()
    yield

app = FastAPI(lifespan=lifespan)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """Serves the index.html"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, is_audio: str, token: str = Query(...)):
    """Client websocket endpoint"""

    # Authenticate the user
    try:
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['uid']
        print(f"Client authenticated: {user_id} (session: {session_id})")
    except Exception as e:
        print(f"Authentication failed: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return

    # Wait for client connection
    await websocket.accept()
    print(f"Client connected, audio mode: {is_audio}")

    # Start agent session using the authenticated user's UID
    live_events, live_request_queue = await start_agent_session(user_id, is_audio == "true")

    # Start tasks
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )

    # Wait until the websocket is disconnected or an error occurs
    tasks = [agent_to_client_task, client_to_agent_task]
    try:
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    except WebSocketDisconnect:
        print(f"Client #{user_id} disconnected")
    finally:
        # Close LiveRequestQueue and cancel tasks
        live_request_queue.close()
        agent_to_client_task.cancel()
        client_to_agent_task.cancel()
        print(f"Cleaned up resources for client #{user_id}")
