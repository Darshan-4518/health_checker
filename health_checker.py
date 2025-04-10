import os
import signal
import subprocess
import json
import socket
import sys
from datetime import datetime,date
from psutil import cpu_percent,virtual_memory,disk_usage,process_iter
#device health related methods

#--android

android_device_status = dict()

def get_battery_health_status(udid):
    health_status_flag = [None, "Unknown", "Good", "Overheat", "Dead", "Overvoltage", "Failure", "Cold"]

    health_val = subprocess.run("adb -s "+ udid + " shell dumpsys battery | grep -i health | awk 'NR==1 {print $2}'""", text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    status = int(health_val.stdout)
    return health_status_flag[status]


def get_available_android_devices():
    device_cmd = subprocess.run("adb devices", text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)

    output_of_device_cmd = device_cmd.stdout

    index = output_of_device_cmd.find("\n") + 1

    current_status = dict()

    while index < len(output_of_device_cmd):
        line_end_index = output_of_device_cmd.find("\n", index)

        line = output_of_device_cmd[index:line_end_index]

        split_line = line.split("\t")

        if len(split_line) == 2:
            udid, status = split_line
            device_data = dict()
            if status == 'device':
                device_data['status'] = "Up"
                device_data['battery_health'] = get_battery_health_status(udid)
            else:
                device_data['status'] = f"Down({status})"
                device_data['battery_health'] = None

            current_status[udid] = device_data

        index = line_end_index + 1

    return current_status

def android_device_health():
    current_status = get_available_android_devices()

    device_status_keys = set(android_device_status.keys())
    current_status_keys = set(current_status.keys())
    for udid in current_status:
        if udid in device_status_keys:
            android_device_status[udid]['status'] = current_status[udid]['status']
            if current_status[udid]['battery_health']:
                android_device_status[udid]['battery_health'] = current_status[udid]['battery_health']
        else:
            android_device_status[udid] = current_status[udid]

    for offline_udid in (device_status_keys - current_status_keys):
        android_device_status[offline_udid]['status'] = "Down(disconnected)"

#--ios

ios_device_status = dict()

def get_connected_ios_devices():
    ios_devices_command = subprocess.run("idevice_id -l", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

    output = ios_devices_command.stdout

    udid_of_connected_devices = output.split("\n")

    current_ios_device_status = dict()

    for index in range(len(udid_of_connected_devices)-1):
        device_data = dict()
        device_data['status'] = 'Up'
        current_ios_device_status[udid_of_connected_devices[index]] = device_data

    return current_ios_device_status

def ios_device_health():
    current_ios_device_status = get_connected_ios_devices()

    current_ios_device_status_keys = set(current_ios_device_status.keys())
    ios_device_status_keys = set(ios_device_status.keys())

    for udid in current_ios_device_status_keys:
        ios_device_status[udid] = current_ios_device_status[udid]

    for udid in ios_device_status_keys - current_ios_device_status_keys:
        ios_device_status[udid] = "Down(offline)"



def marge_device_health_of_ios_android():
    both_device_health = dict()
    for key in android_device_status:
        both_device_health[key] = android_device_status[key]
    for key in ios_device_status:
        both_device_health[key] = ios_device_status[key]

    return both_device_health

#server health related methods

def convert_into_gb(bytes):
    constant1 = 1024 ** 3
    constant2 = 1.07374

    return (bytes/constant1) * constant2

def server_monitor_data():
    cpu_usage = cpu_percent(interval)
    ram_usage = virtual_memory()[2]
    server_storage =  disk_usage('/')
    total = convert_into_gb(server_storage.total)
    free = convert_into_gb(server_storage.free)
    server_health_data = {
        "cpu":f"{cpu_usage}%",
        "ram":f"{ram_usage}%",
        "storage":f"{free:.2f}/{total:.2f}"
    }

    return server_health_data


def machine_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname_ex(hostname)[2]
    ips = [ip for ip in ip_address if not ip.startswith("127")]
    return ips[0]


def run():
    history_data_file_name =  f"health_checker {date.today().strftime('%d-%m-%y')}.jsonl"
    while True:
        print("Checking health of devices and server...")
        server_health_data = server_monitor_data()
        android_device_health()
        ios_device_health()
        both_device_health = marge_device_health_of_ios_android()

        now = datetime.now()
        current_timestamp = now.strftime("%d-%m-%y %H:%M:%S")

        if now.hour == 0:
            history_data_file_path =  f"health_checker {date.today().strftime('%d-%m-%y')}.jsonl"


        main_data = {
            "local_machine_ip" : machine_ip(),
            "timestamp" : current_timestamp,
            "device_health" : both_device_health,
            "server_health" : server_health_data
        }

        with open(log_path + history_data_file_name,"a") as history_file , open(latest_data_file_path,"w") as latest_data_file:
            json.dump(main_data,history_file)
            json.dump(main_data,latest_data_file)
            history_file.write("\n")


def terminate_previous_run():
    current_time = datetime.now().strftime("%d-%m-%y %H:%M:%S")
    if os.path.exists(process_id_file_path):
        with open(process_id_file_path,"r") as pid_file:
            # os.path.exists(file_path) and os.rename(file_path,f"{directory_path}/health_checker_{current_time}.jsonl")
            pid = int(pid_file.read())
            is_process_running(pid) and os.kill(pid, signal.SIGTERM)


def is_process_running(pid):
    for process in process_iter(['pid']):
        if process.info['pid'] == pid :
            return True

    return False


if __name__ == "__main__" :
    arguments = sys.argv
    server_path = arguments[1]
    health_checker_directory_path = "/callshellscript/python_scripts/health_checker/"
    full_path = server_path + health_checker_directory_path

    log_path = full_path + "log/"

    if not os.path.exists(log_path):
        os.mkdir(log_path)

    process_id_file_path = log_path + "health_checker_pid.pid"
    latest_data_file_path = f"{log_path}health_checker.json"
    terminate_previous_run()


    with open(process_id_file_path,"w") as file:
            file.write(str(os.getpid()))
    
    interval = 10
    if len(arguments) > 2:
        interval = int(arguments[1])
    run()