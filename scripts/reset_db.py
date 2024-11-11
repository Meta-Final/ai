import sys
from pathlib import Path
import os

# Add project root to Python path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# Set env file path
os.environ["ENV_FILE"] = str(ROOT_DIR / ".env")



from sqlalchemy import create_engine, text
from app.models import Base
from app.core.logging import logger
from app.core.config import settings
from app.services.vector_store import VectorStore
import asyncio
from qdrant_client import QdrantClient
from qdrant_client.http import models

def create_db_user():
    """Create database user and grant privileges"""
    engine = create_engine("postgresql://final_project_admin:final_project_admin_password@backend-db-container:5432/llm_api")  # Need admin connection first
    
    DATABASE_HOST="backend-db-container"
    db_user = settings.DATABASE_USER
    db_password = settings.DATABASE_PASSWORD
    db_name = settings.DATABASE_NAME
    
    try:
        with engine.connect() as connection:
            # Create user if not exists
            connection.execute(text(f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '{db_user}') THEN
                        CREATE USER {db_user} WITH PASSWORD '{db_password}';
                    END IF;
                END
                $$;
            """))
            
            # Create database if not exists
            connection.execute(text(f"""
                CREATE DATABASE {db_name}
                    WITH 
                    OWNER = {db_user}
                    ENCODING = 'UTF8'
                    LC_COLLATE = 'en_US.utf8'
                    LC_CTYPE = 'en_US.utf8';
            """))
            
            # Grant privileges
            connection.execute(text(f"""
                GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};
            """))
            connection.commit()
            logger.info(f"Created user {db_user} and database {db_name}")
            return True
    except Exception as e:
        logger.error(f"Error creating database user: {e}")
        return False

def reset_postgresql():
    """Reset database and create tables"""
    engine = create_engine("postgresql://final_project_user:final_project_user_password@backend-db-container:5432/llm_api")
    
    try:
        # Drop all tables and recreate schema
        with engine.connect() as connection:
            connection.execute(text("DROP SCHEMA public CASCADE"))
            connection.execute(text("CREATE SCHEMA public"))
            connection.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            connection.execute(text("GRANT ALL ON SCHEMA public TO public"))
            connection.execute(text(f"GRANT ALL ON SCHEMA public TO {settings.DATABASE_USER}"))
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


# class VectorStore:
#     def __init__(self):
#         self.client = QdrantClient(settings.QDRANT_CLIENT_URL, port=settings.QDRANT_CLIENT_PORT)
#         self.collection_name = "articles"
#         self._ensure_collection()

#     def _ensure_collection(self):
#         try:
#             self.client.get_collection(self.collection_name)
#         except Exception:
#             self.client.create_collection(
#                 collection_name=self.collection_name,
#                 vectors_config=models.VectorParams(
#                     size=settings.EMBEDDING_DIM,
#                     distance=models.Distance.COSINE
#                 )
#             )
#             logger.info(f"Created collection: {self.collection_name}")

#     async def reset_collection(self):
#         """Reset the articles collection"""
#         try:
#             # Delete if exists
#             try:
#                 self.client.delete_collection(self.collection_name)
#             except Exception:
#                 pass
#             # Create new collection
#             self.client.create_collection(
#                 collection_name=self.collection_name,
#                 vectors_config=models.VectorParams(
#                     size=settings.EMBEDDING_DIM,
#                     distance=models.Distance.COSINE
#                 )
#             )
#             logger.info(f"Reset collection: {self.collection_name}")
#         except Exception as e:
#             logger.error(f"Error resetting collection: {e}")
#             raise



if __name__ == "__main__":
    logger.info("Starting database reset...")
    
    user_created = create_db_user()
    if not user_created:
        logger.error("Failed to create database user")
        sys.exit(1)
        
    pg_success = reset_postgresql()
    vector_store = VectorStore()
    qdrant_success = asyncio.run(vector_store.reset_collection())
    
    if pg_success and qdrant_success:
        logger.info("Successfully reset all databases")
    else:
        logger.error("Failed to reset one or more databases")
        sys.exit(1)