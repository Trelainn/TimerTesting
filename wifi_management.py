import os
import time


def list_wifi_networks():
    scan_results = os.popen("nmcli dev wifi list").read()
    scan_results = scan_results.splitlines()
    scan_results.pop(0)
    scan_return = []
    for result in scan_results:
        result = result.split(' ')
        print(result)
        print("\n")
        try:
            while 1:
                result.pop('')
        except Exception as e:
            print (e)
            pass
        scan_return.append(result)
    return scan_return

    

scan_results = list_wifi_networks()
time.sleep(5)

print(scan_results)
