import os

def turn_on():
    os.system("nmcli radio wifi on")

def turn_off():
    os.system("nmcli radio wifi off")

def connect(ssid,password=""):
	if password=="":
		os.system(f"nmcli dev wifi connect {ssid}")
	else:
		os.system(f"nmcli dev wifi connect {ssid} password {password}")
          
def hotspot(ssid,password):
	os.system("nmcli dev wifi hotspot ssid {ssid} password {password}")

def list_wifi_networks():
    scan_results = os.popen("nmcli dev wifi list").read()
    return scan_results
    scan_results = scan_results.splitlines()
    if scan_results:
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
            #print (e)
            pass
        bssid = result[0]
        try:
            end = result.index('Ad-Hoc')
        except Exception as e:
            #print(e)
            pass
        try:
            end = result.index('Infra')
        except Exception as e:
            #print(e)
            pass
        ssid = " ".join(result[1:end])
        scan_return.append({"IN USE": current, "BSSID": bssid, "SSID": ssid})
    return scan_return