# scripts/reset_db.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
# from app.core.database import engine, Base
from app.models import Base
from app.core.logging import logger
from app.core.config import settings
from qdrant_client import QdrantClient
import asyncio

from qdrant_client.http import models
from app.core.config import QDRANT_CLIENT_URL, QDRANT_CLIENT_PORT
from app.core.config import EMBEDDING_DIM

def reset_postgresql():
    """Reset database and create tables"""
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # Drop all tables and recreate schema
        with engine.connect() as connection:
            connection.execute(text("DROP SCHEMA public CASCADE"))
            connection.execute(text("CREATE SCHEMA public"))
            connection.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            connection.execute(text("GRANT ALL ON SCHEMA public TO public"))
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
            connection.commit()
            logger.info("Reset schema")
            
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Created all tables")
        
        return True
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return False




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



if __name__ == "__main__":
    logger.info("Starting database reset...")
    
    pg_success = reset_postgresql()
    # qdrant_success = reset_qdrant()
    vector_store = VectorStore()
    qdrant_success = asyncio.run(vector_store.reset_collection())
    
    if pg_success and qdrant_success:
        logger.info("Successfully reset all databases")
    else:
        logger.error("Failed to reset one or more databases")
        sys.exit(1)