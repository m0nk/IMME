from imme import imme
import irc
import thread
import time


sent_messages=[]
connected=0

x=0

class irc_thread:
  irc_messages=[]
  def read_messages(self,name,number):
    while 1:
      self.irc_messages+= irc.recieve_messages()
      time.sleep(.025)

imme=imme()
imme.start_loops()

irc_thread=irc_thread()
thread.start_new_thread(irc_thread.read_messages,('name1',3))
  
while 1:
  for i in range(len(imme.messages)):
    message=imme.messages.pop(0)
    if message[0]=='NAME_REQ':
      imme.send_computer_name('IRC_TEST',[7,4,4,8])
    elif message[0]=='LOGIN_ATTEMPT':
      if message[1]['pass']==message[1]['user']:
        imme.allow_login(message[1]['msgid'],[1,2,3,4],message[1]['key'])
      else:
        imme.disallow_login(message[1]['msgid'],message[1]['key'],True)
    elif message[0]=='FRIEND_LIST_REQ':
       friends=[([4,5,3,6],'IRCtest')]
       imme.send_friend_list(message[1]['msgid'],message[1]['connection_id'],message[1]['contact_id'],friends)
       connected=1
       connection_id=message[1]['connection_id']
    elif message[0]=='LOGGED_IN_FRIENDS_REQ':
       imme.send_online_list(message[1]['msgid'],message[1]['connection_id'],message[1]['contact_id'],[4,5,3,6])
    elif message[0]=='MSG_IN':
       imme.acknowledge_message(message[1]['msgid'],message[1]['connection_id'],message[1]['contact_id'],message[1]['text_id'])
       irc.send_message(message[1]['text'])
    elif message[0]=='MSG_OUT_ACK':
      print message
    elif message[0]=='CONVO_END_REQ':
      mme.end_conversation(message[1]['msgid'],message[1]['connection_id'],message[1]['contact_id'],message[1]['text_id'])
    elif message[0]=='DISSCONNECT_REQ':
      imme.close_connection(message[1]['msgid'],message[1]['connection_id'],message[1]['contact_id'])

  for i in range(len(irc_thread.irc_messages)):
    if connected==1:
      irc_message=irc_thread.irc_messages.pop(0)
      if len(irc_message)<=80:
        imme.send_message(connection_id,[1,2,3,4],[4,5,3,6],irc_message)
      else:
        for i in range(len(irc_message)/80):
          imme.send_message(connection_id,[1,2,3,4],[4,5,3,6],irc_message)
          irc_message=irc_message[80:]
        if irc_message:
          imme.send_message(connection_id,[1,2,3,4],[4,5,3,6],irc_message)
    else:
      irc_thread.irc_messages=[]
  time.sleep(.010)
