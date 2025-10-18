# server.py - Your AI Co-Pilot's Brain, Wrapped as an ADK Tool

import asyncio
import logging
import os
from typing import Dict, Any


from fastmcp import FastMCP
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import cohere

# --- CONFIGURATION ---
# Load from environment variables for security and flexibility
ELASTIC_CLOUD_ID = os.environ.get("ELASTIC_CLOUD_ID")
ELASTIC_API_KEY = os.environ.get("ELASTIC_API_KEY")
COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
INDEX_NAME = "mercedes-manual-index"
EMBEDDING_DIM = 768

# --- INITIALIZE SERVICES (GLOBAL STATE) ---
# These are loaded once when the server starts, not on every request.
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

logger.info("Initializing AI Co-Pilot services...")
es_client = Elasticsearch(cloud_id=ELASTIC_CLOUD_ID, api_key=ELASTIC_API_KEY)
embedding_model = SentenceTransformer("unsloth/embeddinggemma-300m")
co = cohere.Client(api_key=COHERE_API_KEY)
logger.info("✅ All services connected and models loaded.")

# --- MCP SERVER SETUP ---
mcp = FastMCP("Alora - The Mercedes-AMG AI Co-Pilot 🚗")

# --- THE RAG PIPELINE (Encapsulated Logic) ---

def search_manual(query: str, num_results: int = 5) -> str:
    """Performs hybrid search on the Mercedes manual index."""
    logger.info(f"Executing hybrid search for query: '{query}'")
    query_vector = embedding_model.encode(query).tolist()
    
    search_query = {
        "size": num_results,
        "query": {"match": {"chunk_text": {"query": query, "boost": 0.1}}},
        "knn": {
            "field": "embedding", "query_vector": query_vector,
            "k": num_results, "num_candidates": 50, "boost": 0.9
        }
    }
    response = es_client.search(index=INDEX_NAME, body=search_query)
    context = "\n\n---\n\n".join([hit['_source']['chunk_text'] for hit in response["hits"]["hits"]])
    return context

def generate_answer(query: str, context: str) -> str:
    """Generates a grounded answer using the Cohere API."""
    logger.info("Synthesizing final answer with LLM...")
    message = f"""
    You are an expert AI co-pilot for the Mercedes-AMG GT R.
    Your task is to answer the user's question based ONLY on the provided context from the official operator's manual.
    If the information is not present in the context, you MUST state that the manual does not provide that specific detail.
    Do not use any prior knowledge. Format your answer clearly and concisely.

    --- CONTEXT FROM MANUAL ---
    {context}
    --- END OF CONTEXT ---

    USER QUESTION: {query}
    """
    response = co.chat(model='command-a-03-2025', message=message, temperature=0.1)
    return response.text

# --- THE TOOL FOR GOOGLE ADK ---

@mcp.tool()
def ask_amg_manual(question: str) -> Dict[str, Any]:
    """
    Answers any question about the Mercedes-AMG GT R by consulting the official operator's manual.
    Use this tool to find information on features, warnings, maintenance, and vehicle operations.

    Args:
        question: The user's question about the car (e.g., 'How do I use RACE START?').

    Returns:
        A dictionary containing the final, grounded answer.
    """
    logger.info(f">>> 🛠️ Tool: 'ask_amg_manual' called with question: '{question}'")
    try:
        # Step 1: Retrieve Context
        retrieved_context = search_manual(question)
        
        # Step 2: Generate Answer
        final_answer = generate_answer(question, retrieved_context)
        
        return {"answer": final_answer}

    except Exception as e:
        logger.error(f"Error in RAG pipeline: {e}")
        return {"error": "I encountered an issue trying to look that up. Please try rephrasing your question."}

# --- SERVER LIFECYCLE ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 Alora MCP server starting on port {port}")
    asyncio.run(
        mcp.run_async(transport="http", host="0.0.0.0", port=port)
    )