import csv
import sys
from datetime import datetime
from psutil import cpu_percent,virtual_memory,disk_usage

def convert_into_gb(bytes):
    constant1 = 1024 ** 3
    constant2 = 1.07374

    return (bytes/constant1) * constant2

def write_in_csv(file_name,row_as_list,mode):
    with open(file_name,mode) as file:
        writer = csv.writer(file)
        writer.writerow(row_as_list)

def server_monitor_data(file_name,interval):
    cpu_usage = cpu_percent(interval)
    ram_usage = virtual_memory()[2]
    server_storage =  disk_usage('/')
    total = convert_into_gb(server_storage.total)
    free = convert_into_gb(server_storage.free)
    current_time = datetime.now().strftime("%d-%m-%y %H:%M:%S")
    row_as_list = [current_time, cpu_usage, ram_usage, f"{free:.2f}/{total:.2f}"]
    write_in_csv(file_name,row_as_list,mode="a")

    server_monitor_data(file_name,interval)

if __name__ == "__main__":
    header = ['time','cpu(%)','ram(%)','storage(free/total)']
    file_name = sys.argv[2]
    interval = int(sys.argv[1])
    write_in_csv(file_name,header,mode='w')
    server_monitor_data(file_name,interval)
