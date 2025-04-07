import os
import subprocess
import json
import socket
import sys
from datetime import datetime
from psutil import cpu_percent,virtual_memory,disk_usage

android_device_status = dict()

#device health related methods

#--android
def get_battery_health_status(udid):
    health_status_flag = [None, "Unknown", "Good", "Overheat", "Dead", "Overvoltage", "Failure", "Cold"]

    health_val = subprocess.run(f"adb -s {udid} shell dumpsys battery | grep -i  health", text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    value = health_val.stdout.split(":")[1]

    return health_status_flag[int(value)]


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

def server_monitor_data(interval):
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


def run(interval=10):
    server_health_data = server_monitor_data(interval)
    android_device_health()
    ios_device_health()

    both_device_health = marge_device_health_of_ios_android()

    main_data = {
        "local_machine_ip" : machine_ip(),
        "timestamp" : datetime.now().strftime("%d-%m-%y %H:%M:%S"),
        "device_health" : both_device_health,
        "server_health" : server_health_data
    }

    with open("health_checker.jsonl","a") as file:
        json.dump(main_data,file)
        file.write("\n")

    run(interval)


if __name__ == "__main__" :
    with open("health_checker.jsonl","w"),open("health_checker_pid.pid","w") as file:
            file.write(str(os.getpid()))

    arguments = sys.argv

    if len(arguments) > 1:
        interval = int(arguments[1])
        run(interval)
    else:
        run()