#!/usr/bin/env python3

""" Example of announcing a service (in this case, a fake HTTP server) """

import argparse
import logging
import socket
from time import sleep

from zeroconf import IPVersion, ServiceInfo, Zeroconf

if __name__ == '__main__':

    hostname=str(socket.gethostname())
    IPAddress=socket.gethostbyname(hostname+".local")

    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument('--v6', action='store_true')
    version_group.add_argument('--v6-only', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)
    if args.v6:
        ip_version = IPVersion.All
    elif args.v6_only:
        ip_version = IPVersion.V6Only
    else:
        ip_version = IPVersion.V4Only
    '''
    properties = {}
    info = ServiceInfo(
        "_seamaze-timer._tcp.local.",
        "SeamazeTimer"+hostname+"._seamaze-timer._tcp.local.",
        addresses=[socket.inet_aton(IPAddress)],
        port=80,
        properties={'version': '1.0'},
        server=hostname+".local."
    )
    '''
    info = ServiceInfo(
        "Seamaze_"+hostname+"._tcp.local.",
        "_seamaze_timer._tcp.local.",
        addresses=[socket.inet_aton(IPAddress)],
        port=80,
    )
    '''

    zeroconf = Zeroconf(ip_version=IPVersion.All)
    print("Registration of a service, press Ctrl-C to exit...")
    zeroconf.register_service(info)
    
    try:
        while True:        
            sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering...")
        zeroconf.unregister_service(info)
        zeroconf.close()