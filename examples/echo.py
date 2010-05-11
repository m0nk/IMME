import imme
import time

packet_pool=[]
assembled_packets=[]
messages=[]
connection_id=1
message_id=1

def convert_byte(text):
  bytes=[]
  for letter in text:
    bytes.append(ord(letter))
  return bytes

while 1:
  packet_pool+=imme.packet_reader()
  if len(packet_pool)>0:
    temp=imme.assemble_packets(packet_pool)
    if temp:
      print temp
      assembled_packets.append(temp[0])
      packet_pool=temp[1]
    print packet_pool
    if assembled_packets:
      for i in range(len(assembled_packets)):
        packet=assembled_packets.pop(i)
        messages.append(imme.parse_packet(packet))
        print messages
    if messages:
      for i in range(len(messages)):
        message=messages.pop(i)
        if message:
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
          elif message[0]=='MSG_IN':
            packet=imme.craft_packet(imme.MESSAGE_TYPES['MSG_IN_RES']+[message[1]['msgid'],1]+message[1]['contact_id']+message[1]['text_id']+[0])
            packet2=imme.craft_packet(imme.MESSAGE_TYPES['MSG_OUT']+[message_id,1]+[1,3,3,7,9,2,1,3]+[1,1,1,1]+convert_byte(message[1]['text'])+[0])
            imme.send(packet)
            imme.send(packet2)
            if message_id != 256:
              message_id+=1
            else: 
              message_id=1
           # imme.send(packet)
          elif message[0]=='MSG_OUT_ACK':
            print 'message '+str(message[1]['msgid'])+' send sucessfully'
          elif message[0]=='DISCONNECT_REQ':
            packet=imme.craft_packet(imme.MESSAGE_TYPES['DISCONNECT_RES']+[message[1]['msgid'],1]+message[1]['contact_id']+[0])
            imme.send(packet)
          elif message[0]=='CONVO_END_REQ':
            packet=imme.craft_packet(imme.MESSAGE_TYPES['CONVO_END_RES']+[message[1]['msgid'],1]+message[1]['contact_id']+message[1]['text_id']+[0])
            imme.send(packet)
          else:
            print message
            print '^unhandled'
