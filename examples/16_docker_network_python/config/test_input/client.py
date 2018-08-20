#!/usr/bin/env python3
import socket
import os
import csv
import sys
import time
import traceback

MY_NAME = ""
KNOWN_HOSTS_CSV = 'knownhosts.csv'

#This tut
server_name = ""
incoming_port = 0
outgoing_port = 1
outgoing_socket = None
incoming_socket = None
open_connection = None

def init():
  read_known_hosts_csv()
  initialize_incoming_connections()

def read_known_hosts_csv():
  global server_name
  global incoming_port
  global outgoing_port
  with open(KNOWN_HOSTS_CSV) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for sender, recv, port in csv_reader:
      if sender == MY_NAME:
        outgoing_port =port
        server_name = recv
      elif recv == MY_NAME:
        incoming_port = port
        server_name = sender
      else:
        continue

def initialize_incoming_connections():
  global incoming_socket
  incoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_address = ('', int(incoming_port))
  incoming_socket.bind(server_address)
  incoming_socket.listen(5)
  incoming_socket.setblocking(False)
  print('Listening on port {0} for incoming connections'.format(incoming_port))

def init_outgoing_connection():
  global outgoing_socket, outgoing_port
  if outgoing_socket != None:
    return True

  server_address = (server_name, int(outgoing_port))
  outgoing_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  try:
    outgoing_socket.connect(server_address)
    return True
  except Exception as e:
    print('Unable to connect on {0}'.format(server_address))
    return False

def send_out_message(msg):
  global outgoing_socket
  if outgoing_socket == None:
    print("ERROR! Could not establish outgoing connection to {0}".format(server_name))
    sys.exit(1)
  print("Sending '{0}' to {1}".format(msg, server_name))
  sys.stdout.flush()
  outgoing_socket.sendall(msg.encode('utf-8'))

def cleanup():
  print("Cleaning up after myself.")
  global outgoing_socket, outgoing_port, open_connection
  if outgoing_socket != None:
    outgoing_socket.close()
  if incoming_socket != None:
    incoming_socket.close()
  if open_connection != None:
    open_connection.close()

def check_for_request():
  global open_connection, incoming_socket
  try:
    if open_connection == None:
      open_connection, client_address = incoming_socket.accept()
      open_connection.setblocking(False)

    message = open_connection.recv(1024)
    return message.decode('utf-8')
  except BlockingIOError as e:
    #print("Exception encountered. Shouldn't be a big deal.")
    #traceback.print_exc()
    pass
  except Exception as e:
    print(traceback.format_exc())
  return None

def delay_seconds(secs=.5):
  time.sleep(secs)

def send_message_and_wait_for_response(message):
  while not init_outgoing_connection():
    pass

  send_out_message(message)

  response = None
  while response == None:
    response = check_for_request()
    time.sleep(.1)
  print("Recieved '{0}' from {1}".format(response, server_name))
  sys.stdout.flush()

def auto_run_zero():
  delay_seconds(1)
  send_message_and_wait_for_response('ping')
  
def auto_run_one():
  delay_seconds(1)
  send_message_and_wait_for_response('ping')
  send_message_and_wait_for_response('ping')

def auto_run_two():
  send_message_and_wait_for_response('not ping')

def auto_run_three():
  send_message_and_wait_for_response('not ping')
  send_message_and_wait_for_response('ping')
  send_message_and_wait_for_response('ping')

def auto_run_four():
  while not init_outgoing_connection():
    pass
  while True:
    send_out_message('ping')

def auto_run_five():
  message = "not ping"
  message = message * 1000000  
  send_message_and_wait_for_response(message)

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("ERROR: Please pass the following arguments:\n\t1: The name of this host in the knownhosts.csv file.\n\t3:The name of the run you want to do.")
    sys.stdout.flush()
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
  print('Shutting down.')



