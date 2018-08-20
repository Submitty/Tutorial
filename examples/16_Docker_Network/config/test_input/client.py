#!/usr/bin/env python3
import socket
import os
import csv
import sys
import time
import traceback

#!/usr/bin/env python3
import socket
import os
import csv
import sys
import time
import traceback

MY_NAME = ""
SERVER_NAMES_FILE = ''
KNOWN_HOSTS_CSV = 'knownhosts.csv'

PORT_TO_INFO = dict()
NAME_TO_INFO = dict()

def init():
  read_known_hosts_csv()
  print('read known hosts')
  initialize_incoming_connections()
  print('initialized connections')

def read_known_hosts_csv():
  with open(KNOWN_HOSTS_CSV) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    
    for sender, recv, port in csv_reader:
      if sender == MY_NAME:
        if not recv in NAME_TO_INFO:
          NAME_TO_INFO[recv] = dict()
        NAME_TO_INFO[recv]['outgoing_port'] = port
        if not port in PORT_TO_INFO:
          PORT_TO_INFO[port] = dict()
        PORT_TO_INFO[port]['outgoing_connection'] = recv
      elif recv == MY_NAME:
        if not sender in NAME_TO_INFO:
          NAME_TO_INFO[sender] = dict()
        NAME_TO_INFO[sender]['incoming_port'] = port
        if not port in PORT_TO_INFO:
          PORT_TO_INFO[port] = dict()
        PORT_TO_INFO[port]['incoming_connection'] = sender
      else:
        continue

def initialize_incoming_connections():
  for name, info in NAME_TO_INFO.items():
    if not 'incoming_port' in info:
      continue
    port = info['incoming_port']
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('', int(port))
    sock.bind(server_address)
    sock.listen(5)
    sock.setblocking(False)
    NAME_TO_INFO[name]['incoming_socket'] = sock
    print('Listening on port {0} for incoming connections'.format(port))

def init_outgoing_connection(name):
  if 'outgoing_socket' in NAME_TO_INFO[name]:
    return True

  outgoing_port = NAME_TO_INFO[name]['outgoing_port']

  server_address = ('localhost', int(outgoing_port))
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  try:
    sock.connect(server_address)
    NAME_TO_INFO[name]['outgoing_socket'] = sock
    return True
  except Exception as e:
    print('Could not connect to {0}'.format(server_address))
    return False

def send_out_message(name, msg):
  if not 'outgoing_socket' in NAME_TO_INFO[name]:
    print("ERROR! Could not establish outgoing connection to {0}")
    sys.exit(1)
  sock = NAME_TO_INFO[name]['outgoing_socket']
  print("sending {0} to {1}".format(msg, name))
  sock.sendall(msg.encode('utf-8'))

def cleanup():
  for port, info in PORT_TO_INFO.items(): 
    if not 'incoming_connection' in info:
      continue
    name = info['incoming_connection']
    sock = NAME_TO_INFO[name]['incoming_socket']

    if 'connection' in NAME_TO_INFO[name]:
      NAME_TO_INFO[name]['connection'].close()
    sock.close()

def check_for_request():
  for port, info in PORT_TO_INFO.items(): 
    if not 'incoming_connection' in info:
      continue

    name = info['incoming_connection']
    sock = NAME_TO_INFO[name]['incoming_socket']

    try:
      if not 'connection' in NAME_TO_INFO[name]:
        connection, client_address = sock.accept()
        connection.setblocking(False)
        NAME_TO_INFO[name]['connection'] = connection
      else:
        connection = NAME_TO_INFO[name]['connection']

      message = connection.recv(1024)
      return message.decode('utf-8'), name, port
    except BlockingIOError as e:
      #print("Exception encountered. Shouldn't be a big deal.")
      #traceback.print_exc()
      pass
    except Exception as e:
      log(traceback.format_exc())
  return None, None, None

def delay_seconds(secs=.5):
  time.sleep(secs)

def send_message_and_wait_for_response(server_name, message):
  if init_outgoing_connection(server_name):
    send_out_message(server_name, message)

  response = None
  #log('sent {0} on port {1}. Waiting for response.'.format(message, port))
  while response == None:
    response, return_name, return_port = check_for_request()
    time.sleep(.1)
  print('recieved {0} from {1}'.format(response, server_name))

def auto_run_zero():
  delay_seconds(1)
  send_message_and_wait_for_response('server', 'ping')
  
def auto_run_one():
  delay_seconds(1)
  send_message_and_wait_for_response('server','ping')
  send_message_and_wait_for_response('server','ping')

def auto_run_two():
  send_message_and_wait_for_response('server','not ping')

def auto_run_three():
  send_message_and_wait_for_response('server','not ping')
  send_message_and_wait_for_response('server','ping')
  send_message_and_wait_for_response('server','ping')

def auto_run_four():
  while not init_outgoing_connection('server'):
    pass
  while True:
    send_out_message('server','ping')

def auto_run_five():
  message = "not ping"
  message = message * 10000  
  send_message_and_wait_for_response('server', message)




if __name__ == "__main__":
  if len(sys.argv) < 3:
    log("ERROR: Please pass the following arguments:\n\t1: The name of this host in the knownhosts.csv file.\n\t3:The name of the run you want to do.")
    sys.exit(1)
  MY_NAME = sys.argv[1]
  RUN_NAME = sys.argv[2]
  init()
  if RUN_NAME == "0":
    auto_run_zero()
  elif RUN_NAME == "1":
    auto_run_one()
  elif RUN_NAME == "2":
    auto_run_two()
  elif RUN_NAME == "3":
    auto_run_three()
  elif RUN_NAME == "4":
    auto_run_four()
  elif RUN_NAME == "5":
    auto_run_five()

  cleanup()




