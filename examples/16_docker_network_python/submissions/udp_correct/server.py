#!/usr/bin/env python3
import socket
import os
import csv
import sys
import time
import traceback

KNOWN_HOSTS_TCP = "knownhosts_tcp.csv"
KNOWN_HOSTS_UDP = "knownhosts_udp.csv"

MY_NAME = ""
USE_UDP = False

client_name = ""

incoming_tcp_port = 0
outgoing_tcp_port = 1
incoming_udp_port = 2
outgoing_udp_port = 3

outgoing_tcp_socket = None
incoming_tcp_socket = None
open_tcp_connection = None

outgoing_udp_socket = None
incoming_udp_socket = None

def init():
  read_known_hosts_csv()
  initialize_incoming_connections()


#knownhosts_tcp.csv and knownhosts_udp.csv are of the form
#sender,recipient,port_number
# such that sender sends all communications to recipient via port_number. 
def read_known_hosts_csv():
  global client_name
  global incoming_tcp_port, outgoing_tcp_port
  global incoming_udp_port, outgoing_udp_port
  with open(KNOWN_HOSTS_TCP) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for sender, recv, port in csv_reader:
      if sender == MY_NAME:
        outgoing_tcp_port =port
        client_name = recv
      elif recv == MY_NAME:
        incoming_tcp_port = port
        client_name = sender
      else:
        continue
  if USE_UDP:
    with open(KNOWN_HOSTS_UDP) as csv_file:
      csv_reader = csv.reader(csv_file, delimiter=',')
      for sender, recv, port in csv_reader:
        if sender == MY_NAME:
          outgoing_udp_port =port
          client_name = recv
        elif recv == MY_NAME:
          incoming_udp_port = port
          client_name = sender
        else:
          continue

def initialize_incoming_connections():
  global incoming_tcp_socket, incoming_udp_socket
  incoming_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_address = ('', int(incoming_tcp_port))
  incoming_tcp_socket.bind(server_address)
  incoming_tcp_socket.listen(5)
  incoming_tcp_socket.setblocking(False)
  print('Listening on port {0} for incoming tcp connections'.format(incoming_tcp_port))

  if USE_UDP:
    incoming_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    incoming_udp_socket.setblocking(False)
    server_address = ('', int(incoming_udp_port))
    incoming_udp_socket.bind(server_address)
    print('Listening on port {0} for incoming udp connections'.format(incoming_udp_port))

def init_outgoing_connection(connection_type):
  global outgoing_tcp_socket, outgoing_tcp_port
  global outgoing_udp_socket, outgoing_udp_port

  if connection_type == 'tcp':
    if outgoing_tcp_socket != None:
      return True
    server_address = (client_name, int(outgoing_tcp_port))
    outgoing_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      outgoing_tcp_socket.connect(server_address)
      return True
    except Exception as e:
      print('Unable to connect on {0} (tcp)'.format(server_address))
      traceback.print_exc()
      return False
  elif connection_type == 'udp':
    if outgoing_udp_socket != None:
      return True
    server_address = (client_name, int(outgoing_udp_port))
    outgoing_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return True
  return False
    


def send_out_message(msg, tcp=True):
  global outgoing_tcp_socket, outgoing_udp_socket
  if tcp and outgoing_tcp_socket == None:
    print("ERROR! Could not establish outgoing tcp connection to {0}".format(client_name))
    sys.exit(1)
  elif tcp == False and outgoing_udp_socket == None:
    print("ERROR! Could not establish outgoing udp connection to {0}".format(client_name))
    sys.exit(1)
  
  if tcp:
    print("Sending '{0}' to {1}".format(msg, client_name, outgoing_tcp_port))
    sys.stdout.flush()
    outgoing_tcp_socket.sendall(msg.encode('utf-8'))
  else:
    print("Sending '{0}' to {1}".format(msg, client_name, outgoing_udp_port))
    sys.stdout.flush()
    destination_address = (client_name, int(outgoing_udp_port))
    outgoing_udp_socket.sendto(msg.encode('utf-8'),destination_address)


def cleanup():
  global incoming_tcp_socket, outgoing_tcp_socket, open_tcp_connection, outgoing_udp_socket, incoming_udp_socket
  if incoming_tcp_socket != None:
    incoming_tcp_socket.close()
  if outgoing_tcp_socket != None:
    outgoing_tcp_socket.close()
  if open_tcp_connection != None:
    open_tcp_connection.close()
  if outgoing_udp_socket != None:
    outgoing_udp_socket.close()
  if incoming_udp_socket != None:
    incoming_udp_socket.close()

def check_for_request():
  global open_tcp_connection, incoming_tcp_socket, incoming_udp_socket
  try:
    if open_tcp_connection == None:
      open_tcp_connection, client_address = incoming_tcp_socket.accept()
      open_tcp_connection.setblocking(False)

    message = open_tcp_connection.recv(1024)
    return message.decode('utf-8'), True
  except BlockingIOError as e:
    #print("Exception encountered. Shouldn't be a big deal.")
    pass
  except Exception as e:
    print(traceback.format_exc())

  if USE_UDP:
    try:
      message = incoming_udp_socket.recv(1024)
      return message.decode('utf-8'), False
    except socket.error:
      pass
    except Exception as e:
      print(traceback.format_exc())

  return None, None

def sendPong(tcp=True):
  connection_type = 'tcp' if tcp else 'udp'
  if init_outgoing_connection(connection_type):
    send_out_message("pong",tcp=tcp) 
  else:
    print("ERROR: could not send pong.")

def send_err(old_message,tcp=True):
  connection_type = 'tcp' if tcp else 'udp'
  if init_outgoing_connection(connection_type):
    print("Sending 'Invalid Message {0}' to {1}".format(old_message, client_name))
    send_out_message("Invalid Message '{0}'".format(old_message),tcp=tcp) 
  else:
    print("ERROR: could not send error message.")

def run():
  running = True
  while running:
    sys.stdout.flush()
    message, tcp_message = check_for_request()
    if message == '':
      print('{0} disconnected.'.format(client_name))
      sys.stdout.flush()
      running = False
      continue
    if message != None:
      print("Recieved '{0}' from {1}".format(message, client_name))
      sys.stdout.flush()
      if message == "ping":
        sendPong(tcp=tcp_message)
      else:
        send_err(message,tcp=tcp_message)
    sys.stdout.flush()
    time.sleep(.1)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("ERROR: Please pass the following arguments:\n\t1: The name of this host in the knownhosts.csv file.")
    sys.stdout.flush()
    sys.exit(1)
  MY_NAME = sys.argv[1]

  if len(sys.argv) > 2:
    if sys.argv[2].strip() == 'udp_enabled':
      USE_UDP=True
  init()

  run()
  cleanup()