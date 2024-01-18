#!/usr/bin/env python3

import argparse
import logging
import socket
from time import sleep

from zeroconf import IPVersion, ServiceInfo, Zeroconf

if __name__ == '__main__':

    hostname=str(socket.gethostname())
    IPAddress=socket.gethostbyname(hostname+".local")

    try:
        while True:   
            info = ServiceInfo(
                "_seamaze-timer._tcp.local.",
                "SeamazeTimer"+hostname+"._seamaze-timer._tcp.local.",
                addresses=[socket.inet_aton(IPAddress)],
                port=80,
                properties={'Version': '1.0', 'Nickname': 'Seamaze Timer 1'},
                server=hostname+".local."
            )

            zeroconf = Zeroconf(ip_version=IPVersion.All)
            print("Registration of a service, press Ctrl-C to exit...")
            zeroconf.register_service(info)     
            sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering...")
        zeroconf.unregister_service(info)
        zeroconf.close()