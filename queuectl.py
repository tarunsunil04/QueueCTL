# queuectl.py
import click
import uuid
import datetime
import os
import sys
import shlex  # This is the key to handling quoted commands
from db import get_db, ensure_indexes
from config import get_config, set_config_value
from worker_manager import start_workers, stop_workers # Import our new functions

# --- Main CLI Group ---
# We use 'context_settings' to make --help work in the shell
@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def cli():
    """
    queuectl: A CLI-based background job queue system.
    
    Type a command and press Enter.
    Type 'exit' to quit the shell.
    """
    pass

# --- Enqueue Command (New User-Friendly Version) ---

@cli.command()
@click.argument('job_id', type=str)
@click.argument('command', nargs=-1) # This takes all remaining arguments
def enqueue(job_id, command):
    """
    Add a new job to the queue.
    
    JOB_ID: A unique ID for the job (e.g., job1)
    COMMAND: The command to run (e.g., sleep 5 && echo hello)
    
    Example:
    enqueue my-job "sleep 5 && echo 'hello world'"
    """
    try:
        db, jobs_collection, _ = get_db()
        if db is None:
            click.echo("❌ Error: Could not connect to DB.", err=True)
            return
            
        ensure_indexes()
            
        if not command:
            click.echo("❌ Error: COMMAND cannot be empty.", err=True)
            return

        # Join the tuple of command parts back into a single string
        full_command = " ".join(command)
        
        config = get_config()
        now = datetime.datetime.utcnow()
        
        job = {
            "id": job_id,
            "command": full_command,
            "state": "pending",
            "attempts": 0,
            "max_retries": config["max_retries"],
            "created_at": now,
            "updated_at": now,
            "run_at": now,
        }
        
        jobs_collection.insert_one(job)
        click.echo(f"✅ Job enqueued with ID: {job_id}")
        
    except Exception as e:
        if "E11000" in str(e):
            click.echo(f"❌ Error: A job with ID '{job_id}' already exists.", err=True)
        else:
            click.echo(f"❌ Error adding job: {e}", err=True)


# --- Worker Command Group (Refactored) ---

@cli.group()
def worker():
    """Manage worker processes."""
    pass

@worker.command()
@click.option('--count', default=1, type=int, help="Number of workers to start.")
def start(count):
    """Start one or more worker processes in the background."""
    success, message = start_workers(count)
    click.echo(message)

@worker.command()
def stop():
    """Stop all running worker processes gracefully."""
    success, message = stop_workers()
    click.echo(message)


# --- Status Command (Unchanged) ---

@cli.command()
def status():
    """Show summary of all job states & active workers."""
    try:
        db, jobs_collection, dlq_collection = get_db()
        if db is None:
            click.echo("❌ Error: Could not connect to DB.", err=True)
            return

        pending = jobs_collection.count_documents({"state": "pending"})
        processing = jobs_collection.count_documents({"state": "processing"})
        completed = jobs_collection.count_documents({"state": "completed"})
        dead = dlq_collection.count_documents({})
        
        click.echo("--- Job Queue Status ---")
        click.echo(f"Pending:    {pending}")
        click.echo(f"Processing: {processing}")
        click.echo(f"Completed:  {completed}")
        click.echo(f"Dead (DLQ): {dead}")
        
        click.echo("\n--- Worker Status ---")
        if os.path.exists(".queuectl.pids"):
            try:
                with open(".queuectl.pids", 'r') as f:
                    pids = f.read().splitlines()
                click.echo(f"Running: {len(pids)} worker(s)")
                for pid in pids:
                    click.echo(f"  - PID: {pid}")
            except Exception:
                click.echo("Error reading PID file.")
        else:
            click.echo("Stopped")
            
    except Exception as e:
        click.echo(f"❌ Error getting status: {e}", err=True)


# --- List Command (Unchanged) ---

@cli.command()
@click.option('--state', type=click.Choice(['pending', 'processing', 'completed'], case_sensitive=False), help="Filter jobs by state.")
def list(state):
    """List jobs, optionally filtered by state."""
    try:
        db, jobs_collection, _ = get_db()
        if db is None:
            click.echo("❌ Error: Could not connect to DB.", err=True)
            return

        query = {}
        if state:
            query = {"state": state}
            click.echo(f"--- Showing '{state}' jobs ---")
        else:
            click.echo("--- Showing all jobs ---")

        for job in jobs_collection.find(query).sort("created_at", -1).limit(50):
            click.echo(f"- ID: {job['id']}")
            click.echo(f"  Cmd: {job['command']}")
            click.echo(f"  State: {job['state']} (Attempts: {job['attempts']})")
            click.echo(f"  Updated: {job['updated_at']}")
            if job.get('last_error'):
                click.echo(f"  Error: {job['last_error'][:100]}...")
    except Exception as e:
        click.echo(f"❌ Error listing jobs: {e}", err=True)


# --- DLQ Command Group (Unchanged) ---

@cli.group()
def dlq():
    """View or retry jobs in the Dead Letter Queue."""
    pass

@dlq.command(name="list")
def dlq_list():
    """List all jobs in the DLQ."""
    try:
        db, _, dlq_collection = get_db()
        if db is None:
            click.echo("❌ Error: Could not connect to DB.", err=True)
            return

        click.echo("--- Jobs in Dead Letter Queue (DLQ) ---")
        count = dlq_collection.count_documents({})
        if count == 0:
            click.echo("DLQ is empty.")
            return

        for job in dlq_collection.find().sort("updated_at", -1).limit(50):
            click.echo(f"- ID: {job['id']}")
            click.echo(f"  Cmd: {job['command']}")
            click.echo(f"  Last Error: {job.get('last_error', 'N/A')}")
            click.echo(f"  Failed At: {job['updated_at']}")
    except Exception as e:
        click.echo(f"❌ Error listing DLQ: {e}", err=True)

@dlq.command()
@click.argument('job_id')
def retry(job_id):
    """Move a job from the DLQ back to the 'pending' queue."""
    try:
        db, jobs_collection, dlq_collection = get_db()
        if db is None:
            click.echo("❌ Error: Could not connect to DB.", err=True)
            return
            
        job = dlq_collection.find_one({"id": job_id})
        
        if not job:
            click.echo(f"❌ Job {job_id} not found in DLQ.", err=True)
            return

        job["state"] = "pending"
        job["attempts"] = 0
        job["updated_at"] = datetime.datetime.utcnow()
        job["run_at"] = datetime.datetime.utcnow()
        if "last_error" in job:
            del job["last_error"]
        
        jobs_collection.insert_one(job)
        dlq_collection.delete_one({"id": job_id})
        
        click.echo(f"✅ Job {job_id} moved from DLQ to 'pending' queue.")
        
    except Exception as e:
        if "E11000" in str(e):
             click.echo(f"❌ Error: Job {job_id} already exists in the main 'jobs' queue.", err=True)
        else:
            click.echo(f"❌ Error retrying job: {e}", err=True)


# --- Config Command Group (Unchanged) ---

@cli.group()
def config():
    """Manage configuration."""
    pass

@config.command(name="set")
@click.argument('key')
@click.argument('value')
def config_set(key, value):
    """Set a config value (e.g., max_retries, backoff_base)."""
    try:
        set_config_value(key, value)
    except (KeyError, ValueError) as e:
        click.echo(f"❌ Error: {e}", err=True)

@config.command(name="show")
def config_show():
    """Show the current configuration."""
    click.echo(f"--- Current Configuration (.queuectl_config.json) ---")
    config = get_config()
    click.echo(json.dumps(config, indent=2))


# --- The Interactive REPL (Read-Eval-Print Loop) ---
def main_loop():
    """Runs the main interactive shell."""
    click.echo("Welcome to queuectl! Type 'help' or '-h' for commands.")
    
    while True:
        try:
            command_line = input("queuectl > ")
            
            if command_line.strip() == "exit":
                click.echo("Attempting graceful shutdown of workers...")
                success, message = stop_workers()
                click.echo(message)
                click.echo("Exiting.")
                break
                
            if command_line.strip() == "":
                continue
            
            # Use shlex.split to handle quotes, e.g.
            # enqueue job1 "sleep 5 && echo hello"
            args = shlex.split(command_line)
            
            # We call click's main function, but tell it
            # not to exit the whole program when it's done.
            cli.main(args, standalone_mode=False)
            
        except SystemExit:
            # click.main() raises this on --help or errors.
            # We catch it to keep the shell alive.
            pass
        except EOFError:
            # User pressed Ctrl+D
            click.echo("\nExiting...")
            break
        except Exception as e:
            # Catch other errors like shlex parsing
            click.echo(f"❌ Unhandled shell error: {e}", err=True)

if __name__ == "__main__":
    # Check if command-line arguments were passed (e.g., 'worker start')
    if len(sys.argv) > 1:
        # If args exist, run in non-interactive, standalone mode.
        # Click will automatically parse sys.argv.
        cli.main()
    else:
        # If no args (just 'python queuectl.py'), run the interactive shell.
        main_loop()