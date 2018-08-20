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
    log("ERROR! Could not establish outgoing connection to {0}")
    sys.exit(1)
  sock = NAME_TO_INFO[name]['outgoing_socket']
  print('responding with {0}'.format(msg))
  sock.sendall(msg.encode('utf-8'))


def check_for_request():

  for port, info in PORT_TO_INFO.items(): 
    if not 'incoming_connection' in info:
      continue

    if 'disconnected' in info:
      if info['disconnected'] == True:
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

def sendPong(name):
  if init_outgoing_connection(name):
    send_out_message(name, "pong") 
  else:
    print("ERROR: could not send pong.")

def send_err(name,old_message):
  if init_outgoing_connection(name):
    send_out_message(name, "I didn't understand the message {0}".format(old_message)) 
  else:
    print("ERROR: could not send pong.")

def run():
  while True:
    message, name, port = check_for_request()
    if message == '':
      PORT_TO_INFO[port]['disconnected'] = True
      continue
    if name != None:
      if message == "ping":
        sendPong(name)
      else:
        send_err(name,message)
    time.sleep(.1)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    log("ERROR: Please pass the following arguments:\n\t1: The name of this host in the knownhosts.csv file.")
    sys.exit(1)
  MY_NAME = sys.argv[1]
  
  init()
  run()