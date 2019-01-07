#! /usr/bin/env python3

import os
import sys
import argparse

from fuse import FUSE
from RpcFuse import Passthrough
from control import Controller

from threading import Thread

def t(controller):
    while(True):
        i = input("CMD: ")
        if(i[0:8] == "shutdown"):
            host = str(i).split('-')[1]
            controller.migrate(host)
        elif(i == "q"):
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Distributed file system client")
    parser.add_argument('-c','--control',required=True, help='Backup file location for control layer')
    parser.add_argument('-v','--virtual', required=True, help='Virtual mount point')
    parser.add_argument('-r','--real', required=True, help='Physical mount directory')
    parser.add_argument('-p','--port', required=True, help='Port for server endpoint')
    parser.add_argument('--hosts', required=True,nargs='+', help='List of hosts')
    parser.add_argument('--clear', required=False,type=int, help='Clear control backup file')

    args = parser.parse_args()
    
    if(args.clear == 1):
        # Remove control layer data
        try:
            os.remove(args.control)
        except:
            pass

    controller = Controller(args.control)
    
    hosts = []
    #hosts = [("172.17.0.2", 18861), ("172.17.0.3", 18861)]  # IP,PORT TUPLE
    for host in args.hosts:
        hosts.append((host,args.port))

    hasActiveHost = controller.generateNodes(hosts)
    if(not hasActiveHost):
        exit(0)


    k = Thread(target = t,args=(controller,))
    k.start()

    print(f"Mounting {args.real} on {args.virtual}")
    FUSE(Passthrough(controller,args.real), args.virtual, foreground=True,allow_other=True)
    k.join()
