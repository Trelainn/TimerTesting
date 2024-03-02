#!/usr/bin/env python3

import socket
from time import sleep

from zeroconf import IPVersion, ServiceInfo, Zeroconf

class network_registration:

    def __init__(self):
        self.hostname=str(socket.gethostname())
        self.IPAddress=socket.gethostbyname(self.hostname+".local")
        self.info = ServiceInfo(
            "_seamaze-timer._tcp.local.",
            "Seamaze"+self.hostname+"._seamaze-timer._tcp.local.",
            addresses=[socket.inet_aton(self.IPAddress)],
            port=8080,
            properties={'Version': '1.0', 'Nickname': 'Seamaze Timer 1'},
            server=self.hostname+".local."
        )
        self.zeroconf = Zeroconf(ip_version=IPVersion.All)
        #print("Registration of a service, press Ctrl-C to exit...")
        

    def register(self):
        self.zeroconf.register_service(self.info)
        try:
            while True:
                sleep(0.1)
        except:
            pass
        finally:
            self.unregister()


    def unregister(self):
        #print("Unregistering...")
        self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()  
        #print("Finishing")