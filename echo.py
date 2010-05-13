from imme import imme

imme=imme()
imme.start_loops()

while 1:
 for i in imme.messages:
  print len(imme.messages)
  message=imme.messages.pop(0)
  if message[0]=='NAME_REQ':
    imme.send_computer_name('m0nk',[1,2,3,4])
  if message[0]=='LOGIN_ATTEMPT':
    if message[1]['user']==message[1]['pass']:
      imme.allow_login(message[1]['msgid'],[7,4,4,8],message[1]['key'])
    else:
      imme.disallow_login(message[1]['msgid'],message[1]['key'],True)
  elif message[0]=='FRIEND_LIST_REQ':
    friend_list=[([1,3,3,7],'echo')]
    imme.send_friend_list(message[1]['msgid'],message[1]['connection_id'],message[1]['contact_id'],friend_list)
  elif message[0]=='LOGGED_IN_FRIENDS_REQ':
    imme.send_online_list(message[1]['msgid'],message[1]['connection_id'],message[1]['contact_id'],[1,3,3,7])
  elif message[0]=='MSG_IN':
    imme.acknowledge_message(message[1]['msgid'],message[1]['connection_id'],message[1]['contact_id'],message[1]['text_id'])
    imme.send_message(message[1]['connection_id'],message[1]['contact_id'],message[1]['recipient_id'],message[1]['text'])
  elif message[0]=='CONVO_END_REQ':
    imme.end_conversation(message[1]['msgid'],message[1]['connection_id'],message[1]['contact_id'],message[1]['text_id'])
  elif message[0]=='DISSCONNECT_REQ':
    imme.close_connection(message[1]['msgid'],message[1]['connection_id'],message[1]['contact_id'])
