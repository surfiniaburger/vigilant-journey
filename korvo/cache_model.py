from sentence_transformers import SentenceTransformer

print("Caching sentence transformer model...")
SentenceTransformer("unsloth/embeddinggemma-300m")
print("Model cached successfully.")
