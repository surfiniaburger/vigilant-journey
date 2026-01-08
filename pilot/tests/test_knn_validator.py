import pytest
import json
import importlib
import sys
from unittest.mock import patch, mock_open

# Mock data for unit testing
mock_corpus_data = [
    {"id": "doc1", "text": "This is a document about Mercedes brakes."},
    {"id": "doc2", "text": "This discusses engine oil viscosity."},
    {"id": "doc3", "text": "Irrelevant text about cooking."}
]

def test_knn_validator_logic():
    """
    Unit Test:
    Mocks the file loading and vectorizer training to test the internal logic.
    """
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_corpus_data))):
        with patch("json.load", return_value=mock_corpus_data):
            # Force reload to ensure it trains on the mock data
            from pilot.google_search_agent import knn_validator
            importlib.reload(knn_validator)
            
            # Match
            result = knn_validator.validate_with_knn("Mercedes brakes")
            assert result["confidence"] > 0
            
            # Mismatch
            result_irrelevant = knn_validator.validate_with_knn("pizza")
            assert result["confidence"] > result_irrelevant["confidence"]

def test_knn_validator_integration():
    """
    Integration Test:
    Verifies that the real 'mercedes_jargon_corpus.json' loads correctly 
    and the model works with verbatim text.
    """
    # Force reload WITHOUT any patches to ensure it loads the real file
    from pilot.google_search_agent import knn_validator
    importlib.reload(knn_validator)
    
    # Full verbatim text from the real corpus (id: dynamic_select_manual_001)
    query = ("The DYNAMIC SELECT switch is used to change between the following drive programs: "
             "Slippery, Individual, Comfort, Sport, Sport Plus, and RACE. The RACE program is for "
             "use on dedicated race circuits, not public roads. Depending on the selected program, "
             "vehicle characteristics such as engine and transmission management, "
             "Active Distance Assist DISTRONIC, AMG Dynamics, suspension, steering, "
             "and the position of the exhaust gas flaps will change.")
    result = knn_validator.validate_with_knn(query)
    
    # In the real model, verbatim text should have distance 0 -> confidence 1.0
    assert result["confidence"] > 0.9
    
    # Check that search for gibberish yields low confidence
    result_irrelevant = knn_validator.validate_with_knn("XYZABC123 Completely Irrelevant Text")
    assert result_irrelevant["confidence"] < 0.5
