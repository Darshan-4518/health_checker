import os
import signal

with open("server_cpu_usage_process_id.pid","r") as file:
    pid = int(file.read())
    os.kill(pid,signal.SIGTERM)