import os
import time


def list_wifi_networks():
    return os.popen("nmcli dev wifi list").read()
    

scan_results = list_wifi_networks()
time.sleep(5)

print(scan_results.split(' '))
