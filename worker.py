# worker.py
import time
import subprocess
import datetime
import os
import signal
import sys
from pymongo import ReturnDocument
from db import get_db, ensure_indexes # Import the helper functions

# --- Worker-specific globals ---
WORKER_ID = f"pid_{os.getpid()}" # Initial ID, will be updated
RUNNING = True # Flag for graceful shutdown

def handle_shutdown(sig, frame):
    """
    Signal handler for the CHILD process.
    Catches SIGTERM from the parent and sets RUNNING to False.
    """
    global RUNNING
    if RUNNING:
        print(f"Worker {WORKER_ID}: 🛑 Shutdown signal received. Finishing current job...")
        RUNNING = False
    else:
        print(f"Worker {WORKER_ID}: 🛑 Shutdown signal received again. Forcing exit.")
        exit(1)


def find_and_lock_job(jobs_collection):
    """
    Atomically find a 'pending' job, set its state to 'processing',
    and return it.
    """
    try:
        now = datetime.datetime.utcnow()
        
        job = jobs_collection.find_one_and_update(
            {
                "state": "pending",
                "run_at": {"$lte": now}
            },
            {
                "$set": {
                    "state": "processing",
                    "updated_at": now,
                    "worker_id": WORKER_ID
                }
            },
            sort=[("created_at", 1)],
            return_document=ReturnDocument.AFTER
        )
        return job
    except Exception as e:
        print(f"Worker {WORKER_ID}: ❌ Error finding job: {e}")
        return None

def execute_job(job):
    """Execute the job's command using subprocess."""
    print(f"Worker {WORKER_ID}: 🚀 Starting job {job['id']}: {job['command']}")
    try:
        result = subprocess.run(
            job['command'], 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"Worker {WORKER_ID}: ✅ Finished job {job['id']}")
            return True, None
        else:
            stderr = result.stderr or "No stderr output."
            print(f"Worker {WORKER_ID}: ❌ Job {job['id']} failed. Stderr: {stderr.strip()}")
            return False, stderr
            
    except Exception as e:
        print(f"Worker {WORKER_ID}: ❌ Job {job['id']} execution error: {e}")
        return False, str(e)

def handle_job_success(jobs_collection, job):
    """Set job state to 'completed'."""
    jobs_collection.update_one(
        {"id": job["id"]},
        {"$set": {
            "state": "completed", 
            "updated_at": datetime.datetime.utcnow(),
            "worker_id": None
        }}
    )

def handle_job_failure(jobs_collection, dlq_collection, job, error_message, base):
    """Handle retries with exponential backoff or move to DLQ."""
    new_attempts = job.get("attempts", 0) + 1
    
    if new_attempts >= job["max_retries"]:
        print(f"Worker {WORKER_ID}: 💀 Job {job['id']} failed max retries. Moving to DLQ.")
        job["state"] = "dead"
        job["updated_at"] = datetime.datetime.utcnow()
        job["last_error"] = error_message
        job["worker_id"] = None
        
        dlq_collection.insert_one(job)
        jobs_collection.delete_one({"id": job["id"]})
        
    else:
        delay_seconds = base ** new_attempts
        run_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay_seconds)
        
        print(f"Worker {WORKER_ID}: 🔁 Job {job['id']} retrying ({new_attempts}/{job['max_retries']}). Next run in {delay_seconds}s.")
        
        jobs_collection.update_one(
            {"id": job["id"]},
            {"$set": {
                "state": "pending",
                "attempts": new_attempts,
                "run_at": run_at,
                "updated_at": datetime.datetime.utcnow(),
                "last_error": error_message,
                "worker_id": None
            }}
        )

def start_worker(backoff_base):
    """Main worker loop."""
    global WORKER_ID, RUNNING
    
    # --- 1. SET UP LOGGING (THIS MUST BE FIRST) ---
    pid = os.getpid()
    WORKER_ID = f"pid_{pid}" # Set the global worker ID
    
    try:
        os.makedirs("logs", exist_ok=True)
        log_file_path = f"logs/worker_{pid}.log"
        
        # This print goes to the console that launched 'worker start'
        print(f"Worker {pid} starting. Logging to {log_file_path}") 
        
        sys.stdout = open(log_file_path, 'a', buffering=1, encoding='utf-8')
        sys.stderr = sys.stdout
    except Exception as e:
        # If logging fails, we can't do anything.
        print(f"CRITICAL: Worker {pid} failed to open log file. Exiting. Error: {e}")
        return
    
    # --- 2. SET UP SHUTDOWN HANDLERS ---
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore Ctrl+C
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    print(f"--- Worker {WORKER_ID} log started at {datetime.datetime.utcnow()} ---")
    print(f"Using backoff base: {backoff_base}")
    
    # --- 3. CONNECT TO DATABASE ---
    db, jobs_collection, dlq_collection = None, None, None
    try:
        db, jobs_collection, dlq_collection = get_db()
        if db is None:
            raise Exception("Database connection failed. get_db() returned None.")
        
        # Ensure indexes are created by the worker
        if not ensure_indexes():
             raise Exception("Failed to create database indexes.")
             
        print("MongoDB connection successful and indexes ensured.")
        
    except Exception as e:
        print(f"CRITICAL: Worker {WORKER_ID} exiting. DB setup failed: {e}")
        RUNNING = False # Stop the worker loop
    
    # --- 4. START THE MAIN LOOP ---
    while RUNNING:
        try:
            job = find_and_lock_job(jobs_collection)
            
            if job:
                success, error = execute_job(job)
                
                if success:
                    handle_job_success(jobs_collection, job)
                else:
                    handle_job_failure(jobs_collection, dlq_collection, job, error, backoff_base)
            else:
                if RUNNING:
                    time.sleep(1) # Sleep to avoid busy-waiting
                    
        except Exception as e:
            # Catch-all for safety in the loop
            print(f"CRITICAL: Unhandled error in worker loop: {e}")
            time.sleep(5)
    
    print(f"Worker {WORKER_ID}: Gracefully shutting down.")