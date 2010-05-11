import usb
import time

vendor_id=0x0e4c
product_id=0x7272

MESSAGE_TYPES={'NAME_REQ':[1,0,128],'NAME_RES':[0,1,128],'LOGIN_ATTEMPT':[1,0,1],'LOGIN_AUTH':[0,1,1],
                       'FRIEND_LIST_REQ':[1,8,1],'FRIEND_LIST_RES':[0,9,1],'LOGGED_IN_FRIENDS_REQ':[1,4,1],
                       'LOGGED_IN_FRIENDS_RES':[0,5,1],'DISCONNECT_REQ':[1,2,1],'DISCONNECT_RES':[0,3,1],
                       'MSG_IN':[1,4,2],'MSG_IN_RES':[0,5,2],'MSG_OUT':[0,6,2],'MSG_OUT_ACK':[0,7,2],
                       'CONVO_END_REQ':[1,8,2],'CONVO_END_RES':[0,9,2]} 

def find_imme():
  for bus in usb.busses():
    for device in bus.devices:
      if device.idVendor == vendor_id and device.idProduct == product_id:    
        handle=device.open()
        try:
          handle.detachKernelDriver(0)
        except:
          pass
        try:
          handle.claimInterface(0)
        except:
          pass
  return handle

handle=find_imme()

init_string=(250,251,17,1,1,13,0,1,128,0,7,4,4,8,109,48,110,107,0,46)

def convert_ascii(text):
  new_text=''
  for byte in text:
    new_text+=chr(byte)
  return new_text

def send(packets):
  for d in range(len(packets)):
    packet=packets.pop(0)
    number=0
    for i in packet:
      handle.controlMsg(0x21,0x09,(number,i),0x0200,0x00)
      number+=1
      time.sleep(.050)

packets_on_wire=[]

def packet_reader():
  unparsed_packets=[]
  while 1:
    try:
      unparsed_packets.append(handle.interruptRead(0x82,2)[0])
      if unparsed_packets[0]==0:
        unparsed_packets=[]
    except:
      return unparsed_packets

def assemble_packets(data_pool):
  packet=None
  temp=data_pool[:]
  done=False
  if len(temp)>=5:
    for part in range(1,temp[4]+1,1):
      if part ==1:
        if len(temp)>=temp[2]+2:
          packet=temp[:temp[2]+3]
          if temp[4]==1:
            done=True
          temp=temp[temp[2]+3:]
      else:
        packet=packet[:len(packet)-1]
        if len(temp)>=5 and len(temp)>=temp[2]+2:
          packet+=temp[5:temp[2]+3]
          if temp[3]==temp[4]:
            done=True
          temp=temp[temp[2]+3:]
  if done:
    return packet,temp
  return None

def parse_packet(packet):
  for key in MESSAGE_TYPES:
    if MESSAGE_TYPES[key]==packet[6:9]:
      message_type=key
      message=[message_type]
      if message_type=='NAME_REQ':
        return message
      elif message_type=='LOGIN_ATTEMPT':
        message.append({'msgid':packet[9],'key':packet[11:15],'user':convert_ascii(packet[15:packet[15:].index(0)+15]),'pass':convert_ascii(packet[packet[15:].index(0)+16:len(packet)-2])})
      elif message_type=='FRIEND_LIST_REQ':
        message.append({'msgid':packet[9],'connection_id':packet[10],'contact_id':packet[11:15]})
      elif message_type=='LOGGED_IN_FRIENDS_REQ':
        message.append({'msgid':packet[9],'connection_id':packet[10],'contact_id':packet[11:15]})
      elif message_type=='DISCONNECT_REQ':
        message.append({'msgid':packet[9],'conection_id':packet[10],'contact_id':packet[11:15]})
      elif message_type=='MSG_IN':
        message.append({'msgid':packet[9],'connection_id':packet[10],'contact_id':packet[11:15],'text_id':packet[15:19],'recipient_id':packet[19:23],'text':convert_ascii(packet[23:len(packet)-2])})
      elif message_type=='MSG_OUT_ACK':
        message.append({'msgid':packet[9],'connection_id':packet[10],'contact_id':packet[11:15],'text_id':packet[15:19],'sender_id':packet[19:23],'error_code':packet[24]})
      elif message_type=='CONVO_END_REQ':
        message.append({'msgid':packet[9],'connection_id':packet[10],'contact_id':packet[11:15],'text_id':packet[15:19]})
      else: 
        print 'packet'  
     
      return message
   
def generate_checksum(packet):
  checksum=0
  for item in packet:
    checksum+=item
  checksum=checksum%256
  return checksum

def craft_packet(command):
  packets=[]
  length2=len(command)
  parts=len(command)/55+1
  for i in range(1,parts+1,1):
    if i==1:
      if parts > 1:
        packet=[250,251,59,1,parts,length2]+command[0:55]
        packet.append(generate_checksum(packet[2:]))
      else:
        packet=[250,251,length2+4,1,1,length2]+command
        packet.append(generate_checksum(packet[2:]))
      packets.append(packet)
    else:
      command=command[55:55+len(command)-55]
      packet=[250,251,len(command)+3,i,parts]+command
      packet.append(generate_checksum(packet[2:]))
      packets.append(packet)
  return packets
