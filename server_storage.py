import shutil

def convert_gib_into_gb(gib_storage):
    return gib_storage*1.07374

def get_storage_info():
    disk_usage = shutil.disk_usage('/')
    # print(disk_usage)
    total = disk_usage.total / (1024 ** 3)
    # used = disk_usage.used / (1024 ** 3)
    free = disk_usage.free / (1024 ** 3)
    print(total,free)
    print(f"{convert_gib_into_gb(free):.2f}/{convert_gib_into_gb(total):.2f}")


get_storage_info()
