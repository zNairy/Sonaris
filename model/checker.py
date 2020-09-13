# coding: utf-8

import win32api
import win32con
from getpass import getuser

def main():
    try:
        user = getuser()
        hkey = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, f"Software\\Microsoft\\Windows\\CurrentVersion")
        win32api.RegSetValue(hkey, "RunOnce", win32con.REG_SZ, f"")
        hkey.close()
        hkey = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, f"Software\\Microsoft\\Windows\\CurrentVersion")
        win32api.RegSetValue(hkey, "Run", win32con.REG_SZ, f"")
        hkey.close()
    except Exception:
        pass

if __name__ == '__main__':
    main()