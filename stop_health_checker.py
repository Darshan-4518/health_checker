import os
import signal

with open("health_checker_pid.pid","r") as file:
    pid = int(file.read())
    os.kill(pid,signal.SIGTERM)