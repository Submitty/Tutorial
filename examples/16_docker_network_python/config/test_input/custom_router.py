import socket
import sys
import csv
import traceback
import queue
import errno
from time import sleep
import os
import datetime
import random
from datetime import timedelta  

from submitty_router import submitty_router

#Custom router extends submitty_router
class custom_router(submitty_router):
  # The constructor for our custom router
  def __init__(self, seed=None, log_file='router_log.txt'):
    super().__init__(seed=seed, log_file=log_file)

  '''
  Override this function to manipuate student messages.
  '''
  def manipulate_recieved_message(self, sender, recipient, port, message, message_number):
    now = datetime.datetime.now()
    # The total time the program has been running as of right now.
    elapsed_time = now - self.execution_start_time
    # Use the time at which this message will be processed. Set to now initially.
    process_time = now
    # Leave blank to avoid outputting a message to the student on their sequence diagram
    message_to_student = None
    #If true, this message is entirely discarded.
    drop_me = False

    #EXAMPLE: modify one bit of the student's message in 1/10 messages before 2 seconds
    if random.randint(1,10) == 10 and elapsed_time.total_seconds() <= 2:
      # Convert the message int an array of bytes
      m_array = bytearray(message)
      # Determine which bit will be flipped
      flipbit = random.randint(0,len(m_array)-1 )
      # Flip the bit
      m_array[flipbit] = m_array[flipbit] + 1
      # Update the message
      message = bytes(m_array)
      # OPTIONAL: Tell the student that their message was corrupted via a message in their sequence diagram.
      message_to_student = "Corrupted"
    #EXAMPLE: delay the student message by up to 1 second in 1/10 messages
    elif random.randint(1,10) == 10:
      # Choose an amount of delay (in ms) between .1 and 1 second.
      milliseconds_dela = random.randint(100,1000)
      # Extend the processing time that far into the future
      process_time = process_time + timedelta(milliseconds=milliseconds_dela)
      # OPTIONAL: add a message to the student's sequence diagram that lets them know about the delay
      message_to_student = "Delayed {0} ms".format(milliseconds_dela)
    #We drop 1/10th of packets
    elif random.randint(1,10) == 10:
      drop_me = True

    data = {
      'sender' : sender,
      'recipient' : recipient,
      'port' : port,
      'message' : message,
      'message_to_student' : message_to_student,
      'drop_message' : drop_me
    }
    return (process_time, data)


#You must provide a main which is capable of running your router.
if __name__ == '__main__':
  router = custom_router()
  router.log("This is the custom router!")
  # submitty_router provides init and run functions for you to call.
  router.init()
  router.run()
    
