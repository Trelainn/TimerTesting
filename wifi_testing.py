import wifimangement_linux as wifi 
import time

wifi.off()
time.sleep(5)
wifi.on()

print(wifi.print_psk())