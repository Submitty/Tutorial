#!/usr/bin/env python3
import socket
import os
import csv
import sys
import time
import traceback

MY_NAME = ""
KNOWN_HOSTS_CSV = 'knownhosts_tcp.csv'

# This tutorial is kept simple intentionally rather than using data structures or
# dictionaries to store these values.
client_name = ""
incoming_port = 0
outgoing_port = 1
outgoing_socket = None
incoming_socket = None
open_connection = None

def init():
  read_known_hosts_csv()
  initialize_incoming_connections()

#knownhosts_tcp.csv and knownhosts_udp.csv are of the form
#sender,recipient,port_number
# such that sender sends all communications to recipient via port_number. 
def read_known_hosts_csv():
  global client_name
  global incoming_port
  global outgoing_port
  with open(KNOWN_HOSTS_CSV) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for sender, recv, port in csv_reader:
      if sender == MY_NAME:
        outgoing_port =port
        client_name = recv
      elif recv == MY_NAME:
        incoming_port = port
        client_name = sender
      else:
        continue

def initialize_incoming_connections():
    global incoming_socket

    incoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('', int(incoming_port))
    incoming_socket.bind(server_address)
    incoming_socket.listen(5)
    incoming_socket.setblocking(False)
    print('Listening on port {0} for incoming tcp connections'.format(incoming_port))

def init_outgoing_connection():
  global outgoing_socket
  if outgoing_socket != None:
    return True

  server_address = (client_name, int(outgoing_port))
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
    print("ERROR! Could not establish outgoing connection to {0}".format(client_name))
    sys.exit(1)
  print("Sending '{0}' to {1}".format(msg, client_name))
  outgoing_socket.sendall(msg.encode('utf-8'))

def cleanup():
  global outgoing_socket
  global incoming_socket
  global open_connection

  if outgoing_socket != None:
    outgoing_socket.close()
  if incoming_socket != None:
    incoming_socket.close()
  if open_connection != None:
    open_connection.close()

def check_for_request():
  global open_connection
  global incoming_socket

  try:
    if open_connection == None:
      open_connection, client_address = incoming_socket.accept()
      open_connection.setblocking(False)

    message = open_connection.recv(1024)
    return message.decode('utf-8')
  except BlockingIOError as e:
    pass
  except Exception as e:
    print(traceback.format_exc())
    sys.stdout.flush()
  return None

def sendPong():
  if init_outgoing_connection():
    while True:
      send_out_message("pong") 
  else:
    print("ERROR: could not send pong.")

def send_err(old_message):
  if init_outgoing_connection():
    print("Sending 'Invalid Message {0}' to {1}".format(old_message, client_name))
    send_out_message("Invalid Message '{0}'".format(old_message)) 
  else:
    print("ERROR: could not send error message.")

def run():
  running = True
  while running:
    message = check_for_request()
    if message == '':
      print('{0} disconnected.'.format(client_name))
      running = False
      continue
    if message != None:
      print("Recieved '{0}' from {1}".format(message, client_name))
      if message == "ping":
        sendPong()
      else:
        send_err(message)
    sys.stdout.flush()
    time.sleep(.1)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("ERROR: Please pass the following arguments:\n\t1: The name of this host in the knownhosts.csv file.")
    sys.stdout.flush()
    sys.exit(1)
  MY_NAME = sys.argv[1]
  
  init()
  run()
  cleanup()