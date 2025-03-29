import time
import psutil
import sys

def get_cpu_usage_ram(interval):
    print(f"Cpu RAM usage : {psutil.virtual_memory()[2]}%")
    time.sleep(interval)
    get_cpu_usage_ram(interval)

interval = int(sys.argv[1])
get_cpu_usage_ram(interval)