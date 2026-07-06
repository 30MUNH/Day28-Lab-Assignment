# scripts/mock_kaggle_services.py
from fastapi import FastAPI
import uvicorn
import threading
import time

# vLLM Mock Server (port 8001)
vllm_app = FastAPI()

@vllm_app.get("/health")
@vllm_app.get("/v1/health")
def vllm_health():
    return {"status": "healthy"}

@vllm_app.post("/v1/chat/completions")
def chat_completions(data: dict):
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "This is a mock answer from Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4. Event-driven architectures and platform engineering are great!"
                }
            }
        ],
        "model": "Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4"
    }

# Embedding Mock Server (port 8002)
embed_app = FastAPI()

@embed_app.get("/health")
@embed_app.get("/v1/health")
def embed_health():
    return {"status": "healthy"}

@embed_app.post("/v1/embeddings")
def v1_embeddings(data: dict):
    inp = data.get("input", "")
    if isinstance(inp, str):
        inp = [inp]
    embeddings_list = []
    for i, text in enumerate(inp):
        embeddings_list.append({
            "object": "embedding",
            "index": i,
            "embedding": [0.1] * 384
        })
    return {
        "object": "list",
        "data": embeddings_list,
        "model": data.get("model", "sentence-transformers/all-MiniLM-L6-v2")
    }

@embed_app.post("/embed")
def embed(data: dict):
    texts = data.get("texts", [])
    # Return a dummy 384-dimensional vector for each text
    return {"embeddings": [[0.1] * 384 for _ in texts]}

def run_vllm():
    uvicorn.run(vllm_app, host="0.0.0.0", port=8001, log_level="warning")

def run_embed():
    uvicorn.run(embed_app, host="0.0.0.0", port=8002, log_level="warning")

if __name__ == "__main__":
    t1 = threading.Thread(target=run_vllm, daemon=True)
    t2 = threading.Thread(target=run_embed, daemon=True)
    t1.start()
    t2.start()
    print("Mock Kaggle services started:")
    print("  - vLLM mock on http://localhost:8001")
    print("  - Embedding mock on http://localhost:8002")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping mock services...")
