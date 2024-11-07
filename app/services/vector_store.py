from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.core.config import settings
from app.core.logging import logger
import numpy as np
from app.core.config import QDRANT_CLIENT_URL, QDRANT_CLIENT_PORT
# from qdrant_client.async_client import AsyncQdrantClient
from app.core.config import EMBEDDING_DIM

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(QDRANT_CLIENT_URL, port=QDRANT_CLIENT_PORT)
        self.collection_name = "articles"
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=EMBEDDING_DIM,
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.collection_name}")

    async def add_article(self, article_id: str, vector: np.ndarray, payload: dict):
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=article_id,
                        vector=vector.tolist(),
                        payload=payload
                    )
                ]
            )
            logger.info(f"Added article {article_id} to vector store")
        except Exception as e:
            logger.error(f"Error adding article to vector store: {e}")
            raise

    async def search_articles(self, vector: np.ndarray, limit: int = 5):
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector.tolist(),
                limit=limit
            )
            return results
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise
        
    async def delete_article(self, article_id: str):
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[article_id]
                )
            )
            logger.info(f"Deleted article {article_id} from vector store")
        except Exception as e:
            logger.error(f"Error deleting article from vector store: {e}")
            raise
        
        
    async def reset_collection(self):
        """Reset the articles collection"""
        try:
            # Delete if exists
            try:
                self.client.delete_collection(self.collection_name)
            except Exception:
                pass
            # Create new collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=EMBEDDING_DIM,
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Reset collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            raise
