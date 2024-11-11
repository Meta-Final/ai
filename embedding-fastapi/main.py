from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from loguru import logger

class TextInput(BaseModel):
    texts: List[str]
    max_length: Optional[int] = 7680
    truncate: bool = False

class EmbeddingService:
    def __init__(self):
        self.model_name = "BM-K/KoSimCSE-roberta-multitask"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
        self.model.eval()
        logger.info(f"Initialized embedding model on {self.device}")

    @torch.no_grad()
    def get_embeddings(self, texts: List[str], max_length: int = 7680) -> np.ndarray:
        # Batch tokenization
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt"
        ).to(self.device)

        # Get embeddings
        outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :]
        
        return embeddings.cpu().numpy()

app = FastAPI()
embedding_service = None

@app.on_event("startup")
async def startup_event():
    global embedding_service
    embedding_service = EmbeddingService()

@app.get("/health")
async def health_check():
    if embedding_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return {"status": "healthy", "model": embedding_service.model_name}

@app.post("/embed")
async def get_embeddings(input_data: TextInput):
    try:
        embeddings = embedding_service.get_embeddings(
            input_data.texts,
            max_length=input_data.max_length
        )
        return {
            "embeddings": embeddings.tolist(),
            "dimensions": embeddings.shape[1]
        }
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)