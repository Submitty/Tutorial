#!/usr/bin/env python3
import socket
import os
import csv
import sys
import time
import traceback

MY_NAME = ""
KNOWN_HOSTS_TCP = 'knownhosts_tcp.txt'
KNOWN_HOSTS_UDP = 'knownhosts_udp.txt'
USE_UDP = False


# This tutorial is kept simple intentionally rather than using data structures or
# dictionaries to store these values.
server_name = ""

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
  global server_name
  global incoming_tcp_port, outgoing_tcp_port
  global incoming_udp_port, outgoing_udp_port
  
  with open(KNOWN_HOSTS_TCP) as infile:
    content = infile.readlines()    

  for line in content:
    sender, recv, port = line.split()
    if sender == MY_NAME:
      outgoing_tcp_port =port
      server_name = recv
    elif recv == MY_NAME:
      incoming_tcp_port = port
      server_name = sender
    else:
      continue

  if USE_UDP:
    with open(KNOWN_HOSTS_UDP) as infile:
      content = infile.readlines()

    for line in content:
      sender, recv, port = line.split()
      if sender == MY_NAME:
        outgoing_udp_port =port
        server_name = recv
      elif recv == MY_NAME:
        incoming_udp_port = port
        server_name = sender
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
    server_address = (server_name, int(outgoing_tcp_port))
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
    server_address = (server_name, int(outgoing_udp_port))
    outgoing_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return True
  return False
    


def send_out_message(msg, tcp=True):
  global outgoing_tcp_socket, outgoing_udp_socket
  if tcp and outgoing_tcp_socket == None:
    print("ERROR! Could not establish outgoing tcp connection to {0}".format(server_name))
    sys.exit(1)
  elif tcp == False and outgoing_udp_socket == None:
    print("ERROR! Could not establish outgoing udp connection to {0}".format(server_name))
    sys.exit(1)

  
  if tcp:
    print("Sending '{0}' to {1}".format(msg, server_name, outgoing_tcp_port))
    sys.stdout.flush()
    outgoing_tcp_socket.sendall(msg.encode('utf-8'))
  else:
    sys.stdout.flush()
    destination_address = (server_name, int(outgoing_udp_port))
    outgoing_udp_socket.sendto(msg.encode('utf-8'),destination_address)

def cleanup():
  print("Cleaning up after myself.")
  global incoming_tcp_socket, outgoing_tcp_socket, open_tcp_connection, outgoing_udp_socket, incoming_udp_socket
  if incoming_tcp_socket != None:
    incoming_tcp_socket.close()
  if outgoing_tcp_socket != None:
    outgoing_tcp_socket.close()
  if open_tcp_connection != None:
    open_tcp_connection.close()
  if USE_UDP:
    if outgoing_udp_socket != None:
      outgoing_udp_socket.close()
    if incoming_udp_socket != None:
      incoming_udp_socket.close()

def check_for_request(tcp_allowed=True):
  global open_tcp_connection, incoming_tcp_socket, incoming_udp_socket
  
  if tcp_allowed:
    try:
      if open_tcp_connection == None:
        open_tcp_connection, client_address = incoming_tcp_socket.accept()
        open_tcp_connection.setblocking(False)

      message = open_tcp_connection.recv(1024)
      return message.decode('utf-8')
    except BlockingIOError as e:
      #print("Exception encountered. Shouldn't be a big deal.")
      #traceback.print_exc()
      pass
    except Exception as e:
      print(traceback.format_exc())

  if USE_UDP:
    try:
      message = incoming_udp_socket.recv(1024)
      return message.decode('utf-8')
    except socket.error:
      pass
    except Exception as e:
      print(traceback.format_exc())

  return None

def delay_seconds(secs=.5):
  time.sleep(secs)

def send_message_and_wait_for_response(message,tcp=True):
  connection_type = 'tcp' if tcp else 'udp'
  while not init_outgoing_connection(connection_type):
    pass

  send_out_message(message,tcp)

  response = None
  while response == None:
    response = check_for_request()
    time.sleep(.1)
  print("Recieved '{0}' from {1}".format(response, server_name))
  sys.stdout.flush()

def just_send_message(message,tcp=True):
  connection_type = 'tcp' if tcp else 'udp'
  while not init_outgoing_connection(connection_type):
    pass
  send_out_message(message,tcp)

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
  print("We are sending messages to the server...")
  just_send_message('ping',tcp=False,)
  just_send_message('not ping',tcp=False)
  just_send_message('ping',tcp=False)
  just_send_message('not ping',tcp=False)
  just_send_message('not ping',tcp=False)
  just_send_message('ping',tcp=False)
  just_send_message('ping',tcp=False)

  responses = []
  for count in range(7):
    delay_seconds()
    #We don't want tcp responses.
    response = check_for_request(tcp_allowed=False)
    if response != None:
      responses.append(response)
  pongs = 0
  not_pongs = 0
  for response in responses:
    if response == "pong":
      pongs += 1
    else:
      not_pongs += 1
  
  if pongs > 0:
    print("We sent 4 pings to the server...")
    print('We recieved some pongs! It looks like the student was using UDP!'.format(pongs))
  if not_pongs > 0:
    print("We sent 3 'not pings' to the server...")
    print('We recieved some "not pongs!" It looks like the student was using UDP!'.format(not_pongs))


if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("ERROR: Please pass the following arguments:\n\t1: The name of this host in the knownhosts.csv file.\n\t3:The name of the run you want to do.")
    sys.stdout.flush()
    sys.exit(1)
  MY_NAME = sys.argv[1]
  RUN_NAME = sys.argv[2]

  if len(sys.argv) > 3:
    if sys.argv[3].strip() == 'udp_enabled':
      USE_UDP=True
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

  cleanup()
  print('Shutting down.')



