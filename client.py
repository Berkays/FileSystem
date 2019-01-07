#! /usr/bin/env python3

import os
import sys

from fuse import FUSE
from RpcFuse import Passthrough
from control import Controller

from threading import Thread

def t(controller):
    while(True):
        i = input("CMD: ")
        if(i[0:7] == "migrate"):
            host = str(i).split('-')[1]
            controller.migrate(host)

if __name__ == "__main__":
    if(len(sys.argv) >= 2):
        if(int(sys.argv[1]) == 1):
            # Remove control layer data
            try:
                os.remove("/home/berkay/backup.dat")
            except:
                pass

    controller = Controller()
    
    hosts = [("172.17.0.2", 18861), ("172.17.0.3", 18861)]  # IP,PORT TUPLE
    hasActiveHost = controller.generateNodes(hosts)
    if(not hasActiveHost):
        #exit(0)
        pass

    mntPoint = "/home/berkay/client_virtual/"
    physicalMntPoint = "/home/berkay/client_real/"

    k = Thread(target = t,args=(controller,))
    k.start()

    print(f"Mounting {physicalMntPoint} on {mntPoint}")
    FUSE(Passthrough(controller,physicalMntPoint), mntPoint, foreground=True,allow_other=True)
    k.join()