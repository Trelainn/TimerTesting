import os
import time


def list_wifi_networks():
    scan_results = os.popen("nmcli dev wifi list").read()
    scan_results = scan_results.splitlines()
    scan_results.pop(0)
    scan_return = []
    for result in scan_results:
        current = False
        result = result.split(' ')
        if result.pop(0) == '*':
            current = True
        try:
            while 1:
                result.remove('')
        except Exception as e:
            print (e)
            pass
        bssid = result[0:16]
        try:
            end = result.index('Ad-Hoc')
        except Exception as e:
            print(e)
        try:
            end = result.index('Infra')
        except:
            pass
        print(end)
        ssid = result[17]
        scan_return.append(result)
    return scan_return

    

scan_results = list_wifi_networks()
time.sleep(5)

print(scan_results)
