#!/usr/bin/env python3
import socket
import os
import sys
import time
import json
import traceback
import threading

MY_NAME = ""
KNOWN_HOSTS_JSON = 'knownhosts.json'
ADDRESS_BOOK = dict()
IP_LOOKUP = dict()
RUNNING = False
INCOMING_PORT = -1

#knownhosts_tcp.csv and knownhosts_udp.csv are of the form
#sender,recipient,port_number
# such that sender sends all communications to recipient via port_number. 
def read_known_hosts_json():
  global INCOMING_PORT, ADDRESS_BOOK, IP_LOOKUP
  with open(KNOWN_HOSTS_JSON) as infile:
    content = json.load(infile)
  
  for host, info in content['hosts'].items():
    port = info['udp_start_port']
    IP_LOOKUP[info['ip_address']] = host
    
    if host == MY_NAME:
      INCOMING_PORT = int(port)
    else:
      ADDRESS_BOOK[host] = int(port)

  if INCOMING_PORT == -1:
    raise SystemExit(f'ERROR: No entry for this host in {KNOWN_HOSTS_JSON}')


def listen_for_incoming_messages():
  global RUNNING, IP_LOOKUP, ADDRESS_BOOK

  udp_socket =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udp_socket.bind(('', INCOMING_PORT))
  udp_socket.settimeout(1)

  while RUNNING:
    try:
      msg, addr = udp_socket.recvfrom(1024)
    except socket.timeout as e:
      continue
    message = msg.decode('utf-8')

    parts = message.split(':')

    while parts[0] == MY_NAME:
      print(f'Forwarding {parts} to myself.')
      parts.pop(0)

    if len(parts) == 0 or parts[0] == 'FINISHED!':
      print('Finished!')
    else:
      next_message = ':'.join(parts[1:])
      next_host = parts[0]
      print(f'Forwarding {next_message} to {parts[0]}')
      
      udp_socket.sendto(next_message.encode('utf-8'), (parts[0], ADDRESS_BOOK[next_host]))



if __name__ == "__main__":

  MY_NAME = socket.gethostname()
  RUNNING = True

  read_known_hosts_json()
  try:
    listen_for_incoming_messages()
  except KeyboardInterrupt:
    sys.exit(0)