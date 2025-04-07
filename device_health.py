import csv
import json
import subprocess
import time
from datetime import datetime

device_status = dict()


def get_battery_health_status(udid):
    health_status_flag = [None, "Unknown", "Good", "Overheat", "Dead", "Overvoltage", "Failure", "Cold"]

    connected_devices = subprocess.run("adb devices", text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       shell=True)

    health_val = subprocess.run(f"adb -s {udid} shell dumpsys battery | grep -i  health", text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    value = health_val.stdout.split(":")[1]

    return health_status_flag[int(value)]


def get_available_devices():
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
            device_data['status'] = status
            device_data['battery_health'] = None
            if split_line[1] == 'device':
                device_data['battery_health'] = get_battery_health_status(udid)

            current_status[udid] = device_data

        index = line_end_index + 1

    return current_status


def write_in_csv(rows):
    with open("device_status.csv", "a") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(rows)
        writer.writerow([])


def device_availability_status(interval):
    # print("Checking Device Status.....")
    # current_status = get_available_devices()
    # current_status_key_set = set(current_status.keys())
    # device_status_key_set = set(android_device_status.keys())
    # for status in current_status_key_set:
    #     android_device_status[status] = current_status[status]
    # for new_device in (device_status_key_set - current_status_key_set):
    #     android_device_status[new_device] = "offline"
    #
    #
    # list_of_status = [[datetime.now().strftime("%d-%m-%y %H:%M:%S")],[],
    #                   ["no","udid","status","battery_health"]]
    #
    # no = 1
    # down_reason = ["unauthorized","offline"]
    # for udid in android_device_status:
    #     row = [no,udid]
    #     status = ""
    #     if android_device_status[udid] in down_reason:
    #         status = f"down({android_device_status[udid]})"
    #         battery_health = android_device_status['battery_health']
    #     else:
    #         status = "up"
    #         battery_health = get_battery_health_status(udid)
    #
    #     row.append(status)
    #     row.append(battery_health)
    #     list_of_status.append(row)
    #     no += 1
    #
    # write_in_csv(list_of_status)

    current_status = get_available_devices()

    device_status_keys = set(device_status.keys())
    current_status_keys = set(current_status.keys())
    for udid in current_status:
        if udid in device_status_keys:
            device_status[udid]['status'] = current_status[udid]['status']
            if current_status[udid]['battery_health']:
                device_status[udid]['status'] = current_status[udid]['status']
        else:
            device_status[udid] = current_status[udid]

    for offline_udid in (device_status_keys - current_status_keys):
        device_status[offline_udid]['status'] = "offline"

    with open("device_health.jsonl", "a") as file:
        json.dump(device_status, file)

    time.sleep(interval)

    device_availability_status(interval)


device_availability_status(10)


# print(get_available_devices())
# print(android_device_status)

# if __name__ == "__main__":
#     # with open("android_device_status.csv", "w"):
#     #     pass
#
#     device_availability_status(20)
