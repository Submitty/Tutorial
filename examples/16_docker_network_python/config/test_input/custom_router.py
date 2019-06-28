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
  Override this function to manipulate student messages.

  data has the following keys:
  1. sender: The node that sent the message.
  2. recipient: The node to which the message is bound
  3. port: The port on which the message was received and will be sent.
  4. message: The message that was passed.
  5. message_number: The sequence number of the message as it was received by the router.
  6. receipt_time: The time at which the message was received by the router (sent by the sender)
  7. forward_time: The time at which the message is scheduled to be forwarded by the router to the recipient.
     Defaults to be equivalent to receipt_time.
  8. drop_message: A boolean, which, if true, states that the message will be dropped.
     Defaults to false.
  9. diagram_label: A label for this message on the sequence diagram generated by this testcase
     Defaults to None

  current_test_duration defines how long the test has currently been running as a timedelta object.
  '''
  def manipulate_received_message(self, data, current_test_duration):
    #EXAMPLE: modify one bit of the student's message in 1/10 messages before 2 seconds
    if random.randint(1,10) == 10 and current_test_duration.total_seconds() <= 2:
      # Convert the message int an array of bytes
      m_array = bytearray(data['message'])

      # Determine which bit will be flipped
      flipbit = random.randint(0,len(m_array)-1 )

      # Flip the bit
      m_array[flipbit] = m_array[flipbit] + 1

      # Update the message
      data['message'] = bytes(m_array)

      # OPTIONAL: Tell the student that their message was corrupted via a message in their sequence diagram.
      data['diagram_label'] = "Corrupted"

    #EXAMPLE: delay the student message by up to 1 second in 1/10 messages
    elif random.randint(1,10) == 10:
      # Choose an amount of delay (in ms) between .1 and 1 second.
      milliseconds_dela = random.randint(100,1000)

      # Extend the processing time that far into the future
      data['forward_time'] = data['forward_time'] + timedelta(milliseconds=milliseconds_dela)

      # OPTIONAL: add a message to the student's sequence diagram that lets them know about the delay
       data['diagram_label'] = "Delayed {0} ms".format(milliseconds_dela)

    #We drop 1/10th of packets
    elif random.randint(1,10) == 10:
      data['drop_message'] = True

    return data


#You must provide a main which is capable of running your router.
if __name__ == '__main__':
  #Construct an instance of our router
  router = custom_router()

  router.log("This is the custom router!")

  # submitty_router provides init and run functions for you to call.
  router.init()
  router.run()
    
