from httpx import AsyncClient
import numpy as np
from app.core.logging import logger
# from app.core.config import settings

class EmbeddingService:
    def __init__(self):
        self.embedding_service_url = "http://embedding-service:8001"
        self.client = AsyncClient()
        logger.info(f"Initialized embedding client for {self.embedding_service_url}")

    async def get_embedding(self, text: str) -> np.ndarray:
        try:
            response = await self.client.post(
                f"{self.embedding_service_url}/embed",
                json={"texts": [text]}
            )
            response.raise_for_status()
            embeddings = response.json()["embeddings"]
            return np.array(embeddings[0])
        except Exception as e:
            logger.error(f"Error getting embedding from service: {e}")
            raise

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()