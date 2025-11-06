# worker_manager.py
import os
import signal
from multiprocessing import Process
from worker import start_worker
from config import get_config

PID_FILE = ".queuectl.pids"

def start_workers(count):
    if os.path.exists(PID_FILE):
        return False, "❌ Workers are already running. Use 'worker stop' first."

    config = get_config()
    backoff_base = config["backoff_base"]
    pids = []
    messages = []

    for _ in range(count):
        p = Process(target=start_worker, args=(backoff_base,))
        p.start()
        pids.append(p.pid)
        messages.append(f"   Started worker with PID: {p.pid}")
        
    try:
        with open(PID_FILE, 'w') as f:
            f.write("\n".join(map(str, pids)))
        messages.append(f"✅ All workers running. PID data stored in {PID_FILE}.")
        return True, "\n".join(messages)
    except Exception as e:
        messages.append(f"❌ Error writing PID file: {e}")
        messages.append("   Attempting to kill started processes...")
        for pid in pids:
            try: os.kill(pid, signal.SIGTERM)
            except: pass
        return False, "\n".join(messages)

def stop_workers():
    if not os.path.exists(PID_FILE):
        return True, "🤔 No workers seem to be running (PID file not found)."

    messages = ["Stopping all worker processes..."]
    try:
        with open(PID_FILE, 'r') as f:
            pids = [int(pid) for pid in f.read().splitlines()]
        
        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
                messages.append(f"   Sent SIGTERM to worker {pid}")
            except ProcessLookupError:
                messages.append(f"   Worker {pid} was already stopped.")
            except Exception as e:
                messages.append(f"   Error stopping worker {pid}: {e}")
        
        os.remove(PID_FILE)
        messages.append(f"✅ All workers stopped. Removed {PID_FILE}.")
        return True, "\n".join(messages)
    except Exception as e:
        return False, f"❌ Error stopping workers: {e}"