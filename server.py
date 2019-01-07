#! /usr/bin/env python3

from rpyc.utils.server import ThreadedServer
from RpcService import RpcService

if __name__ == "__main__":
    print("Starting server...")
    t = ThreadedServer(RpcService, port=18861, protocol_config={ 'allow_public_attrs': True, })
    t.start()
