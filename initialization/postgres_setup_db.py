# import os
# import sys
# from pathlib import Path

# # Add project root to Python path
# project_root = str(Path(__file__).parent.parent)
# sys.path.append(project_root)

# from sqlalchemy import create_engine, text
# from sqlalchemy_utils import database_exists, create_database
# from app.models import Base
# from dotenv import load_dotenv
# import time

# class DatabaseInitializer:
#     def __init__(self):
#         load_dotenv()
        
#         # Connection URLs for localhost (host machine)
#         self.postgres_url = "postgresql://postgres:postgres@localhost:5432/postgres"
#         self.database_url = (
#             "postgresql://final_project_user:final_project_user_password@"
#             "localhost:5432/llm_api"
#         )
        
#         # Get the path to the SQL file
#         self.current_dir = Path(__file__).parent
#         self.sql_file_path = self.current_dir / "sql" / "init-db.sql"

#     def create_database(self, engine):
#         """Create database if it doesn't exist"""
#         try:
#             with engine.connect() as conn:
#                 # Commit any existing transaction
#                 conn.execute(text("commit"))
#                 # Create database
#                 conn.execute(text("CREATE DATABASE llm_api"))
#                 print("Database 'llm_api' created successfully")
#         except Exception as e:
#             if "already exists" not in str(e):
#                 print(f"Error creating database: {str(e)}")
#                 raise
#             print("Database 'llm_api' already exists")

#     def execute_sql_file(self, engine):
#         """Execute the SQL initialization file"""
#         try:
#             with engine.connect() as conn:
#                 # Execute SQL commands
#                 with open(self.sql_file_path, 'r') as file:
#                     sql_commands = file.read()
#                     conn.execute(text("commit"))  # Ensure we're not in a transaction
#                     conn.execute(text(sql_commands))
#                     conn.commit()
#                 print("SQL initialization completed successfully")
#         except Exception as e:
#             print(f"Error executing SQL file: {str(e)}")
#             raise

#     def create_tables(self):
#         """Create all tables defined in SQLAlchemy models"""
#         try:
#             engine = create_engine(self.database_url)
#             Base.metadata.create_all(engine)
#             print("Tables created successfully")
#         except Exception as e:
#             print(f"Error creating tables: {str(e)}")
#             raise

#     def init_db(self):
#         """Initialize the database"""
#         try:
#             print("Initializing database...")
            
#             # Create initial engine to create database
#             engine = create_engine(self.postgres_url)
            
#             # Create database
#             self.create_database(engine)
            
#             # Execute the SQL initialization script
#             self.execute_sql_file(engine)
            
#             # Create all tables
#             self.create_tables()
            
#             print("Database initialization completed successfully!")
            
#         except Exception as e:
#             print(f"Error initializing database: {str(e)}")
#             raise

# def main():
#     initializer = DatabaseInitializer()
#     initializer.init_db()

# if __name__ == "__main__":
#     main()

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database
from app.models import Base
from dotenv import load_dotenv
import time

class DatabaseInitializer:
    def __init__(self):
        load_dotenv()
        
        # Connection URLs for localhost (host machine)
        self.admin_url = "postgresql://postgres:postgres@localhost:5432/postgres"
        self.db_url = (
            "postgresql://final_project_user:final_project_user_password@"
            "localhost:5432/llm_api"
        )
        
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
                    # Create new user
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
                conn.execute(text("CREATE DATABASE llm_api"))
                print("Database 'llm_api' created successfully")
                
                # Set database owner
                conn.execute(text("commit"))
                conn.execute(text("ALTER DATABASE llm_api OWNER TO final_project_user"))
                print("Database owner set successfully")
                
        except Exception as e:
            if "already exists" not in str(e):
                print(f"Error creating database: {str(e)}")
                raise
            print("Database 'llm_api' already exists")

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
        """Initialize the database"""
        try:
            print("Initializing database...")
            
            # Create user and grant privileges
            self.create_user()
            
            # Create database
            self.create_database()
            
            # Create all tables
            self.create_tables()
            
            print("Database initialization completed successfully!")
            
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            raise

def main():
    initializer = DatabaseInitializer()
    initializer.init_db()

if __name__ == "__main__":
    main()