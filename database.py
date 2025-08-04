from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from settings import get_settings

# Get settings
settings = get_settings()

# Use database_url from settings
SQLALCHEMY_DATABASE_URL = settings.database_url

# Remove SQLite-specific connect_args
engine = create_engine(SQLALCHEMY_DATABASE_URL)

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # Attempt to connect
    with engine.connect() as connection:
        # You can execute a simple query to confirm the connection is active
        # For PostgreSQL, 'SELECT 1' is a common no-op query.
        connection.execute(text("SELECT 1"))
        print("Database connection successfully established!")

except Exception as e:
    print(f"Error connecting to the database: {e}")

finally:
    # It's good practice to dispose of the engine if it's no longer needed
    # This closes all connections in the pool.
    if 'engine' in locals(): # Check if engine was created
        engine.dispose()
        print("Engine disposed.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
