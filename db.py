# db.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "queuectl"

# This holds the connection *per-process*
_client = None

def get_db():
    """
    Connects to the database if not already connected.
    This function is process-safe.
    """
    global _client
    
    # Check if this specific process is already connected
    if _client is None:
        try:
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            _client.server_info() # Force connection check
            
        except Exception as e:
            # We will let the caller (the worker log) print the error
            _client = None # Ensure client remains None if connection fails
            return None, None, None # Return None to signal failure

    # If connection was successful (or already existed)
    db = _client[DB_NAME]
    jobs_collection = db["jobs"]
    dlq_collection = db["dlq"]
    
    return db, jobs_collection, dlq_collection

def ensure_indexes():
    """
    Ensures the necessary indexes exist.
    This is safe to call multiple times.
    RAISES AN EXCEPTION ON FAILURE.
    """
    # We REMOVED the try/except block.
    # Now, if create_index fails, it will raise an exception.
    
    db, jobs_collection, _ = get_db()
    if db is not None:
        jobs_collection.create_index("id", unique=True)
        jobs_collection.create_index("state")
        jobs_collection.create_index([("state", 1), ("run_at", 1)])
        return True
    else:
        # This will be caught by the worker if get_db() fails
        raise Exception("get_db() returned None while ensuring indexes.")