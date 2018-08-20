import socket
import sys
import csv
import traceback
import queue
import datetime
import errno
from time import sleep
import os

'''
knownhosts.csv is of the form
Sender,Recipient,Port
'''
KNOWN_HOSTS_CSV = 'knownhosts.csv'

LOG_FILE = 'router_log.txt'

'''
SWITCHBOARD is a dict of the form
{
  PORT_NUMBER : {
    sender : HOST_NAME
    recipient : HOST_NAME
  }
  ...
}
'''
SWITCHBOARD = {}

#PORTS contains a list of all ports that we have to listen at.
PORTS = list()

# A queue determining message processing order.
QUEUE = queue.PriorityQueue()
# Global control variable
RUNNING = True


##################################################################################################################
# HELPER FUNCTIONS
##################################################################################################################
def convert_queue_obj_to_string(obj):
  str = '\tSENDER: {0}\n\tRECIPIENT: {1}\n\tPORT: {2}\n\tCONTENT: {3}'.format(obj['sender'], obj['recipient'], obj['port'], obj['message'])
  return str

def log(line):
  if os.path.exists(LOG_FILE):
    append_write = 'a' # append if already exists
  else:
      append_write = 'w' # make a new file if not
  with open(LOG_FILE, mode=append_write) as out_file:
    out_file.write(line + '\n')
    out_file.flush()

def build_switchboard():
  try:
    #Read the known_hosts.csv see the top of the file for the specification
    with open(KNOWN_HOSTS_CSV, 'r') as infile:
      reader = csv.reader(infile)
      for sender, recipient, port in reader:
        #Strip away trailing or leading whitespace
        sender = '{0}_Actual'.format(sender.strip())
        recipient = '{0}_Actual'.format(recipient.strip())
        port = port.strip()

        if not port in PORTS:
          PORTS.append(port)
        else:
          raise SystemExit("ERROR: port {0} was encountered twice. Please keep all ports independant.".format(port))

        SWITCHBOARD[port] = {}
        SWITCHBOARD[port]['sender'] = sender
        SWITCHBOARD[port]['recipient'] = recipient
        SWITCHBOARD[port]['connected'] = False


  except IOError as e:
    log("ERROR: Could not read {0}.".format(KNOWN_HOSTS_CSV))
    log(traceback.format_exc())
  except ValueError as e:
    log("ERROR: {0} was improperly formatted. Please include lines of the form (SENDER, RECIPIENT, PORT)".format(KNOWN_HOSTS_CSV))
    log(traceback.format_exc())
  except Exception as e:
    log('Encountered an error while reading and parsing {0}'.format(KNOWN_HOSTS_CSV))
    log(traceback.format_exc())


##################################################################################################################
# OUTGOING CONNECTION/QUEUE FUNCTIONS
##################################################################################################################

# def connect_outgoing_sockets():
#   for port in PORTS:
#     connect_outgoing_tcp_socket(port)


def connect_outgoing_tcp_socket(port):
  if SWITCHBOARD[port]['connected']:
    return 

  recipient = SWITCHBOARD[port]['recipient']
  server_address = (recipient, int(port))
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  #We catch errors one level up.
  log('Connecting to {0}'.format(server_address))
  sock.connect(server_address)
  log("Connected to {0}".format(server_address))
  SWITCHBOARD[port]['connected'] = True
  SWITCHBOARD[port]['outgoing_socket'] = sock

def send_outgoing_message(data):
  try:
    port = data['port']
    message = data['message']
    sock = SWITCHBOARD[port]['outgoing_socket']
  except:
    log(traceback.format_exc())
  try:
    log('Attempting to send the message...')
    sock.sendall(message)
    log('Message sent.')
  except:
    log(traceback.format_exc())
    SWITCHBOARD[port]['connected'] = False
    SWITCHBOARD[port]['outgoing_socket'].close()

def process_queue():
  still_going = True
  while still_going:
    try:
      now = datetime.datetime.now()
      #priority queue has no peek function due to threading issues.
      #  as a result, pull it off, check it, then put it back on.
      value = QUEUE.get_nowait()
      if value[0] <= now:
        log("It is time to process the message {0}".format(value[1]))
        send_outgoing_message(value[1])
      else:
        QUEUE.put(value)
        still_going = False
    except queue.Empty:
      still_going = False


##################################################################################################################
# INCOMING CONNECTION FUNCTIONS
##################################################################################################################

def connect_incoming_sockets():
  for port in PORTS:
    open_incoming_tcp_socket(port)

def open_incoming_tcp_socket(port):
  # Create a TCP/IP socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  #Bind the socket to the port
  server_address = ('', int(port))
  sock.bind(server_address)
  log('bound socket to {} port {}'.format(*server_address))
  #listen for at most 1 incoming connections at a time.
  sock.listen(1)
  #There is another way to accomplish this using select, but I think it is tcp exclusive.
  sock.setblocking(False)

  SWITCHBOARD[port]['incoming_socket'] = sock
  # sock.getsockname()[1] returns the port number.

def listen_to_sockets():
  for port in PORTS:

    try:
      if not 'connection' in SWITCHBOARD[port]:
        sock = SWITCHBOARD[port]['incoming_socket']
        connection, client_address = sock.accept()
        connection.setblocking(False)
        SWITCHBOARD[port]['connection'] = connection
        log('established connection with {0}'.format(port))
      else:
        connection = SWITCHBOARD[port]['connection']


      #TODO: May have to the max recvfrom size.
      #The recvfrom call will raise a OSError if there is nothing to recieve. 
      message, sender = connection.recvfrom(4096)
      log('recieved message {!r} on port {}'.format(message,port))
      #if we did not error:
      connect_outgoing_tcp_socket(port)
      recipient = SWITCHBOARD[port]['recipient']
      
      data = {
        'sender' : sender,
        'recipient' : recipient,
        'port' : port,
        'message' : message
      }
      log('Recieved the following:\n{0}\n'.format(convert_queue_obj_to_string(data)))

      #TODO allow rules to change what time is used for the priority queue.
      currentTime = datetime.datetime.now()
      tup = (currentTime, data)
      QUEUE.put(tup)
    except socket.timeout as e:
      #This is likely an acceptable error caused by non-blocking sockets having nothing to read.
      err = e.args[0]
      if err == 'timed out':
        log('no data')
      else:
        log('real error!')
        log(traceback.format_exc())
    except BlockingIOError as e:
      #print("Exception encountered. Shouldn't be a big deal.")
      #traceback.print_exc()
      pass
    except ConnectionRefusedError as e:
      #this means that connect_outgoing_tcp didn't work.
      # SWITCHBOARD[port]['incoming_socket'].close()
      log('Connection on outgoing channel not established. Message dropped.')
      log(traceback.format_exc())
      SWITCHBOARD[port]['connected'] = False
    except socket.gaierror as e:
      log("unable to connect to unknown/not set up entity.")
      log(traceback.format_exc())
    except Exception as e:
      log("ERROR: error listening to socket {0}".format(port))
      log(traceback.format_exc())


##################################################################################################################
# CONTROL FUNCTIONS
##################################################################################################################


#Do everything that should happen before multiprocessing kicks in.
def init():
  log('Booting up the router...')
  build_switchboard()
  #Only supporting tcp at the moment.
  log('Connecting incoming sockets...')
  connect_incoming_sockets()

def run():
  running = True
  sleep(1)
  log('Listening for incoming connections...')
  while RUNNING:
    listen_to_sockets()
    process_queue()


if __name__ == '__main__':
  init()
  run()

#First thing tomorrow:
#1) Connect up a brand new docker network of networks.
#2) Test until router is good.
#3) If possible, start work on getting things to run on submitty.

