#! /usr/bin/env python3

import os
import sys

from fuse import FUSE, Operations, FuseOSError
from RpcFuse import Passthrough
from control import Controller

if __name__ == "__main__":
    controller = Controller()
    
    hosts = [("172.17.0.2", 18861), ("172.17.0.3", 18861)]  # IP,PORT TUPLE
    hasActiveHost = controller.generateNodes(hosts)
    if(not hasActiveHost):
        exit(0)

    if(len(sys.argv) >= 2):
        if(int(sys.argv[1]) == 1):
            # Remove control layer data
            try:
                os.remove("/home/berkay/backup.dat")
            except:
                pass
                
    mntPoint = "/home/berkay/client_virtual/"
    physicalMntPoint = "/home/berkay/client_real/"

    print(f"Mounting {physicalMntPoint} on {mntPoint}")
    FUSE(Passthrough(controller,physicalMntPoint), mntPoint, foreground=True, nothreads=True,allow_other=True)
    

