from socket import *
import time

sSock=socket(AF_INET,SOCK_STREAM)

sSock.connect(('irc.freenode.net',6667))
#sSock.settimeout(.700)
sSock.send('NICK m0nk-imme\n')
w=sSock.recv(1024)
sSock.send('USER m0nk-imme 8 * : m0nk-imme\n')
sSock.send('JOIN ##club-ubuntu\n')
w=sSock.recv(2048)

def recieve_messages():
  messages=[]
  try:
    data=sSock.recv(2048)
    data=data.split('\r\n')
  except:
    return messages
  for command in data:
    if len(command.split(' ')) >=2 and  command.split(' ')[1]=='PRIVMSG':
      user=command[1:command.find('!')]
      temp=command[1:]
      message=temp[temp.find(':')+1:]
      messages.append(user+': '+message)
    if command.split(' ')[0]=='PING':
      print 'ping'
      sSock.send('PONG :'+command.split(':')[1]+'\n')
  return messages

def send_message(text):
  if len(text)<80:
    sSock.send('PRIVMSG ##club-ubuntu :'+text+'\n')
