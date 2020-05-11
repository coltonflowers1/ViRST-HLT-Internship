#adapted from example for non-blocking reading from stdin:
#https://repolinux.wordpress.com/2012/10/09/non-blocking-read-from-stdin-in-python/

"""Store input in a queue as soon as it arrives, and work on
it as soon as possible. Do something with untreated input if
the user interrupts. Do other stuff if idle waiting for
input."""

import sys
import threading
import queue

import zmq#MOD
import json#MOD
import time#MOD
from modules.message.format.DialogueInternalMessageFormat import SystemOutputMessage, UserInputMessage, \
  RequestMessage, SystemDialogueMessage, SystemDialogueData, SystemDialogueOperation, MessageType, \
  to_enum, system_output_message_from_dict, system_dialogue_message_from_dict#MOD
from modules.message.format.SharedConfig import Config#MOD

#MOD START
# setup remote interaction via zeromq
context = zmq.Context()
# PUB socket for sending user-input
pubSocket = context.socket(zmq.PUB)
pubSocket.bind(Config.USER_INPUT_ADDR)
# SUB socket for receiving system-output
subSocket = context.socket(zmq.SUB)
subSocket.connect(Config.SYSTEM_OUTPUT_ADDR)
subSocket.setsockopt_string(zmq.SUBSCRIBE, Config.SYSTEM_OUTPUT_SUBJECT)
# REQ socket for querying current system-output
querySocket = context.socket(zmq.REQ)
querySocket.connect(Config.QUERY_SYSTEM_OUTPUT_ADDR)
#MOD END


timeout = 0.5 # seconds
last_work_time = time.time()

def treat_input(linein):
  global last_work_time
  send_user_input_message(linein)
  last_work_time = time.time()

def input_cleanup():
  print()
  while not input_queue.empty():
    line = input_queue.get()
    print("Didn't get to work on this line:", line, end='')

# will hold all input read, until the work thread has chance
# to deal with it
input_queue = queue.Queue()

# will signal to the work thread that it should exit when
# it finishes working on the currently available input
no_more_input = threading.Lock()
no_more_input.acquire()

no_more_input2 = threading.Lock()#MOD
no_more_input2.acquire()#MOD

# will signal to the work thread that it should exit even if
# there's still input available
interrupted = threading.Lock()
interrupted.acquire()

interrupted2 = threading.Lock()#MOD
interrupted2.acquire()#MOD

# work thread' loop: work on available input until main
# thread exits
def treat_input_loop():
  while not interrupted.acquire(blocking=False):
    try:
      treat_input(input_queue.get(timeout=timeout))
    except queue.Empty:
      # if no more input, exit
      if no_more_input.acquire(blocking=False):
        break
    #  else:
    #    idle_work()
  print('INPUT User-Input loop is done.')
  pubSocket.close()

# work thread' loop: work on available input until main
# thread exits
def treat_output_loop():
  list = query_exercise_list_blocking()
  if verbose:
    print("  [exercise list]: ", list.data)
  if verbose:
    print("retrieving current system output message...")
  msg = query_current_system_output_message_blocking()
  first_msg_time = None
  if msg.data is not None and msg.data.text is not None:
    first_msg_time = msg.timestamp
    print("\n>>", msg.data.text)
  elif verbose:
    print("no current system output message yet, waiting for dialogue system...")
  while not interrupted2.acquire(blocking=False):
    try:
      msg = receive_system_output_message()
      if msg.timestamp is None or msg.timestamp != first_msg_time:
        print("\n>>", msg.data.text)
    except zmq.ZMQError:
      # if no more input, exit
      if no_more_input2.acquire(blocking=False):
        break
      time.sleep(timeout)
  print('RECEIVE System-Output loop is done.')
  subSocket.close()
  querySocket.close()

def query_current_system_output_message_blocking() -> 'SystemOutputMessage':
  query = RequestMessage(type=MessageType.OUTPUT,timestamp=int(time.time() * 1000), data=None)
  jsonQuery = json.dumps(query.to_dict())
  if verbose:
    print("  [query current system output]: ", jsonQuery)
  querySocket.send_string(jsonQuery)
  sysOutput = querySocket.recv_string()
  if verbose:
    print("  [received current system output]: ", sysOutput)
  return system_output_message_from_dict(json.loads(sysOutput.strip()))

def query_exercise_list_blocking() -> 'SystemDialogueMessage':
  query = SystemDialogueMessage(type=MessageType.DIALOGUE,timestamp=int(time.time() * 1000), data=SystemDialogueData(operation=SystemDialogueOperation.LIST,dialogues=None,dialogue=None))
  jsonQuery = json.dumps(query.to_dict())
  if verbose:
    print("  [query exercise list]: ", jsonQuery)
  querySocket.send_string(jsonQuery)
  sysOutput = querySocket.recv_string()
  if verbose:
    print("  [received exercise list]")
  return system_dialogue_message_from_dict(json.loads(sysOutput.strip()))

def receive_system_output_message() -> 'SystemOutputMessage':
  sysOutput = subSocket.recv_string(flags=zmq.NOBLOCK)
  if verbose:
    print("  [received system output]: ", sysOutput)
  # FIXME detect & handle when message has other type than "input"
  # TODO handle message types other than "input"
  msgTypeStr = to_enum(MessageType, MessageType.OUTPUT)
  jsonMsg = sysOutput.replace(msgTypeStr, "", 1).strip()
  return system_output_message_from_dict(json.loads(jsonMsg))

def send_user_input_message(userInputString):
  msg = UserInputMessage(type=MessageType.INPUT, timestamp=int(time.time() * 1000), data=userInputString)
  jsonMsg = json.dumps(msg.to_dict())
  rawMsg = "%s %s" % (to_enum(MessageType, msg.type), jsonMsg)
  if verbose:
    print("  [sending user input]: ", rawMsg)
  pubSocket.send_string(rawMsg)

# MOD:
# commandline parameters:
verbose = False
# parse cmd params:
for arg in sys.argv[1:]:
  if arg == "verbose":
    verbose = True

if verbose:
  print("using verbose mode")
  print("Current libzmq version is %s" % zmq.zmq_version())
  print("Current  pyzmq version is %s" % zmq.__version__)
else:
  print("use command line parameter \"verbose\" for detailed output")

print("Starting Console %s...\n" % ("client"))
# END MOD

work_thread = threading.Thread(target=treat_input_loop)
work_thread.start()

work_thread2 = threading.Thread(target=treat_output_loop)
work_thread2.start()

# main loop: stuff input in the queue until there's either
# no more input, or the program gets interrupted
try:
  for line in sys.stdin:
    if line: # optional: skipping empty lines
      input_queue.put(line)

  # inform work loop that there will be no new input and it
  # can exit when done
  no_more_input.release()
  no_more_input2.release()

  # wait for work thread to finish
  work_thread.join()
  work_thread2.join()

except KeyboardInterrupt:
    interrupted.release()
    interrupted2.release()
    input_cleanup()

print('Main loop is done.')
