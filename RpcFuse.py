#! /usr/bin/env python3

from fuse import Operations
import os
import sys
import errno
import rpyc

from pathlib import Path

ROOT_DIR = "/home/berkay/client_real/"

class Passthrough(Operations):
    def __init__(self, controller):
        self.controller = controller

    def _full_path(self, partial):
        partial = partial.lstrip("/")
        path = os.path.join(ROOT_DIR, partial)
        return path

    # Directory methods
    # ==================

    def access(self, path, mode):
        print("FileSystem method: access\n")
        pass        

    def getattr(self, path, fh=None):
        #print("FileSystem method: getattr\n")
        
        if(path in self.controller.directories):
            full_path = self._full_path(path)
            st = os.lstat(full_path)
            return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                                                    'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
        try:
            dir = str(Path(path).parent)
            rpath = self.controller.files[path].rpath
            print("VIRTUAL PATH: ",path)
            print("REAL PATH: ",rpath)
            return self.controller.nextServer.getConnection().root.getattr(rpath,fh)
        except:
            full_path = self._full_path(path)
            st = os.lstat(full_path)
            return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                                                    'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        #print("FileSystem method: readdir\n")

        if path in self.controller.directories:
        
            fileList = []

            for node in self.controller.nodes:
                serverFileList = list(self.controller.nodes[node].getConnection().root.readdir("./",fh))
                for rpath in serverFileList:
                    file = self.controller.getFileFromReal(rpath)
                    if(file is not None):
                        if(file.directory == path):
                            fileList.append(str(Path(file.vpath).name))
                        
                
            # Add Directories
            if(path == "/"):
                for dir in self.controller.directories:
                    if(dir == "/"):
                        continue
                    fileList.append(dir[1:])

            if(len(fileList) > 0):
                for r in fileList:
                    yield r
            
    def readlink(self, path):
        print("FileSystem method: readlink\n")
        pathname = os.readlink(path)
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, ROOT_DIR)
        else:
            return pathname

    def rmdir(self, path):
        self.controller.removeDirectory(path)
        os.rmdir(self._full_path(path))

    def mkdir(self, path, mode):
        # Directories only exist in control layer
        # Server uses flat namespace eg: /data_store/file123
        self.controller.recordDirectory(path)
        return os.mkdir(self._full_path(path),mode)

    def unlink(self, path): # File remove
        print("FileSystem method: unlink\n")
        self.controller.removeFile(path)


    # File methods
    # ============

    def open(self, path, flags):
        print("File method: open\n")
        #Convert virtual path to real path
        fileRecord = self.controller.files[path]
        node = self.controller.getNode(fileRecord.nodeAddress)
        return node.getConnection().root.open(fileRecord.rpath,flags)

    def create(self, path, mode, fi=None):
        print("File method: create\n")
        fileRecord = self.controller.recordFile(path)
        return self.controller.nextServer.getConnection().root.create(fileRecord.rpath,mode,fi)

    def read(self, path, length, offset, fh):
        print("File method: read\n")
        fileRecord = self.controller.files[path]
        node = self.controller.getNode(fileRecord.nodeAddress)
        return node.getConnection().root.read(fileRecord.rpath, length,offset,fh)

    def write(self, path, buf, offset, fh):
        print("File method: write\n")
        fileRecord = self.controller.files[path]
        node = self.controller.getNode(fileRecord.nodeAddress)
        return node.getConnection().root.write(fileRecord.rpath, buf,offset,fh)

    def truncate(self, path, length, fh=None):
        print("File method: truncate\n")
        fileRecord = self.controller.files[path]
        node = self.controller.getNode(fileRecord.nodeAddress)
        node.getConnection().root.truncate(fileRecord.rpath,length,fh)

    def flush(self, path, fh):
        print("File method: flush\n")
        rpath = self.controller.files[path].rpath
        return self.controller.nextServer.getConnection().root.flush(rpath, fh)

    def release(self, path, fh):
        print("File method: release\n")
        fileRecord = self.controller.files[path]
        node = self.controller.getNode(fileRecord.nodeAddress)
        return node.getConnection().root.release(fileRecord.rpath,fh)

    def fsync(self, path, fdatasync, fh):
        print("File method: fsync\n")
        fileRecord = self.controller.files[path]
        node = self.controller.getNode(fileRecord.nodeAddress)
        return node.getConnection().root.fsync(fileRecord.rpath,fdatasync,fh)