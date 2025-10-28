import asyncio
import json
import os
from dotenv import load_dotenv
import vertexai

# Temporarily add the parent directory to the path to allow direct imports
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google_search_agent.agent import create_root_agent
from google.adk.memory import VertexAiMemoryBankService
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig
from google.genai.types import Content, Part
from google.adk.sessions import BaseSessionService, Session
from google.adk.agents import BaseAgent
from sentence_transformers import SentenceTransformer, util

# --- CONFIGURATION ---
EVALUATION_DATASET_PATH = "pilot/evaluation/evaluation_dataset.json"
SIMILARITY_THRESHOLD = 0.75

# --- INITIALIZATION ---
async def initialize_evaluation_services():
    """Initializes the services required for the evaluation script."""
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION")
    if not all([project_id, location]):
        raise ValueError("Missing GOOGLE_CLOUD_PROJECT or GOOGLE_CLOUD_LOCATION")
    vertexai.init(project=project_id, location=location)

    agent_engine_id = os.environ.get("AGENT_ENGINE_ID")
    if not agent_engine_id:
        raise ValueError("Missing AGENT_ENGINE_ID")

    memory_service = VertexAiMemoryBankService(
        project=project_id,
        location=location,
        agent_engine_id=agent_engine_id,
    )

    # Use a mock session service for evaluation
    class MockSessionService(BaseSessionService):
        def __init__(self):
            self.sessions = {}

        async def create_session(self, app_name, user_id, **kwargs):
            session_id = f"eval-session-{len(self.sessions)}"
            session = Session(id=session_id, app_name=app_name, user_id=user_id, events=[], state={})
            self.sessions[session_id] = session
            return session

        async def get_session(self, session_id, app_name, user_id, **kwargs):
            return self.sessions.get(session_id)

        async def update_session(self, session: Session, **kwargs):
            self.sessions[session.id] = session

        async def append_event(self, session: Session, event, **kwargs):
            session.events.append(event)
            await self.update_session(session)

        async def delete_session(self, session_id, app_name, user_id, **kwargs):
            if session_id in self.sessions:
                del self.sessions[session_id]

        async def list_sessions(self, app_name, user_id, **kwargs):
            return list(self.sessions.values())

    agent = create_root_agent(memory_service, use_mcp_tools=False)
    runner = Runner(
        app_name="EvaluationRunner",
        agent=agent,
        session_service=MockSessionService(),
        memory_service=memory_service,
    )
    return runner

# --- EVALUATION LOGIC ---
async def run_single_evaluation(runner, user_query):
    """Runs a single evaluation case and returns the final answer."""
    session = await runner.session_service.create_session(
        app_name="EvaluationApp",
        user_id="evaluation_user"
    )
    session_id = session.id
    run_config = RunConfig(response_modalities=["TEXT"])

    initial_content = Content(parts=[Part(text=user_query)])

    final_answer = None
    async for event in runner.run_async(session_id=session_id, user_id="evaluation_user", new_message=initial_content, run_config=run_config):
        if event.turn_complete and event.content:
            final_answer_part = event.content.parts[0]
            if final_answer_part.text:
                final_answer = final_answer_part.text
                break # Stop after the first complete turn with a text answer
    return final_answer

async def main():
    """Main function to run the benchmark evaluation."""
    print("Initializing services for evaluation...")
    runner = await initialize_evaluation_services()

    print(f"Loading evaluation dataset from {EVALUATION_DATASET_PATH}...")
    with open(EVALUATION_DATASET_PATH, 'r') as f:
        eval_data = json.load(f)

    print("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    results = []
    for case in eval_data["eval_cases"]:
        print(f"--- Running Evaluation Case: {case['eval_id']} ---")
        print(f"User Query: {case['user_query']}")

        generated_answer = await run_single_evaluation(runner, case['user_query'])

        print(f"Generated Answer: {generated_answer}")
        print(f"Reference Answer: {case['reference_answer']}")

        # Calculate similarity score
        if generated_answer:
            embedding1 = model.encode(generated_answer, convert_to_tensor=True)
            embedding2 = model.encode(case['reference_answer'], convert_to_tensor=True)
            similarity_score = util.pytorch_cos_sim(embedding1, embedding2).item()
            is_correct = similarity_score >= SIMILARITY_THRESHOLD
        else:
            similarity_score = 0.0
            is_correct = False

        print(f"Similarity Score: {similarity_score:.4f}")
        print(f"Correct: {is_correct}")

        results.append({
            "eval_id": case['eval_id'],
            "user_query": case['user_query'],
            "generated_answer": generated_answer,
            "reference_answer": case['reference_answer'],
            "similarity_score": similarity_score,
            "is_correct": is_correct
        })
        print("--------------------------------------------------")

    # --- REPORTING ---
    print("\n--- BENCHMARK RESULTS ---")
    # Add more detailed reporting here in the future
    print(json.dumps(results, indent=2))
    print("------------------------")

if __name__ == "__main__":
    asyncio.run(main())
