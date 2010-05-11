import imme
import irc
import thread
import time

message_id=1
packet_pool=[]
assembled_packets=[]
messages=[]
connected=0

sent_messages=[]

x=0
def convert_byte(text):
  bytes=[]
  for letter in text:
    bytes.append(ord(letter))
  return bytes

class imme_thread:
  packet_pool=[]
  def get_imme(self,name,number):
    while 1:
      self.packet_pool+=imme.packet_reader()
      time.sleep(.100)

class irc_thread:
  irc_messages=[]
  def read_messages(self,name,number):
    while 1:
      self.irc_messages+= irc.recieve_messages()

imme_thread=imme_thread()
thread.start_new_thread(imme_thread.get_imme,('name',2))

irc_thread=irc_thread()
thread.start_new_thread(irc_thread.read_messages,('name1',3))
  
while 1:
  if len(imme_thread.packet_pool)>0:
    if imme_thread.packet_pool[0]!=250:
      imme_thread.packet_pool=[]
    else:
      temp=imme.assemble_packets(imme_thread.packet_pool)
      if temp:
        assembled_packets.append(temp[0])
        imme_thread.packet_pool=temp[1]
      if assembled_packets:
        for i in range(len(assembled_packets)):
          packet=assembled_packets.pop(i)
          messages.append(imme.parse_packet(packet))
      if messages:
        for i in range(len(messages)):
          message=messages.pop(0)
          print message
          if message[0]=='NAME_REQ':
            imme.send(imme.craft_packet(imme.MESSAGE_TYPES['NAME_RES']+[0,7,4,4,8,ord('m'),ord('0'),ord('n'),ord('k'),0]))
          elif message[0]=='LOGIN_ATTEMPT':
            packet=imme.craft_packet(imme.MESSAGE_TYPES['LOGIN_AUTH']+[message[1]['msgid'],1,1,3,3,7,0]+message[1]['key'])
            imme.send(packet)
          elif message[0]=='FRIEND_LIST_REQ':
            packet=imme.craft_packet(imme.MESSAGE_TYPES['FRIEND_LIST_RES']+[message[1]['msgid'],1]+message[1]['contact_id']+[0,1,1,1,1,1,ord('e'),ord('c'),ord('h'),ord('o'),0])
            imme.send(packet)
          elif message[0]=='LOGGED_IN_FRIENDS_REQ':
            packet=imme.craft_packet(imme.MESSAGE_TYPES['LOGGED_IN_FRIENDS_RES']+[message[1]['msgid'],1]+message[1]['contact_id']+[0,1,1,1,1,1])
            imme.send(packet)
            connected=1
          elif message[0]=='MSG_OUT_ACK':
            print 'message '+str(message[1]['msgid'])+' send sucessfully'
          elif message[0]=='MSG_IN':
            if message[1]['msgid'] not in sent_messages:
              packet=imme.craft_packet(imme.MESSAGE_TYPES['MSG_IN_RES']+[message[1]['msgid'],1]+message[1]['contact_id']+message[1]['text_id']+[0])
              imme.send(packet)
              irc.send_message(message[1]['text'])
              sent_messages.append(message[1]['msgid'])
            if message[1]['msgid'] ==256:
              sent_message=[]
          else:
            print message

  for i in range(len(irc_thread.irc_messages)):
    if connected==1:
      irc_message=irc_thread.irc_messages.pop(0)
      if len(irc_message)<=80:
        packet=imme.craft_packet(imme.MESSAGE_TYPES['MSG_OUT']+[message_id,1]+[1,3,3,7,9,2,1,3]+[1,1,1,1]+convert_byte(irc_message))
        imme.send(packet)
      else:
        for i in range(len(irc_message)/80):
          imme.send(imme.craft_packet(imme.MESSAGE_TYPES['MSG_OUT']+[message_id,1]+[1,3,3,7,9,2,1,3]+[1,1,1,1]+convert_byte(irc_message[0:80])))
          irc_message=irc_message[80:]
          if message_id!=256:
            message_id+=1
          else:
            message_id=1
        if irc_message:
          imme.send(imme.craft_packet(imme.MESSAGE_TYPES['MSG_OUT']+[message_id,1]+[1,3,3,7,7,9,2,1,3]+[1,1,1,1]+convert_byte(irc_message)))
      if message_id!=256:
        message_id+=1
      else:
        message_id=1
