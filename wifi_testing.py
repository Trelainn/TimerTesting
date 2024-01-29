import wifimangement_linux as wifi 
import time

print(wifi.share("qr"))

wifi.off()
time.sleep(5)
wifi.on()

print(wifi.scan())
print(wifi.list())
