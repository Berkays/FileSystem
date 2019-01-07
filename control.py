import shutil
import socket
import os.path
from pathlib import Path

import hashlib
import rpyc
import pickle

CONTROL_DATA = "/home/berkay/backup.dat"


class Node():
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.active = False

        self.test_connection()

    def test_connection(self):
        status = True  # Get server status
        try:
            print(f"Testing connection on {self.address}")
            self.conn = rpyc.connect(host=self.address, port=self.port)
            status = self.conn.root.connection_test()
        except:
            status = False

        if(status):
            self.active = True
            print(f"Connection succesful on {self.address}")
        else:
            print(f"Connection failed on {self.address}")
            self.active = False

    def getConnection(self):
        #return rpyc.connect(host=self.address, port=self.port)
        return self.conn

    def shutdown(self):
        self.active = False
        self.conn.close()

class Directory(object):
    def __init__(self,name):
        self.name = name # Directory name
        self.files = [] # Files in this directory

class File(object):
    def __init__(self, virtualPath,node):
        self.nodeAddress = node.address # Associated node ip
        self.vpath = virtualPath
        self.directory = str(Path(virtualPath).parent)
        self.calculatePhysicalPath(virtualPath)

    def calculatePhysicalPath(self,virtualPath):
        self.rpath = hashlib.md5(virtualPath.encode()).hexdigest()

class Controller(object):
    def __init__(self):
        self.nodes = {}
        self.nextServer = None
        
        self.directories = {}
        self.files = {}
        
        self.load_commit()
        for i in self.directories:
            print(i)

        self.recordDirectory("/") # Root directory

    # Generate node list
    def generateNodes(self,hosts):
        for host in hosts:
            ip, port = host
            node = Node(ip,port)
            if(node.active):
                self.nodes[ip] = node
        
        if(len(self.nodes) > 0):
            self.nextServer = next(iter(self.nodes.values()))
            return True
        else:
            print("No active servers found")
            return False

    # Get node object by ip address
    def getNode(self,address):
        if(address in self.nodes):
            return self.nodes[address]

    # Decide server for next file
    def decideNextServer(self):
        for node in self.nodes:
            if(node != self.nextServer.address):
                if(self.nodes[node].active == True):
                    self.nextServer = self.nodes[node]
                    break

    # Get file directory from its virtual path
    def getFileDirectory(self,virtualPath):
        return str(Path(virtualPath).parent)

    # Get File record from physical path
    def getFileFromReal(self,realPath):
        for file in self.files:
            if(self.files[file].rpath == realPath):
                return self.files[file]
        return None

    # Record new directory
    def recordDirectory(self,dirName):
        if(dirName in self.directories):
            return

        self.directories[dirName] = Directory(dirName)
        print(f"Directory {dirName} recorded.")

        self.commit()

    # Remove directory from records
    def removeDirectory(self,virtualPath):
        if(virtualPath in self.directories):
            for file in self.directories[virtualPath].files:
                self.removeFile(file)

            del self.directories[virtualPath]

            print(f"Directory {virtualPath} removed.")

            self.commit()

    # Record a new file
    def recordFile(self,virtualPath):
        fileDirectory = self.getFileDirectory(virtualPath)

        self.decideNextServer() # Decide node to write
        file = File(virtualPath,self.nextServer)
        self.directories[fileDirectory].files.append(virtualPath)
        self.files[virtualPath] = file

        self.commit()

        print(f"File {virtualPath} recorded on server {self.nextServer.address}.")
        return file

    # Remove file and unregister record
    def removeFile(self, virtualPath):
        fileDirectory = self.getFileDirectory(virtualPath)

        self.directories[fileDirectory].files.remove(virtualPath)

        file = self.files[virtualPath]
        node = self.nodes[file.nodeAddress]
        node.getConnection().root.unlink(file.rpath)

        self.commit()
        print(f"File {virtualPath} removed from server {node.address}.")

    # Node migration
    def migrate(self,host):
        # Select new host
        newHost = host
        
        for node in self.nodes:
            if(host != node):
                newHost = node
                break

        if(newHost == host):
            print("No eligible hosts found for migration.")
            return
        
        # Send new host ip
        self.nodes[host].getConnection().root.migrate(newHost)
        
        for f in self.files:
            fileRecord = self.files[f]
            if(fileRecord.nodeAddress == host):
                fileRecord.nodeAddress = newHost
                
        self.nodes[host].shutdown()
        del self.nodes[host]
        print("Migration completed")

    # Load file hiearchy from backup
    def load_commit(self):
        if(os.path.isfile(CONTROL_DATA) == False):
            return
        data_file = open(CONTROL_DATA,mode='rb')
        (self.directories,self.files) = pickle.load(data_file)
        data_file.close()

    # Save file hiearchy
    def commit(self):
        data_file = open(CONTROL_DATA,mode='wb')
        pickle.dump((self.directories,self.files),data_file)
        data_file.close()
