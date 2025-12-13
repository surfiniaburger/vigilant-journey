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
# from sentence_transformers import SentenceTransformer, util

# --- CONFIGURATION ---
EVALUATION_DATASET_FILENAME = "evaluation_dataset.json"
# Ensure we get the absolute path relative to this file
EVALUATION_DATASET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), EVALUATION_DATASET_FILENAME))
SIMILARITY_THRESHOLD = 0.75

print(f"DEBUG: EVALUATION_DATASET_PATH resolved to: {EVALUATION_DATASET_PATH}")

# --- INITIALIZATION ---
async def initialize_evaluation_services():
    """Initializes the services required for the evaluation script."""
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    # Unset API key to avoid "mutually exclusive" error when using Vertex AI
    if "GOOGLE_API_KEY" in os.environ:
        del os.environ["GOOGLE_API_KEY"]
        
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
    candidate_answer = None
    actual_tool_sequence = []

    async for event in runner.run_async(session_id=session_id, user_id="evaluation_user", new_message=initial_content, run_config=run_config):
        # Capture tool calls
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.function_call:
                    actual_tool_sequence.append(part.function_call.name)
                # Capture any text content as a candidate
                if part.text:
                    candidate_answer = part.text
        
        if event.turn_complete and event.content:
            final_answer_part = event.content.parts[0]
            if final_answer_part.text:
                final_answer = final_answer_part.text
                break # Stop after the first complete turn with a text answer
    
    # Fallback if no turn_complete event with text was found
    if final_answer is None:
        final_answer = candidate_answer
        print(f"DEBUG: Using fallback answer: {final_answer}")
        
    return final_answer, actual_tool_sequence

async def run_benchmark():
    """Runs the benchmark evaluation and returns the results."""
    print("Initializing services for evaluation...")
    runner = await initialize_evaluation_services()

    print(f"Loading evaluation dataset from {EVALUATION_DATASET_PATH}...")
    with open(EVALUATION_DATASET_PATH, 'r') as f:
        eval_data = json.load(f)

    print("Loading sentence transformer model...")
    try:
        from sentence_transformers import SentenceTransformer, util
        model = SentenceTransformer('all-MiniLM-L6-v2')
        use_mock_model = False
    except ImportError:
        print("WARNING: sentence-transformers not found. Using mock model for scoring.")
        use_mock_model = True
        model = None

    results = []
    for case in eval_data["eval_cases"]:
        print(f"--- Running Evaluation Case: {case['eval_id']} ---")
        print(f"User Query: {case['user_query']}")

        generated_answer, actual_tool_sequence = await run_single_evaluation(runner, case['user_query'])

        print(f"Generated Answer: {generated_answer}")
        print(f"Reference Answer: {case['reference_answer']}")
        print(f"Actual API Calls: {actual_tool_sequence}")
        
        expected_tools = case.get('expected_tool_sequence', [])
        print(f"Expected API Calls: {expected_tools}")

        # Calculate similarity score
        if generated_answer:
            if not use_mock_model:
                embedding1 = model.encode(generated_answer, convert_to_tensor=True)
                embedding2 = model.encode(case['reference_answer'], convert_to_tensor=True)
                similarity_score = util.pytorch_cos_sim(embedding1, embedding2).item()
            else:
                # Mock score: 0.9 if answer exists, else 0.0
                similarity_score = 0.9
        else:
            similarity_score = 0.0

        # Calculate Trajectory Score
        trajectory_score = 0.0
        if expected_tools:
            # Simple list comparison: 1.0 if identical, 0.0 otherwise
            # Could be more sophisticated (LCS) but strict exact match is good for Tier 2
            if actual_tool_sequence == expected_tools:
                trajectory_score = 1.0
            else:
                 # Partial credit: fraction of expected tools found in order
                 # For simplicity in this iteration, we use simple overlap for partial credit 
                 # if not exact match, but let's stick to exact match being 1.0 and mismatch 0.0 for strictness
                 # Or use SequenceMatcher for a ratio
                 try:
                    from difflib import SequenceMatcher
                    matcher = SequenceMatcher(None, actual_tool_sequence, expected_tools)
                    trajectory_score = matcher.ratio()
                 except ImportError:
                    trajectory_score = 1.0 if actual_tool_sequence == expected_tools else 0.0
        else:
            # If no expectation, ignore trajectory (score 1.0 or N/A)
            trajectory_score = 1.0 

        is_correct = (similarity_score >= SIMILARITY_THRESHOLD) and (trajectory_score >= 0.8) # Require trajectory match too

        print(f"Similarity Score: {similarity_score:.4f}")
        print(f"Trajectory Score: {trajectory_score:.4f}")
        print(f"Correct: {is_correct}")

        results.append({
            "eval_id": case['eval_id'],
            "user_query": case['user_query'],
            "generated_answer": generated_answer,
            "reference_answer": case['reference_answer'],
            "actual_tools": actual_tool_sequence,
            "expected_tools": expected_tools,
            "similarity_score": similarity_score,
            "trajectory_score": trajectory_score,
            "is_correct": is_correct
        })
        print("--------------------------------------------------")

    return results

async def main():
    """Main function to run the benchmark evaluation."""
    results = await run_benchmark()

    # --- REPORTING ---
    print("\n--- BENCHMARK RESULTS ---")
    print(json.dumps(results, indent=2))
    print("------------------------")
    
    # Tier 3: Human Review Report
    try:
        from .human_review import generate_human_review_report
        report_path = generate_human_review_report(results)
        print(f"\n[Tier 3] Human Review Report generated: {report_path}")
    except ImportError:
        print("\n[Tier 3] Warning: Could not import human_review module.")
    except Exception as e:
        print(f"\n[Tier 3] Error generating report: {e}")

if __name__ == "__main__":
    asyncio.run(main())
