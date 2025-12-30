import os
import json
import asyncio
import base64
import warnings
from pathlib import Path
from dotenv import load_dotenv

import bleach
import vertexai

# New imports for Firebase Admin
import firebase_admin
from firebase_admin import auth, credentials

# New imports required for the database connection
from database.mongo_db import get_mongo_session_service
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
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from callbacks import log_queue_var

# ... (Previous code)



#from google_search_agent.agent import root_agent

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

# Your ADK agent code follows...
# from google.adk.agents import LlmAgent
# ...
#
# ADK Streaming
#

# Load Gemini API Key
load_dotenv()

# FIX: Unset API keys if running in Vertex AI mode (Project/Location set) to avoid "mutually exclusive" error in Memory Bank
if os.environ.get("GOOGLE_CLOUD_PROJECT"):
    for key in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
        os.environ.pop(key, None)

APP_NAME = "agents"

# --- NEW: Define a global placeholder for the memory service ---
_memory_service = None

# --- NEW: Create a getter function to export the service ---
def get_memory_service():
    """Returns the initialized instance of the memory service."""
    if _memory_service is None:
        raise RuntimeError("Memory service has not been initialized. Ensure initialize_services() is called first.")
    return _memory_service



async def initialize_services():
    """Initializes the services needed for the agent."""
    global _memory_service # NEW: Declare that we are modifying the global variable
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "gem-creator")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    if not all([project_id, location]):
        raise ValueError(
            "Missing one or more required Google Cloud environment variables: "
            "GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION"
        )
    vertexai.init(project=project_id, location=location)

    # Initialize Firebase Admin SDK
    if not firebase_admin._apps:
        # Use explicit env var, fallback to GCP project, or Error
        firebase_project_id = os.environ.get("FIREBASE_PROJECT_ID") or os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not firebase_project_id:
             # Fallback for local dev if not set (optional, or raise error)
             logging.warning("FIREBASE_PROJECT_ID not set, defaulting to 'milky-way' (User Requested) but this may fail if credentials mismatch.")
             firebase_project_id = "milky-way"
        
        logging.info(f"Initializing Firebase Admin SDK for project '{firebase_project_id}'...")
        firebase_admin.initialize_app(credentials.ApplicationDefault(), {
            'projectId': firebase_project_id,
        })
        logging.info(f"Firebase Admin SDK initialized.")

    # --- Database Connection Setup ---
    storage_type = os.environ.get("SESSION_STORAGE", "mongo")
    print(f"Initializing session storage: {storage_type}")

    if storage_type == "local-postgres":
        from database.local_postgres import get_local_postgres_session_service
        # Note: Local Postgres initialization is synchronous
        session_service = get_local_postgres_session_service()
    elif storage_type == "memory":
        print("Using InMemorySessionService (Non-persistent)")
        from google.adk.sessions import BaseSessionService, Session
        class InMemorySessionService(BaseSessionService):
            def __init__(self): self.sessions = {}
            async def create_session(self, app_name, user_id, **kwargs):
                s_id = str(kwargs.get("id", f"session-{len(self.sessions)}"))
                session = Session(id=s_id, app_name=app_name, user_id=user_id, events=[], state={})
                self.sessions[s_id] = session
                return session
            async def get_session(self, session_id, **kwargs): return self.sessions.get(session_id)
            async def update_session(self, session, **kwargs): self.sessions[session.id] = session
            async def append_event(self, session, event, **kwargs): session.events.append(event); await self.update_session(session)
            async def delete_session(self, session_id, **kwargs): self.sessions.pop(session_id, None)
            async def list_sessions(self, **kwargs): return list(self.sessions.values())
        session_service = InMemorySessionService()
    else:
        # Default to MongoDB (Legacy)
        session_service = await get_mongo_session_service()

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

    _memory_service = VertexAiMemoryBankService(
        project=project_id,
        location=location,
        agent_engine_id=agent_engine_id,
    )

    # --- LATE IMPORT ---
    # We import root_agent here, after _memory_service has been initialized.
    # This ensures that when agent.py is loaded, it can successfully call get_memory_service().
    from google_search_agent.agent import create_root_agent
    root_agent = create_root_agent(memory_service=_memory_service, use_mcp_tools=False)
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
        memory_service=_memory_service,
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
            # Sanitize user input to prevent XSS vulnerabilities
            sanitized_data = bleach.clean(data)
            # Send a text message
            content = Content(role="user", parts=[Part.from_text(text=sanitized_data)])
            live_request_queue.send_content(content=content)
            print(f"[CLIENT TO AGENT]: {sanitized_data}")
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
    logging.info("Entering lifespan...")
    if os.environ.get("APP_ENV") != "test":
        logging.info("Calling initialize_services...")
        try:
            runner = await initialize_services()
            logging.info("initialize_services completed.")
        except Exception:
            logging.error("initialize_services failed", exc_info=True)
            raise
    yield

app = FastAPI(lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "https://vigilant-journey--gem-creator.us-central1.hosted.app",
        "https://gem-creator.web.app",
        "https://gem-creator.firebaseapp.com",
    ], # explicit origins required for credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# --- REST API Request Models ---
from pydantic import BaseModel
from typing import Optional, List

class AnalyzeRequest(BaseModel):
    query: str
    image: Optional[str] = None  # Base64 encoded image
    mime_type: Optional[str] = None # e.g., "image/png"

class AnalyzeResponse(BaseModel):
    text: str # The main analysis text
    # We could add more fields later like tools used, etc.



# ... (Previous code)

@app.post("/analyze")
async def analyze_endpoint(request: AnalyzeRequest):
    """
    Stateless analysis endpoint (STREAMING).
    Streams NDJSON:
    - {"log": "Status update..."}
    - {"result": {"text": "Final Analysis"}}
    """
    if not runner:
        raise HTTPException(status_code=503, detail="Agent runner not initialized")

    # 1. Create a temporary session
    session_id = f"temp-analysis-{os.urandom(4).hex()}"
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id="anonymous_web_user",
        id=session_id
    )

    parts = [Part.from_text(text=request.query)]
    if request.image and request.mime_type:
        try:
            image_data = base64.b64decode(request.image)
            parts.append(Part(inline_data=Blob(data=image_data, mime_type=request.mime_type)))
        except Exception as e:
             raise HTTPException(status_code=400, detail=f"Invalid base64 image: {str(e)}")
    
    content = Content(role="user", parts=parts)
    run_config = RunConfig(
        response_modalities=["TEXT"],
        session_resumption=types.SessionResumptionConfig()
    )

    # Setup Queues
    log_queue = asyncio.Queue()
    # token = log_queue_var.set(log_queue) # REMOVED from here

    async def event_generator():
        token = log_queue_var.set(log_queue) # ADDED here (inside generator context)
        try:
            # --- ROBUST IMPLEMENTATION ---
            # We spawn a producer task that pushes (Type, Data) to the queue.
            # Main loop yields from queue.
            
            output_queue = asyncio.Queue()
            
            async def agent_producer():
                try:
                    async for event in runner.run_async(
                            session_id=session_id,
                            user_id="anonymous_web_user",
                            new_message=content,
                            run_config=run_config
                    ):
                        if event.content and event.content.parts:
                            for part in event.content.parts:
                                if part.text:
                                    output_queue.put_nowait(("TEXT", part.text))
                except Exception as e:
                    output_queue.put_nowait(("ERROR", str(e)))
                finally:
                    output_queue.put_nowait(("DONE", None))

            producer = asyncio.create_task(agent_producer())
            final_text = ""
            
            try:
                while True:
                    # 1. Drain pending logs immediately
                    while not log_queue.empty():
                        msg = log_queue.get_nowait()
                        yield json.dumps(msg) + "\n"

                    # 2. Wait for Next Event (Log or Token)
                    log_task = asyncio.create_task(log_queue.get())
                    out_task = asyncio.create_task(output_queue.get())
                    
                    done, pending = await asyncio.wait(
                        [log_task, out_task], 
                        return_when=asyncio.FIRST_COMPLETED
                    )

                    for task in done:
                        if task == log_task:
                            # Got a log
                            msg = task.result()
                            yield json.dumps(msg) + "\n"
                            out_task.cancel() # Cancel wait on output
                        elif task == out_task:
                            # Got output
                            type_, val = task.result()
                            log_task.cancel() # Cancel wait on log

                            if type_ == "TEXT":
                                final_text += val
                            elif type_ == "ERROR":
                                yield json.dumps({"log": f"❌ Error: {val}"}) + "\n"
                            elif type_ == "DONE":
                                # Final Result
                                yield json.dumps({"result": {"text": final_text}}) + "\n"
                                return

            except Exception as e:
                yield json.dumps({"log": f"❌ Stream Error: {e}"}) + "\n"
            finally:
                # Cleanup producer if it's still running
                try:
                    producer.cancel()
                except Exception:
                    pass

        finally:
            try:
                log_queue_var.reset(token)
            except Exception as e:
                print(f"Warning: Failed to reset log_queue_var: {e}")
            # await runner.session_service.delete_session(session_id)

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")


@app.get("/")
async def root():
    """Serves the index.html"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, is_audio: str):
    """Client websocket endpoint"""

    # Extract token from WebSocket subprotocol header
    # The client sends ["Bearer", token] as subprotocols
    subprotocols = websocket.headers.get("sec-websocket-protocol", "")
    token = None
    if subprotocols:
        # Parse subprotocols: "Bearer, <token>"
        parts = subprotocols.split(',', 1)
        if len(parts) == 2 and parts[0].strip() == 'Bearer':
            token = parts[1].strip()
    
    if not token:
        print("Authentication failed: No token provided in WebSocket subprotocol")
        await websocket.close(code=1008, reason="Authentication failed")
        return

    # Authenticate the user
    try:
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['uid']
        print(f"Client authenticated: {user_id} (session: {session_id})")
    except Exception as e:
        print(f"Authentication failed: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return

    # Wait for client connection - accept with the Bearer subprotocol
    await websocket.accept(subprotocol="Bearer")
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
