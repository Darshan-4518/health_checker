import os
import psutil
import sys


def get_cpu_usage(interval):
    cpu_usage = psutil.cpu_percent(interval=interval)
    print(f"Cpu Usage : {cpu_usage}%")
    get_cpu_usage(interval)


interval = int(sys.argv[1])
with open("server_cpu_usage_process_id.pid","w") as file:
    file.write(str(os.getpid()))
get_cpu_usage(interval)
