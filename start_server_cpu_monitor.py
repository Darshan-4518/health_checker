import subprocess
import sys

interval = int(sys.argv[1])
subprocess.Popen(f"python server_cpu_usage.py {interval}",shell=True)

