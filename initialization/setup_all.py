# RUN THIS SCRIPT TO SETUP THE DATABASE AND QDRANT VECTOR STORE
# ON ROOT DIRECTORY, RUN THE FOLLOWING COMMAND: 
# python -m initialization.setup_all


import os
import sys
from pathlib import Path

# Get absolute path of the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Add project root to Python path
# project_root = str(Path(__file__).parent.parent)
# sys.path.append(project_root)

from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database
from app.models import Base
from dotenv import load_dotenv
import time
from qdrant_client import QdrantClient
from qdrant_client.http import models

class DatabaseInitializer:
    def __init__(self):
        load_dotenv()
        
        # PostgreSQL settings
        self.admin_url = "postgresql://postgres:postgres@localhost:5432/postgres"
        self.db_url = (
            "postgresql://final_project_user:final_project_user_password@"
            "localhost:5432/llm_api"
        )
        
        # Qdrant settings
        self.qdrant_host = "localhost"
        self.qdrant_port = 6333
        self.collection_name = "articles"
        self.vector_size = 768

    def init_qdrant(self):
        """Initialize Qdrant vector store"""
        try:
            print("Initializing Qdrant...")
            client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
            
            # Delete collection if exists
            try:
                client.delete_collection(self.collection_name)
                print(f"Deleted existing collection: {self.collection_name}")
            except Exception:
                pass

            # Create new collection
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE
                )
            )
            print(f"Created new collection: {self.collection_name}")
            
        except Exception as e:
            print(f"Error initializing Qdrant: {str(e)}")
            raise

    def create_user(self):
        """Create database user if it doesn't exist"""
        try:
            engine = create_engine(self.admin_url)
            with engine.connect() as conn:
                # Check if user exists
                result = conn.execute(
                    text("SELECT 1 FROM pg_user WHERE usename = 'final_project_user'")
                )
                user_exists = result.scalar() is not None

                if not user_exists:
                    conn.execute(text("commit"))
                    conn.execute(
                        text("CREATE USER final_project_user WITH PASSWORD 'final_project_user_password'")
                    )
                    print("User 'final_project_user' created successfully")
                else:
                    print("User 'final_project_user' already exists")

                # Grant privileges
                conn.execute(text("commit"))
                privilege_commands = [
                    "GRANT ALL ON SCHEMA public TO final_project_user",
                    "GRANT USAGE ON SCHEMA public TO final_project_user",
                    "GRANT CREATE ON SCHEMA public TO final_project_user",
                    "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO final_project_user",
                    "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO final_project_user",
                    "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO final_project_user",
                    "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO final_project_user"
                ]
                
                for command in privilege_commands:
                    conn.execute(text(command))
                    conn.execute(text("commit"))
                
                print("Privileges granted successfully")

        except Exception as e:
            print(f"Error creating user: {str(e)}")
            raise

    def create_database(self):
        """Create database if it doesn't exist"""
        try:
            engine = create_engine(self.admin_url)
            with engine.connect() as conn:
                conn.execute(text("commit"))
                conn.execute(text("DROP DATABASE IF EXISTS llm_api"))
                print("Dropped existing database 'llm_api'")
                conn.execute(text("CREATE DATABASE llm_api"))
                print("Database 'llm_api' created successfully")
                
                # Set database owner
                conn.execute(text("commit"))
                conn.execute(text("ALTER DATABASE llm_api OWNER TO final_project_user"))
                print("Database owner set successfully")
                
        except Exception as e:
            print(f"Error creating database: {str(e)}")
            raise

    def create_tables(self):
        """Create all tables defined in SQLAlchemy models"""
        try:
            engine = create_engine(self.db_url)
            Base.metadata.create_all(engine)
            print("Tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {str(e)}")
            raise

    def init_db(self):
        """Initialize both PostgreSQL and Qdrant"""
        try:
            print("Starting database initialization...")
            
            # Initialize PostgreSQL
            self.create_user()
            self.create_database()
            self.create_tables()
            
            # Initialize Qdrant
            self.init_qdrant()
            
            print("Database initialization completed successfully!")
            
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            raise

def main():
    initializer = DatabaseInitializer()
    initializer.init_db()

if __name__ == "__main__":
    main()