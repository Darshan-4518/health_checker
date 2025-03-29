import subprocess
import sys


def get_battery_health_status(udid):

     health_status_flag = [None,"Unknown","Good","Overheat","Dead","Overvoltage","Failure","Cold"]

     connected_devices = subprocess.run("adb devices",text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)

     if udid not in connected_devices.stdout:
         print("Device is not connected")
         sys.exit(1)

     health_val = subprocess.run(f"adb -s {udid} shell dumpsys battery | grep -i  health",text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
     value =health_val.stdout.split(":")[1]

     return health_status_flag[int(value)]



print(get_battery_health_status("84b8979a"))