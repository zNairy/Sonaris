from argparse import ArgumentParser

def createSetupParser():
    parser = ArgumentParser(description='Simple multiclient Backdoor!')
    
    parser.add_argument('-a', '--address',  dest='address',
                        help='Endereço do servidor.', default='127.0.0.1')
    parser.add_argument('-p', '--port', dest='port', default=5000,
                        help='Porta do servidor.')

    return parser, parser.parse_args()