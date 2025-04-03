import csv
import sys
from datetime import datetime
from psutil import cpu_percent,virtual_memory,disk_usage

def convert_into_gb(bytes):
    constant1 = 1024 ** 3
    constant2 = 1.07374

    return (bytes/constant1) * constant2


def server_monitor_data(interval):
    cpu_usage = cpu_percent(interval)
    ram_usage = virtual_memory()[2]
    server_storage =  disk_usage('/')
    total = convert_into_gb(server_storage.total)
    free = convert_into_gb(server_storage.free)
    server_health_data = {
        "cpu":f"{cpu_usage}%",
        "ram":f"{ram_usage}%",
        "storage":f"{free}/{total}"
    }

    return server_health_data

if __name__ == "__main__":
   server_monitor_data(1)
