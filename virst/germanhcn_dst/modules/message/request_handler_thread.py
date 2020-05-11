
import json
import time
from modules.message.format.DialogueInternalMessageFormat import SystemOutputMessage, \
		GeneralMessage, ErrorMessage, ErrorData, ErrorType, MessageType, \
		SystemDialogueMessage, SystemDialogueData, SystemDialogueOperation, \
		request_message_from_dict, system_dialogue_data_from_dict

import zmq
import threading

# WORKAROUND for type-hint support without actually importing InteractiveSession (which would cause cyclic dependencies)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from virstInteract import InteractiveSession


def request_worker(request_url, message_handler: 'InteractiveSession', interrupted: threading.Lock, verbose: bool = False):
	"""
		thread/worker for receiving (and replying to) request:
		handles requests for
			* {"type": "output"} -> send reply with current OutputMessage
	"""
	context = zmq.Context.instance()
	socket = context.socket(zmq.REP)
	socket.bind(request_url)
	if verbose:
		print("##  initialized request/reply socket ", request_url, "... ")  # DEBUG
	while not interrupted.acquire(blocking=False):
		res = socket.poll(0.5)  # wait 0.5 seconds for an event, then loop & check if interrupted was set
		if res != 0:
			# print("##  receiveRequest.poll -> ", res)
			raw_msg = socket.recv_string()
			if verbose:
				print("##  receiveRequest -> ", raw_msg)  # DEBUG
			try:
				msg: GeneralMessage = request_message_from_dict(json.loads(raw_msg))
				reply_str: str = None
				reply_msg = None
				if verbose:
					print("##  receiveRequest -> ", msg)  # DEBUG
				if msg.type == MessageType.OUTPUT:
					if verbose:
						print("##  receiveRequest: current system output requested...")  # DEBUG
					if message_handler.lastOutputMessage is not None:
						reply_str = message_handler.lastOutputMessage;  # TODO should add mechanism to invalidate message when neccessary (e.g. (?) new exercise started but no output was sent yet)
					else:  # NOTE if no output-message is available upon REQ/REP, the next output-message will be sent via PUB/SUB channel (when it becomes available)
						reply = SystemOutputMessage(type=MessageType.OUTPUT, timestamp=int(time.time() * 1000), data=None)
						reply_str = json.dumps(reply.to_dict())
				elif msg.type == MessageType.DIALOGUE:
					if verbose:
						print("##  receiveRequest: system dialogue(s) queried...", msg.data)  # DEBUG
					dlg_req_data = system_dialogue_data_from_dict(msg.data)
					if verbose:
						print("##  receiveRequest: system dialogue operation: ", dlg_req_data)  # DEBUG
					if dlg_req_data.operation == SystemDialogueOperation.LIST:  # FIXME define proper query interface!!!
						if verbose:
							print("##  receiveRequest: requested list of exercises...")
						reply_msg = SystemDialogueMessage(type=MessageType.DIALOGUE, timestamp=int(time.time() * 1000),
														  data=SystemDialogueData(
															  operation=SystemDialogueOperation.LIST,
															  dialogues=message_handler.exercises, dialogue=None))

					elif dlg_req_data.operation == SystemDialogueOperation.SET:  # FIXME TODO set to
						if verbose:
							print("##  receiveRequest: TODO set exercise to "+dlg_req_data.dialogue)
						if dlg_req_data.dialogue is None or message_handler.has_exercise(dlg_req_data.dialogue) is not True:
							if verbose:
								print("##  receiveRequest: FAILED to set exercise to "+dlg_req_data.dialogue+": does not exists!")
							reply_msg = ErrorMessage(type=MessageType.ERROR, timestamp=int(time.time() * 1000),
													 data=ErrorData(error=ErrorType.UNKNOWN_TYPE,
																	message="unknown request " + raw_msg))
						else:
							if verbose:
								print("##  receiveRequest: TEST FIXME setting exercise to "+dlg_req_data.dialogue+"...")
							message_handler.interact_anew(False, None, None, dlg_req_data.dialogue)  # FIXME need to "message" other thread instead of changing form here! FIXME need to correctly set verbose and out_file!!!
							reply_msg = SystemDialogueMessage(type=MessageType.DIALOGUE,
															  timestamp=int(time.time() * 1000),
															  data=SystemDialogueData(
																  operation=SystemDialogueOperation.SET, dialogues=None,
																  dialogue=dlg_req_data.dialogue))


					elif dlg_req_data.operation == SystemDialogueOperation.GET:  # FIXME TODO set to
						curr_exercise = message_handler.get_current_exercise();
						if verbose:
							print("##  receiveRequest: get/return current exercise: ", curr_exercise)
						reply_msg = SystemDialogueMessage(type=MessageType.DIALOGUE, timestamp=int(time.time() * 1000),
														  data=SystemDialogueData(operation=SystemDialogueOperation.GET,
																				  dialogues=None,
																				  dialogue=curr_exercise))

				if reply_str is None and reply_msg is None:
					print("##  receiveRequest: unknown or unsupported request "+msg.type+", creating error reply")
					reply_msg = ErrorMessage(type=MessageType.ERROR, timestamp=int(time.time() * 1000),
											 data=ErrorData(error=ErrorType.UNKNOWN_TYPE,
															message="unknown request " + raw_msg))

				if reply_str is None and reply_msg is not None:
					reply_str = json.dumps(reply_msg.to_dict())

			except BaseException as exc:
				print("##  EXC", exc)
				reply_msg = ErrorMessage(type=MessageType.ERROR, timestamp=int(time.time() * 1000),
										 data=ErrorData(error=ErrorType.FORMAT,
														message="unknown request message format: " + raw_msg))
				reply_str = json.dumps(reply_msg.to_dict())

			if verbose:
				print("##  sendReply -> ", reply_str)  # DEBUG
			socket.send_string(reply_str)

	# end while: clean up socket
	socket.close()
	if verbose:
		print("## request_worker thread finished.")
