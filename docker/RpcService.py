#! /usr/bin/env python3

import os
import sys
import rpyc
import socket
import shutil

from pathlib import Path

ROOT_DIR = "/server/data_store/"

class RpcService(rpyc.Service):
    active = True

    def __init__(self):
        self.root = ROOT_DIR

    def connection_test(self):
        return self.active

    def _full_path(self, partial):
        partial = partial.lstrip("/")
        path = os.path.join(self.root, partial)
        return path

    def readdir(self, path, fh):
        path = str(Path(ROOT_DIR))

        for r in os.listdir(path):
            yield r

    def getattr(self, path, fh=None):
        #print("FileSystem method: getattr\n")
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def unlink(self, path):  # File remove
        print(f"Remove: {path}\n")
        return os.unlink(self._full_path(path))

    # File methods
    # ============

    def open(self, path, flags):
        print(f"Open: {path}\n")
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        print(f"Create: {path}\n")
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        print(f"Read: {path}\n")
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        print(f"Write: {path}\n")
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        print(f"Truncate: {path}\n")
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        print(f"Flush: {path}\n")
        return os.fsync(fh)

    def release(self, path, fh):
        print(f"Release: {path}\n")
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        print(f"Fsync: {path}\n")
        return self.flush(path, fh)

    def migrate(self,toHost):
        zipFile = "/server/data_store/backup"
        print("Packing migration data...")
        shutil.make_archive(zipFile, 'zip', ROOT_DIR)  # Zip server files

        print("Sending migration data...")
        with open(zipFile + ".zip", 'rb') as f:
            data = f.read()
            rpyc.connect(host=toHost,port=18861).root.acceptMigrate(data)

        os.remove(self._full_path("backup.zip"))
        print("Migration complete...")

    def acceptMigrate(self,data):
        zipFile = "/server/data_store/backup.zip"

        print("Receiving migration data...")
        f = open(zipFile,'wb')
        f.write(data)
        f.close()

        print("Unpacking migration data...")
        shutil.unpack_archive(zipFile, extract_dir=ROOT_DIR)

        os.remove(self._full_path("backup.zip"))
        print("Migration complete...")

    def shutdown(self):
        print("Shuttind down...")
        self.active = False
        exit(0)
