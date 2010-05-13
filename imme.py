import usb
import time
import thread


class imme:
  data_pool=[]
  assembled_packets=[]
  messages=[]

  connection_id=1
  message_id=1

  MESSAGE_TYPES={'NAME_REQ':[1,0,128],'NAME_RES':[0,1,128],'LOGIN_ATTEMPT':[1,0,1],'LOGIN_AUTH':[0,1,1],
                       'FRIEND_LIST_REQ':[1,8,1],'FRIEND_LIST_RES':[0,9,1],'LOGGED_IN_FRIENDS_REQ':[1,4,1],
                       'LOGGED_IN_FRIENDS_RES':[0,5,1],'DISCONNECT_REQ':[1,2,1],'DISCONNECT_RES':[0,3,1],
                       'MSG_IN':[1,4,2],'MSG_IN_RES':[0,5,2],'MSG_OUT':[0,6,2],'MSG_OUT_ACK':[0,7,2],
                       'CONVO_END_REQ':[1,8,2],'CONVO_END_RES':[0,9,2]}

  def __init__(self):
    for bus in usb.busses():
      for device in bus.devices:
        if device.idVendor==0x0e4c and device.idProduct==0x7272:
          handle=device.open()
          try:
            handle.detachKernelDriver(0)
          except:
            pass
          try:
            handle.claimInterface(0)
          except:
            pass
          self.handle=handle
  
  def convert_ascii(self,text):
    new_text=''
    for byte in text: 
      new_text+=chr(byte)
    return new_text

  def convert_bytes(self,text):
    bytes=[]
    for letter in text:
      bytes.append(ord(letter))
    print bytes
    return bytes

  def send(self,packets):
    for x in range(len(packets)):
      packet=packets.pop(0)
      number=0
      print packet
      for i in packet:
        self.handle.controlMsg(0x21,0x09,(number,i),0x0200,0x00)
        number+=1
      time.sleep(.100) 
  
  def packet_reader(self):
    x=0
    while 1:
      x+=1
      try:
        self.data_pool.append(self.handle.interruptRead(0x82,2)[0])
      except:
        return x

  def assemble_packets(self):
    packet=None
    temp=self.data_pool[:]
    done=False
    if len(temp)>=5:
      for part in range(1,temp[4]+1,1):
        if part == 1:
          if len(temp)>=temp[2]+2:
            packet=temp[:temp[2]+3]
            if temp[4]==1:
              done = True
            temp=temp[temp[2]+3:]
        else:
          if packet:
            packet=packet[:len(packet)-1]
            if len(temp)>=5 and len(temp)>=temp[2]+2:
              packet+=temp[5:temp[2]+3]
              if temp[3] == temp[4]:
                done = True
              temp=temp[temp[2]+3:]
    if done:
      self.assembled_packets.append(packet)
      self.data_pool=temp
      
  
  def parse_packets(self):
    for b in self.assembled_packets:
      packet=self.assembled_packets.pop(0)
      for key in self.MESSAGE_TYPES:
        if self.MESSAGE_TYPES[key]==packet[6:9]:
          message=[key]
          if key=='NAME_REQ':
            print 'name request'
          elif key=='LOGIN_ATTEMPT':
            message.append({'msgid':packet[9],'key':packet[11:15],'user':self.convert_ascii(packet[15:packet[15:].index(0)+15]),'pass':self.convert_ascii(packet[packet[15:].index(0)+16:len(packet)-2])})
          elif key=='FRIEND_LIST_REQ':
            message.append({'msgid':packet[9],'connection_id':packet[10],'contact_id':packet[11:15]})
          elif key=='LOGGED_IN_FRIENDS_REQ':
            message.append({'msgid':packet[9],'connection_id':packet[10],'contact_id':packet[11:15]})
          elif key=='DISCONNECT_REQ':
            message.append({'msgid':packet[9],'connection_id':packet[10],'contact_id':packet[11:15]})
          elif key=='MSG_IN':
            message.append({'msgid':packet[9],'connection_id':packet[10],'contact_id':packet[11:15],'text_id':packet[15:19],'recipient_id':packet[19:23],'text':self.convert_ascii(packet[23:len(packet)-2])})
          elif key=='MSG_OUT_ACK':
            message.append({'msgid':packet[9],'connection_id':packet[10],'contact_id':packet[11:15],'text_id':packet[15:19],'sender_id':packet[19:23],'error_code':packet[24]})
          elif key=='CONVO_END_REQ':
            message.append({'msgid':packet[9],'connection_id':packet[10],'contact_id':packet[11:15],'text_id':packet[15:19]})
          self.messages.append(message)


  def generate_checksum(self,packet):
    checksum=0
    for item in packet:
      checksum+=item
    return checksum%256

  def craft_packet(self,command):
    packets=[]
    length2=len(command)
    parts=len(command)/55+1
    for i in range(1,parts+1,1):
      if i==1:
        if parts > 1:
          packet=[250,251,59,1,parts,length2]+command[0:55]
          packet.append(self.generate_checksum(packet[2:]))
        else:
          packet=[250,251,length2+4,1,1,length2]+command
          packet.append(self.generate_checksum(packet[2:]))
        packets.append(packet)
      else:
        command=command[55:55+len(command)-55]
        packet=[250,251,len(command)+3,i,parts]+command
        packet.append(self.generate_checksum(packet[2:]))
        packets.append(packet)
    return packets

  def send_computer_name(self,name,id):
    packet=self.craft_packet(self.MESSAGE_TYPES['NAME_RES']+[0]+id+self.convert_bytes(name))
    print packet
    self.send(packet)

  def allow_login(self,msgid,contact_id,key):
    packet=self.craft_packet(self.MESSAGE_TYPES['LOGIN_AUTH']+[msgid,self.connection_id]+contact_id+[0]+key)
    self.send(packet)
    self.connection_id+=1

  def disallow_login(self,msgid,key,invalid_pass):
    if invalid_pass:
      error_byte=0xFD
    else:
      error_byte=0xFC
    packet=self.craft_packet(self.MESSAGE_TYPES['LOGIN_AUTH']+[msgid,0,0,0,0,0,error_byte]+key)
    self.send(packet)

  def send_friend_list(self,msgid,connection_id,contact_id,friend_list):
    number_of_friends=len(friend_list)
    friend_packet=[]
    for friend in friend_list:
      temp=friend[0]+self.convert_bytes(friend[1])+[0]
      friend_packet+=temp
    packet=self.craft_packet(self.MESSAGE_TYPES['FRIEND_LIST_RES']+[msgid,connection_id]+contact_id+[0,number_of_friends]+friend_packet)
    self.send(packet)

  def send_online_list(self,msgid,connection_id,contact_id,friend_ids):
    online_friends=len(friend_ids)
    friend_packet=[] 
    for i in friend_ids:
      friend_packet.append(i)
    packet=self.craft_packet(self.MESSAGE_TYPES['LOGGED_IN_FRIENDS_RES']+[msgid,connection_id]+contact_id+[0,online_friends]+friend_packet)
    self.send(packet)

  def acknowledge_message(self,msgid,connection_id,contact_id,text_id):
    packet=self.craft_packet(self.MESSAGE_TYPES['MSG_IN_RES']+[msgid,connection_id]+contact_id+text_id+[0])
    self.send(packet)

  def send_message(self,connection_id,contact_id,sender_id,text):
    text_id=[9,5,3,4]
    packet=self.craft_packet(self.MESSAGE_TYPES['MSG_OUT']+[self.message_id,connection_id]+contact_id+text_id+sender_id+self.convert_bytes(text))
    self.send(packet)
    if self.message_id!=256:
      self.message_id+=1
    else:
      self.message_id=1

  def end_conversation(self,msgid,connection_id,contact_id,text_id):
    packet=self.craft_packet(self.MESSAGE_TYPES['CONVO_END_RES']+[msgid,connection_id]+contact_id+text_id+[0])
    self.send(packet)

  def close_connection(self,msgid,connection_id,contact_id):
    packet=self.craft_packet(self.MESSAGE_TYPES['DISCONNECT_RES']+[msgid,connection_id]+contact_id+[0])
    self.send(packet)

  def read_loop(self,name,number):
    while 1:
      if self.data_pool and self.data_pool[0]!=250:
        self.data_pool=[]
      self.packet_reader()
      if self.data_pool:
        self.assemble_packets()
      if self.assembled_packets:
        self.parse_packets()
      time.sleep(.100)

  def send_loop(self):
    while 1:
      if self.send_pool:
        for i in send_pool:
          self.send(i)

  def start_loops(self):
     thread.start_new_thread(self.read_loop,('name1',3))
