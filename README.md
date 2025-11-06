# QueueCTL

     .:.       .*@%=.          *@@%:                       :--:                                                       :=*-                     
   .%@@@@+     %@@@@#         @@@@@*                      @@@@@%.        :#%#=          #@@@:          :==.         .@@@@@:       :**:         
   :@@@@@:    :@@@@@%         =@@@@@.       :*%%-         *@@@@@:       #@@@@@%.       @@@@@*        .%@@@@.        :@@@@@-      *@@@@#          
   .%@@@@:   .%@@@@+:        .=@@@%*       #@@@@@:        *@@@@%        @@@@@@-        +@@@@@.      :#@@@@@:        -@@@@@.     :@@@@@@.       
 .*@@@@=     *@@@@@#       *@@@@@@@=        %@@@@+       *@@@@=       :@@@@@@          -@@@*:       @%=@@@@        %@@@@@:      =@@@@#-        
:@@@@@@=     #@@@@@%      %@@@@@@@@@@.       *@@=-:     #@@@@@*      #@@@@@*        .@@@@@@@@@-    :*@@@@@%:      =@@@@@@- :    #@@@@%.        
#@@@@@@*    :@@@@@@@@    -@@@@@@@@@@@+     +@@@@@@%    :@@@@@@@-    :@@@@@@@-       +@@@@@@@@@@   -@@@@@@@@@:     %@@@@@@@: :   %@@@@@@        
%@@@@@@@.   %@=@@@@@*    %@@@@@@@@@@@%     @@@@@@@@%   %@@@@@@@%    :@@@@@@@*       -@@@@@@@@@@*  =@@@@@@@@@:     %@@@@@@@%*@= :@@@@@@@*       
@@@@@@@@:  *@* *@@@@=    #@@@@@@@@@@@@     #@@@@@@@    %@@@@@@@@    .@@@@@@@@  =*   =@@@@@@@@@@@  =@@@@@@@@@=     %@@@@@@@@@*  :#@@@@@@@-      
*@@@@@@@+   :*@@@@@@%    %@*@@@@@@@@@@     +@@@@@@-    @@@@@@@@@=    @@@@@@@@@@@*  .#=@@@@@@@@@%. =@=@@@@@@#      %@@@@@@@@:     =@@@@@@@%*-   
=@@@@@@@#     *@@@@@@    :@@@@@@@@@@@@=   ::*@@@@@     =@@@@@@@@+    =@@@@@@@%     #@@@@@@@@@@.   +@-%@@@@@@:     %@@@@@@@@+     =@@@@@%@@@@@+ 
:@@@@@@@=     *@@@@@@     =@@@@@@@@@-@*  .@@@@@@@@*     *@@@@@@@=    .@@@@@@@@    #@@@@@@@@@@@.   .@%@@@@@@@*     @@@@@@@@@#    .@@@@@@@@@@@@% 
#@@@@@@@       %@@@@@%     %@@@@@@@@:%%  =@@@@@@@@#     @@@@@@@@=    %@@@@@@@@   -@@@@@@@@@@@@=    =@@@@@@@@#    :@@@@@@@@@%    =@@@@@@@@@@*.  
#@@@@@@@       *@@@@@@-    *@@@@@@@@:@@  =@@@@@@@@%     :@@@@@@@.    *@@@@@@@*    #@@@@@@@@@@@+     :@@@@@@@@=   -@@@@@@@@@@.   :@@@@@@@:      
.@@@@@@@       *@@@@@@%    .@@@@@@@@:#@.  .@@@@@@@@      @@@@@@@     .@@@@@@@%      ..@@@@@@@@+     .@@@@@@@@==   -@@@@@@@#      @@@@@@@=      
 #@@@@@%       +@@@*@@@     *@@@@@@@:.     #@@@@@@%      #@@@@@*     .@@@@@@@@       .@@@@@@@@+     .@@@@@@@@@@+  :@@@@@@@=     .%@@@@@@%      
 %@@@@@=       +@@# %@@*    *@@@@@@@.      *@@@@@@*      *@@@@@=      @@@@@@@@       .@@@@@@@@=      @@@@@@@@@@%  :@@@@@@@.       *@@@@@@.     
 @@@@@@:       *@@: =@@=    #@@@@@@@       %@@@@@@.      #@@@@@       @@@@@@@@       :@@@=@@@@:      %@@#%@@@@@@. .@@@@@@%        *@@=@@@=     
:@@@@@@:       @@@ :@@%    .@@@@@@@%       @@@+@@%      .@@@@@=      .@@@@@@@@       -@@@:%@@%       %@@*%@@@@@@: :@@@@@@+       .@@% *@@:     
=@@@@@@        %@@ #@@.    =@@#@@@:       #@@-:@@#      @@@@@=       =@@@@@@-.       %@@* %@@*       @@@%@@@@@@#. :@@@@@@:       :@@# -@@=     
*@@@@@@:       =@@.@@-     %@@+@@@       .@@@ =@@#      @@@@@:       *@@%@@@+        @@@- @@@+      .@@@@@@+      =@@@@@@:        %@#  @@@.    
*@@@@@@#       :@@=@%      %@# @@*       .@@=  @@%      @@@@@        :@@*.@@%        @@@:.@@@+      .@@@@@@+      *@@@@@@         -@#   @@=    
*@@@@@@@        @@@@.      #@: @@-       .@@%  *@@*     @@@@@         @@- +@@       .@@@=.@@@=      .@@@@@@=      =@@@@@=         :@%   .@@.   
=@@@@@@@:      %@@@@+      %@%:@@=.       %@+  :@@*     @@@@@.        +@@. @@@.     .@@@:.@@@=       @@@@@@+      -@@@@@:         *@@=  .@@%.  
=@@@@@@@@**.   =-@@@@-    *@@@@@@@@%=    .@@@+ .@@@%:  =@@@@@@+      .@@@@%@@@@@#=   #@@==@@@@:      =@@@@@@*:    :@@@@@@%:       #@@@% :@@@@= 
 ::::::..      . .:::.    .:::::::::.     ..:::.         :::::::.     ::..:::::::    .::: ::::::      .::::::.      .::.:::.      ...::. ..:::.

  
Done as part of **Backend Developer Internship Assignment** for FLAM.

A robust, CLI-based background job queue system built with Python, MongoDB, and Click.

This system manages background jobs using multiple worker processes, handles automatic retries with exponential backoff, and maintains a Dead Letter Queue (DLQ) for permanently failed jobs.

**Core Features**

-> Interactive CLI Shell: A user-friendly REPL to manage your queue.
-> Persistent Job Store: Jobs are stored in MongoDB and survive restarts.
-> Multi-Worker Processing: Run multiple workers in parallel to process jobs concurrently.
-> Atomic Operations: Workers use atomic find_and_lock operations to prevent job-stealing or duplicate processing.
-> Exponential Backoff: Failed jobs are automatically retried with an increasing delay.
-> Dead Letter Queue (DLQ): Jobs that fail all retries are moved to a DLQ for manual inspection.
-> Background Daemons: Workers run as background processes, managed by the CLI.

**Setup & prerequisites**
-> Python 3.10 or newer.
-> A running MongoDB instance.
-> Git for cloning the repository.

---> Download **git** [here](https://github.com/git-for-windows/git/releases/download/v2.51.2.windows.1/Git-2.51.2-64-bit.exe).
---> Download **MongoDB** [here](https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-8.2.1-signed.msi)

  1. Cloning the repo:
  
      `git clone <your-repository-url>
      cd <your-repository-name>`
  
  2. Installing the prereq's:
  
      `pip install -r requirements.txt`
  
  3. Configuring the environment (Optional):
  
      Create an env file (.env) in the root if you want to initialize the MongoDB server somewhere else. This is not necessary as `db.py` already does this locally. 
  
      `MONGO_URI="mongodb://<new-address-goes-here>/"`
  
  
  4. Running the tool:
  
      `python queuectl.py`
  
    NOTE : Single commands can also be run, and will be discussed towards the end.


**Usage & CLI Commands**

Run python queuectl.py to enter the interactive shell. All commands are typed into this prompt.

  1. Managing Workers:

      Managing the threads/workers/processes so to speak.

     Start workers:
      
      `# Start 3 workers in the background
      queuectl > worker start --count 3`
      
      
     Check worker status:
      
      `queuectl > status`
      
      
     Stop all running workers:
      
      `queuectl > worker stop`
  
  
  2. Enqueuing Jobs

      The enqueue command takes a unique Job ID and a Command to be executed.
      
      Note: The command must be wrapped in quotes if it contains spaces or shell operators.
      
      Simple Job:
      
        `queuectl > enqueue job1 "echo Hello World"`
      
      
      Windows Job (with timeout for sleep):
      
        `queuectl > enqueue job2 "timeout /t 5 /nobreak && echo Job 2 is done"`
      
      
      Linux/macOS Job (with sleep):
      
        `queuectl > enqueue job3 "sleep 5 && echo Job 3 is done"`
      
      
      A Job that will fail (for testing retries):
      
        `queuectl > enqueue job-fail "exit 1"`


  3. Checking Status & Listing Jobs

      Get a high-level summary:
      
        `queuectl > status`
      
          `--- Job Queue Status ---
          Pending:    1
          Processing: 2
          Completed:  5
          Dead (DLQ): 1
          
          --- Worker Status ---
          Running: 3 worker(s)
            - PID: 12345
            - PID: 24249
            - PID: 6034
          `
      
      List all active jobs:
      
        `queuectl > list`

     
      Filter jobs by state:
      
        `queuectl > list --state pending
        queuectl > list --state processing`

  4. Managing the Dead Letter Queue (DLQ)

      List all jobs that have permanently failed:
      
        `queuectl > dlq list`
      
      
      Retrying a job from the DLQ: This moves the job back to the main pending queue with its retry count reset.
      
        `queuectl > dlq retry <job-id>`
      
      
  5. Configuration
  
      Show the current config (from .queuectl_config.json):
      
        `queuectl > config show
        {
          "max_retries": 3,
          "backoff_base": 2
        }`
      
      
      Change a config value:
      
        `queuectl > config set max_retries 5`


**Testing Instructions**

  You can test the system using two methods:
  
  1. Manual Testing (User Input)
  
      This is the best way to see the system in action.
    
      Terminal 1 (Run the App):
  
        `python queuectl.py`
  
  
      Start Workers:
  
        `queuectl > worker start --count 2`
  
  
      Enqueue Jobs:
  
        Working job (Windows example)
     
        `queuectl > enqueue job-good "timeout /t 2 /nobreak && echo GOOD"`
  
        A job that fails

         `queuectl > enqueue job-bad "exit 1"`
  
  
      Check Status:

       Run `status` immediately. You'll see the jobs in processing.
  
          `queuectl > status`
  
  
      Observe Logs:
        Check the logs/ directory to see the real-time output from the workers.
  
      Check DLQ:
        After a few seconds, run status again. job-good will be completed, and job-bad will eventually move to the Dead (DLQ) count.
  
          `queuectl > dlq list`
  
  
      Stop:
  
          `queuectl > worker stop
          queuectl > exit`

  2. Automated Testing (Script-based)
  
     The project includes a full end-to-end integration test script, `tester.py`. This script does not use subprocess and instead imports your application's functions directly for robust, deadlock-free testing.
     Stop any running workers from your manual tests (worker stop).
      
     Run the test script:
      
       `python tester.py`
      
     The script will automatically do tthe following:
    
     -> Clear the database.
     -> Start and stop workers.
     -> Run tests for all required scenarios:
     -> Successful job completion.
     -> The full retry-to-DLQ pipeline.
     -> Parallel processing by multiple workers.
     -> Job data persistence across worker restarts.
     -> Print a final PASS or FAIL summary.


## Architecture Overview

**Core Components**

-> Interactive CLI (`queuectl.py`): The user-facing shell built with click. It parses user input and calls the appropriate functions. It uses shlex.split to correctly parse quoted commands.
-> Worker Manager (`worker_manager.py`): Handles the logic for starting (Process.start()) and stopping (os.kill) the background worker processes. It uses a .queuectl.pids file to track running workers.
-> Worker (`worker.py`): The "engine" of the system. Each worker runs in its own process and continuously polls the database for jobs. All worker output is redirected to log files in the logs/ directory.
-> Database (`db.py` & MongoDB): MongoDB serves as the persistent, single source of truth. All communication between the CLI and the workers happens via the database.

**Job Lifecycle**

-> Enqueue: A user runs enqueue job1 "...". The job is saved to the jobs collection with state: "pending".
-> Fetch & Lock: A free worker polls the database. It uses an atomic find_one_and_update operation to find a pending job (where run_at is in the past) and immediately set its state: "processing" and lock it with its worker_id. This prevents any other worker from grabbing the same job.
-> Execute: The worker runs the job's command using subprocess.run().
-> Success: If the command exits with code 0, the worker sets the job's state: "completed".
-> Failure & Retry: If the command fails:
----> The worker increments the attempts count.
----> It checks if attempts < max_retries.
----> If Yes (Retryable): It calculates the backoff delay (delay = base ^ attempts) and sets the job's run_at to a future timestamp. It then sets the state back to pending.
----> If No (Max Retries Hit): The job is moved from the jobs collection to the dlq collection.

**Assumptions, trade-offs and potenial improvements:**

-> Security (`shell=True`): Job commands are executed with shell=True. This is necessary to handle complex commands (like && or >), but it's a security risk if untrusted users can enqueue jobs. In this implementation, we assume the user is trusted.
-> Worker Management (PID File): The system uses a .queuectl.pids file to manage worker state. This is simple and effective but less robust than a true systemd or launchd service. If the queuectl app is force-killed, the PID file may become stale, this was a huge issue while debugging, as silent-exits and deadlocks start appearing.
-> Job "Stuck" State: If a worker process is killed (e.g., kill -9 or OS crash) while a job is in the processing state, that job will remain "stuck" in the processing state indefinitely. An optimization would be to add a "heartbeat" or "job lease" mechanism to detect and requeue these stale jobs.






