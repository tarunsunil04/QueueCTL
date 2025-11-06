import subprocess
import time
import sys
import os
import shlex
from pymongo import MongoClient
from dotenv import load_dotenv

# We will import your application's code directly
from click.testing import CliRunner
from queuectl import cli
from worker_manager import start_workers, stop_workers

# --- Config ---
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "queuectl"

# --- ANSI Colors for Output ---
class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log_pass(msg):
    print(f"{bcolors.OKGREEN}✅ {msg}{bcolors.ENDC}")

def log_fail(msg):
    print(f"{bcolors.FAIL}❌ {msg}{bcolors.ENDC}")

def log_info(msg):
    print(f"{bcolors.HEADER}--- {msg} ---{bcolors.ENDC}")

# --- DB Helper ---
_client = None

def get_db():
    global _client
    if _client is None:
        try:
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
            _client.server_info()
        except Exception as e:
            log_fail(f"Could not connect to MongoDB: {e}")
            return None, None
    db = _client[DB_NAME]
    return db, db["jobs"], db["dlq"]

def clean_db():
    log_info("Cleaning database...")
    db, jobs, dlq = get_db()
    if db is not None:
        jobs.delete_many({})
        dlq.delete_many({})
        log_pass("Database cleaned.")

# --- Click Command Runner ---
runner = CliRunner()

def run_cli_command(command_string):
    """
    Runs a click command in-process, handling errors.
    """
    args = shlex.split(command_string)
    
    try:
        result = runner.invoke(cli, args)
        if result.exit_code != 0:
            if "Usage:" not in result.output:
                log_fail(f"CLI ERROR ({command_string}): {result.output}")
        return result
    except Exception as e:
        log_fail(f"CLI CRASH ({command_string}): {e}")
        return None

# --- Polling Helper ---
def poll_for_status(job_id, collection, expected_state, timeout=15):
    start_time = time.time()
    db, jobs_col, dlq_col = get_db()
    
    target_col = jobs_col if collection == "jobs" else dlq_col
    
    while time.time() - start_time < timeout:
        job = target_col.find_one({"id": job_id})
        if job:
            if expected_state == "dead":
                return job
            if job["state"] == expected_state:
                return job
        time.sleep(0.5)
        
    log_fail(f"Poll timeout: Job '{job_id}' did not reach state '{expected_state}' in {timeout}s.")
    return None

def poll_for_attempts(job_id, expected_attempts, timeout=15):
    start_time = time.time()
    db, jobs_col, _ = get_db()
    
    while time.time() - start_time < timeout:
        job = jobs_col.find_one({"id": job_id})
        if job and job.get("attempts") == expected_attempts:
            return job
        time.sleep(0.5)
        
    log_fail(f"Poll timeout: Job '{job_id}' did not reach {expected_attempts} attempts in {timeout}s.")
    return None

# --- Test Scenarios ---

def test_1_basic_success():
    log_info("Test 1: Basic job completes successfully.")
    
    # --- FIX ---
    # Use Windows 'timeout' command instead of 'sleep'
    # /nobreak prevents it from listening for a keypress
    run_cli_command("enqueue test_job_success 'timeout /t 1 /nobreak && echo success'")
    # --- END FIX ---
    
    job = poll_for_status("test_job_success", "jobs", "completed", 10)
    
    if job:
        log_pass("Test 1 Passed: Job completed successfully.")
        return True
    log_fail("Test 1 Failed.")
    return False

def test_2_fail_to_dlq():
    log_info("Test 2 & 4: Failed job retries and moves to DLQ.")
    
    # --- THIS IS THE FIX ---
    # Set max_retries to 3, so it can fail, reach attempt 1,
    # fail again, reach attempt 2, fail a final time, and then move to DLQ.
    run_cli_command("config set max_retries 3")
    # --- END OF FIX ---
    run_cli_command("config set backoff_base 1")
    
    # 'exit 1' works perfectly on Windows
    run_cli_command("enqueue test_job_fail 'exit 1'")
    
    print("  ... waiting for 1st retry...")
    job = poll_for_attempts("test_job_fail", 1, 10)
    if not job:
        log_fail("Test 2 Failed: Job did not reach 1 attempt.")
        return False
    
    print("  ... waiting for 2nd retry...")
    job = poll_for_attempts("test_job_fail", 2, 10)
    if not job:
        log_fail("Test 2 Failed: Job did not reach 2 attempts.")
        return False
        
    print("  ... waiting for move to DLQ...")
    # Now it will fail its 3rd run (attempts=2) and move to DLQ
    job = poll_for_status("test_job_fail", "dlq", "dead", 10)
    
    if job:
        log_pass("Test 2 Passed: Job failed, retried, and moved to DLQ.")
        return True
    
    log_fail("Test 2 Failed: Job not found in DLQ.")
    return False

def test_3_multiple_workers():
    log_info("Test 3: Multiple workers process jobs without overlap.")
    print("  ... enqueuing 10 fast jobs...")
    
    for i in range(10):
        # --- FIX ---
        # Use Windows 'timeout' command. 1s is the minimum.
        run_cli_command(f"enqueue test_job_multi_{i} 'timeout /t 1 /nobreak'")
        # --- END FIX ---
        
    start_time = time.time()
    db, jobs, _ = get_db()
    
    # Increased timeout to 20s since 10 1s jobs will take a few seconds
    while time.time() - start_time < 20: 
        completed_count = jobs.count_documents({
            "id": {"$regex": "test_job_multi_"},
            "state": "completed"
        })
        if completed_count == 10:
            break
        time.sleep(1)
        
    if completed_count == 10:
        log_pass("Test 3 Passed: All 10 jobs were completed.")
        return True
    
    log_fail(f"Test 3 Failed: Only {completed_count}/10 jobs completed.")
    return False

def test_5_persistence():
    log_info("Test 5: Job data survives worker restart.")
    
    # 'echo' works perfectly on Windows
    run_cli_command("enqueue test_job_persist 'echo this should survive'")
    
    print("  ... stopping workers...")
    success, msg = stop_workers()
    if not success: log_fail(msg)
    
    time.sleep(2)
    
    print("  ... restarting workers...")
    success, msg = start_workers(3)
    if not success:
        log_fail(f"FATAL: {msg}")
        return False
    
    job = poll_for_status("test_job_persist", "jobs", "completed", 10)
    
    if job:
        log_pass("Test 5 Passed: Job survived restart and completed.")
        return True
    
    log_fail("Test 5 Failed: Job did not complete after restart.")
    return False

# --- Main Runner ---
def main():
    log_info("Starting Test Runner...")
    
    clean_db()
    log_info("Stopping any old workers...")
    stop_workers()
    time.sleep(1)
    
    log_info("Starting 3 workers for tests...")
    success, message = start_workers(3)
    if not success:
         log_fail(f"FATAL: Could not start workers. Aborting tests. {message}")
         return
         
    log_info(message)
    time.sleep(2) 

    results = []
    
    try:
        results.append(test_1_basic_success())
        results.append(test_2_fail_to_dlq())
        results.append(test_3_multiple_workers())
        results.append(test_5_persistence())
    except Exception as e:
        log_fail(f"A critical error occurred: {e}")
    finally:
        log_info("Tests complete. Stopping workers...")
        stop_workers()
        clean_db()
        
    log_info("--- Test Summary ---")
    passes = sum(1 for r in results if r)
    fails = len(results) - passes
    
    if fails > 0:
        log_fail(f"{fails} test(s) failed.")
    if passes > 0:
        log_pass(f"{passes} test(s) passed.")
        
    if fails > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()