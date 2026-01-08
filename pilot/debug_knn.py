from pilot.google_search_agent import knn_validator
import json

res = knn_validator.validate_with_knn("test")
print("Keys:", res.keys())
print("Result:", res)
