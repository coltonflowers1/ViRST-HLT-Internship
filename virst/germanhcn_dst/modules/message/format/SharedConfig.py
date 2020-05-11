
#----------------------
# AUTO GENERATED:
#     Generated using simple-consts-generator v1.3.0
# DO NOT CHANGE MANUALLY
#----------------------

"""shared (i.e. "system-wide") configuration/settings for ViRST components"""
class Config(object):
  __slots__ = ()
  def __setattr__(self, *_):
    pass
  
  """publish/subscribe port number for DialogueSystem messages

@see [[HEARTRATE_SUBJECT]]
@see [[HrMessage]]

@see [[STRESS_SUBJECT]]
@see [[StressMessage]]"""
  DIALOGUE_SYSTEM_ADDR = "tcp://127.0.0.1:3322"
  
  """request/reply port number for DialogueSystem messages

@see [[HEARTRATE_SUBJECT]]
@see [[HrMessage]]

@see [[STRESS_SUBJECT]]
@see [[StressMessage]]"""
  QUERY_DIALOGUE_SYSTEM_ADDR = "tcp://127.0.0.1:3323"
  
  """publish/subscribe port number for VR-App messages"""
  VR_APP_ADDR = "tcp://127.0.0.1:12345"
  
  """request/reply port number for VR-App messages"""
  QUERY_VR_APP_ADDR = "tcp://127.0.0.1:12346"
  
  """publish/subscribe port number for user-input (e.g. via typing-to-console or ASR results)

@see [[USER_INPUT_SUBJECT]]
@see [[UserInputMessage]]"""
  USER_INPUT_ADDR = "tcp://127.0.0.1:4422"
  
  """request/reply port number for user-input (e.g. via typing-to-console or ASR results)

@see [[USER_INPUT_SUBJECT]]
@see [[UserInputMessage]]"""
  QUERY_USER_INPUT_ADDR = "tcp://127.0.0.1:4423"
  
  """publish/subscribe port number for system-output (e.g. for printing-to-console or TTS)

@see [[SYSTEM_OUTPUT_SUBJECT]]
@see [[SystemOutputMessage]]"""
  SYSTEM_OUTPUT_ADDR = "tcp://127.0.0.1:5522"
  
  """request/reply port number for system-output (e.g. for printing-to-console or TTS)

@see [[SYSTEM_OUTPUT_SUBJECT]]
@see [[SystemOutputMessage]]"""
  QUERY_SYSTEM_OUTPUT_ADDR = "tcp://127.0.0.1:5523"
  
  """delay (in ms) between PUB'lishing test messages

@TJS-type integer"""
  TEST_SEND_DELAY = 1000
  
  """subject (or request type) for heart rate messages

@see [[HrMessage]]"""
  HEARTRATE_SUBJECT = "heartrate"
  
  """subject (or request type) for stress level messages

@see [[StressMessage]]"""
  STRESS_SUBJECT = "stress"
  
  """subject (or request type) for user-input messages

@see [[UserInputMessage]]"""
  USER_INPUT_SUBJECT = "input"
  
  """subject (or request type) for system output messages

@see [[SystemOutputMessage]]"""
  SYSTEM_OUTPUT_SUBJECT = "output"
  
  
Config = Config()
