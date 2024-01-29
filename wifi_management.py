import os
import time


def list_wifi_networks():
    scan_results = os.popen("nmcli dev wifi list").read()
    scan_results.splitlines()
    scan_results.pop(0)
    for result in scan_results:
        result.split(' ')
        try:
            while true:
                result.pop(' ')
        except Exception as e:
            print (e)
            pass
    return scan_results

    

scan_results = list_wifi_networks()
time.sleep(5)

print(scan_results)
