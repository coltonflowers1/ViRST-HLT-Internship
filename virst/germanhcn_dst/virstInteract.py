from modules.virstEntities import EntityTracker
from modules.bow import BoW_encoder
from  modules.lstm_net import LSTM_net
from modules.bert_embed import UtteranceEmbed
from modules.virstActions import ActionTracker
from modules.virstDataUtils import Data
import modules.virstUtil as util

from modules.message.format.DialogueInternalMessageFormat import SystemOutputMessage, SystemOutputData, UserInputMessage, \
		MessageType, to_enum, user_input_message_from_dict
from modules.message.format.SharedConfig import Config
from modules.message.request_handler_thread import request_worker

import numpy as np
import sys
import aiml
import random
import re
import pickle
import json
import time
import threading
import zmq

class InteractiveSession():

        def __init__(self):
                self.bow_enc = BoW_encoder()
                self.emb = UtteranceEmbed()
                self.at = ActionTracker(interact=True)
                print(self.at.dialog_acts)
                _,_, self.other_da, self.other_da_id = self.at.get_data()
                self.action_templates = self.at.action_templates
                self.action_size = self.at.action_size
                #self.responses = [r[0] for r in self.at.responses]
                #print(self.emb.dim , self.bow_enc.vocab_size , self.action_size)
                self.obs_size = self.emb.dim + self.bow_enc.vocab_size + self.action_size
                nb_hidden = 128
                self.exercises = list(self.at.action_templates.keys())
                self.net = LSTM_net(obs_size=self.obs_size,
                                                        action_size=self.action_size,
                                                        nb_hidden=nb_hidden)
                # restore checkpoint
                self.net.restore()

                # setup remote interaction via zeromq
                context = zmq.Context.instance()
                # PUB socket for sending system-output
                self.pubSocket: zmq.Socket = context.socket(zmq.PUB)
                self.pubSocket.bind(Config.SYSTEM_OUTPUT_ADDR)
                # SUB socket for receiving user-input
                self.subSocket: zmq.Socket = context.socket(zmq.SUB)
                self.subSocket.connect(Config.USER_INPUT_ADDR)
                self.subSocket.setsockopt_string(zmq.SUBSCRIBE, Config.USER_INPUT_SUBJECT)
                self.lastOutputMessage: str = None
                self.requestHandler: threading.Thread = None
                self.requestInterrupted: threading.Lock = None

        def has_exercise(self, exercise_name: str) -> bool:
                return exercise_name in self.at.action_templates

        def get_current_exercise(self) -> str:
                return self.at.exercise

        def send(self, message, utteranceType, state, dialogAct):
                print(">>", message)
                data = SystemOutputData(text=message, utterance_type=utteranceType, state=state, dialogue_act=dialogAct)
                msg = SystemOutputMessage(type=MessageType.OUTPUT, timestamp=int(time.time() * 1000), data=data)
                jsonMsg = json.dumps(msg.to_dict())
                self.lastOutputMessage = jsonMsg;
                rawMsg = "%s %s" % (to_enum(MessageType, msg.type), jsonMsg)
                # print("  ", rawMsg)#DEBUG
                self.pubSocket.send_string(rawMsg)

        def receive(self) -> 'UserInputMessage':
                rawMsg = self.subSocket.recv_string()
                # print("  ", rawMsg)#DEBUG
                # FIXME detect & handle when message has other type than "input"
                # TODO handle message types other than "input"
                msgTypeStr = to_enum(MessageType, MessageType.INPUT)
                # extract JSON message by removing subject/subscription string from beginning of message:
                msgStr = rawMsg.replace(msgTypeStr, "", 1).strip()
                return user_input_message_from_dict(json.loads(msgStr))

        def start_processing_requests(self, verbose: bool = False):
                self.stop_processing_requests()
                self.requestInterrupted = threading.Lock()
                self.requestInterrupted.acquire()
                self.requestHandler = threading.Thread(target=request_worker, args=(
                Config.QUERY_SYSTEM_OUTPUT_ADDR, self, self.requestInterrupted, verbose))
                self.requestHandler.start()

        def stop_processing_requests(self):
                if self.requestInterrupted is not None and self.requestHandler is not None and self.requestHandler.isAlive():
                        self.requestInterrupted.release()
                        # print("should stop request_worker thread now!")
                        self.requestHandler.join()
                        print("stopped request_worker thread.")

        def interact_anew(self, verbose, update, out_file, new_state_name: str = None):
                prev_prediction = -1
                self.net.reset_state()
                if new_state_name is None:
                    new_state_name = random.choice(self.exercises)
                self.at.set_exercise_string(new_state_name)
                self.at.memory.reset_memory(self.at.exercise)
                self.at.initialize_am()

                u = "start"
                if verbose == True:
                        print("\n*******************\nÄUßERUNGSTYP: ", self.at.automaton.get_utterance_type(u))

                action_mask = self.at.am
                u_emb = self.emb.encode(u)  # HIER
                u_bow = self.bow_enc.encode(u)  # HIER
                features = np.concatenate((u_emb, u_bow, action_mask), axis=0)
                # forward
                prediction = self.net.forward(features, action_mask, self.other_da, print_top=True)
                self.at.automaton.current_state, response = self.at.walk(u, prediction)
                prev_prediction = prediction

                if verbose == True:
                        print("AKTUELLER ZUSTAND: ", self.at.automaton.current_state.name, "\nDIALOGAKT: ",
                              self.other_da[prediction],
                              "\n*******************\n")  # print("CURRENT Exercise: ", self.at.exercise)

                # self.net.train_step(features, prediction, action_mask)
                # response = self.at.get_text(prediction)
                self.send(response, self.at.automaton.get_utterance_type(u), self.at.automaton.current_state.name,
                          self.at.dialog_acts[prediction])  # print('>>', response)
                if out_file:
                        out_file.write(u + '\t' + response + '\t' + self.other_da[prediction] + '\n')
                return prev_prediction

        def interact(self,verbose, update, write_to_file):
                print("How do you do? I'm glad you're here. Let's do some exercises together.")
                # open file to write around here
                # only if write_to_file !
                with open('data/dialogs_from_interaction', 'a') as out:
                        with open("data/utterances_from_interaction", "a") as uttout:
                                self.start_processing_requests(verbose)
                                out_file = None
                                if write_to_file:
                                        out_file = out
                                prev_prediction = self.interact_anew(verbose, update, out_file)
                                # begin interaction loop
                                while True:
                                        if verbose == True:
                                                print([self.other_da[i] for i in range(len(self.at.am)) if self.at.am[i] == 1])
                                        #print("prediction: ",self.at.dialog_acts[prediction])
                                        #print("response: ",response)

                                        # get input from user; utterance isn't saved!
                                        message = self.receive()  # u = input(':: ')
                                        u = message.data.strip()
                                        print(":: %s" % (u))

                                        # check if user wants to begin new session
                                        if u == 'clear' or u == 'reset' or u == 'restart' or u == 'von vorne' or u == 'neustart':
                                                if write_to_file:
                                                    out.write("WARNING: Interaction was reset.\n\n")
                                                prev_prediction = self.interact_anew(verbose, update, out_file)
                                                if write_to_file:
                                                    uttout.write(u + "\t" + self.at.automaton.get_utterance_type(u)+"\n")

                                        elif self.other_da[prev_prediction] in ["closing","finish"]:
                                                if write_to_file:
                                                    out.write('\n')
                                                prev_prediction = self.interact_anew(verbose, update, out_file)

                                        # check for exit command
                                        elif u == 'exit'  or u == 'quit':

                                                if update == True:
                                                        self.net.save()
                                                self.send('Ok, wir brechen ab. Bis zum nächsten Mal!', 'EXIT COMMAND',
                                                          self.at.automaton.current_state.name,
                                                          "UNKNOWN")  # print('>> Ok, wir brechen ab. Bis zum nächsten Mal!')
                                                if write_to_file:
                                                        out.write("WARNING: Dialog may not be finished.\n")
                                                break

                                        else:
                                                if u == "\n" or u == "":
                                                        u = '<SILENCE>'
                                                #self.at.reset_action_mask()

                                                if  self.at.automaton.current_state.name == "all_one":
                                                        if verbose == True:
                                                                print("\n*******************\nÄUßERUNGSTYP: ", self.at.automaton.get_utterance_type(u))
                                                        ##print(self.at.automaton.current_state.name, self.at.dialog_acts[prev_prediction])
                                                else:
                                                        if verbose == True:
                                                                print("\n*******************\nÄUßERUNGSTYP: ", self.at.automaton.get_utterance_type(u))
                                                action_mask = self.at.am
                                                u_emb = self.emb.encode(u)#HIER
                                                u_bow = self.bow_enc.encode(u)#HIER
                                                features = np.concatenate((u_emb, u_bow, action_mask), axis=0)
                                                # forward


                                                prediction = self.net.forward(features, action_mask, self.other_da, print_top=True)
                                                self.at.automaton.current_state, response = self.at.walk(u,prediction)
                                                if prediction != "all_one":
                                                        prev_prediction = prediction

                                                #self.at.memory.update(prediction)
                                                if verbose == True:
                                                        print("AKTUELLER ZUSTAND: ", self.at.automaton.current_state.name, "\nDIALOGAKT: ", self.other_da[prediction], "\n*******************\n")                         #print("CURRENT Exercise: ", self.at.exercise)


                                                self.net.train_step(features, prediction, action_mask)
                                                self.send(response, self.at.automaton.get_utterance_type(u),
                                                          self.at.automaton.current_state.name,
                                                          self.at.dialog_acts[prediction]) # print('>>', response)
                                                if write_to_file:
                                                        out.write(u + '\t'+ response + '\t' + self.other_da[prediction] + '\n')
                                                        uttout.write(u + "\t" + self.at.automaton.get_utterance_type(u)+"\n")
                                if write_to_file:
                                        out.write('\n')
                                self.stop_processing_requests()


if __name__ == '__main__':
        # create interactive session
        isess = InteractiveSession()
        # begin interaction
        isess.interact()
