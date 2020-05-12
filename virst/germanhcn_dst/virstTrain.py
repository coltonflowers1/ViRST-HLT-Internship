from modules.bow import BoW_encoder
from modules.lstm_net import LSTM_net
from modules.bert_embed import UtteranceEmbed
from modules.virstActions import ActionTracker
from modules.virstDataUtils import Data
import modules.virstUtil as util
import modules.virstMemory_diff as memory
import random
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import sys
import json 
import pickle
import datetime as dt


class Trainer():
        def __init__(self, train_ratio=15/20, \
                                                        epochs=100, \
                                                        train_whole=True, \
                                                        ):

                self.train_ratio = train_ratio
                self.epochs = epochs
                

                #flag für fehleranalyse
                self.startCountingErrors = False
                self.count_all_one_eval = 0 
                self.count_all_one_train = 0 
                self.count_all_train = 0
                self.count_all_eval = 0
                #data.trainset = [(u,da_indx), ...]
                
                #HIER acttemps und size
                self.at = ActionTracker()
                self.action_templates = self.at.action_templates
                self.at.dialog_acts = self.at.dialog_acts
                self.at.dialog_act_ids = self.at.dialog_act_ids
                self.dataset, self.dialog_indices, self.other_da, self.other_da_id = self.at.get_data()
                self.action_size = self.at.action_size
                self.accs = []
                self.loss = []
                self.dev_accs =[]
                self.dev_loss=[]
                self.countErrors = Counter()
                self.countPredicitions = 0
                self.errorLog = {}
                self.highest_accuracy = 0
                #pickle.load(open("data/errors/errorLog.p", "rb"))
                if train_whole:
                        self.bow_enc = BoW_encoder()
                        self.emb = UtteranceEmbed()
                        #HIER numfeats
                        obs_size = self.emb.dim + self.bow_enc.vocab_size + self.action_size# + self.et.size_context_features
                        nb_hidden = 128
                        self.net = LSTM_net(obs_size,
                                                                        self.action_size,
                                                                        nb_hidden=nb_hidden)

        def train(self):
                print(self.other_da)
                print('\n:: training started', \
                                '\ntrain len :\t', round(len(self.dialog_indices) * self.train_ratio), \
                                '\ndev len :\t', len(self.dialog_indices) - round(len(self.dialog_indices) * self.train_ratio))
                print(self.epochs)
                random.shuffle(self.dialog_indices)
                self.dialog_indices_tr = self.dialog_indices[:round(len(self.dialog_indices) * self.train_ratio)]
                self.dialog_indices_dev = self.dialog_indices[round(len(self.dialog_indices) * self.train_ratio):]
                num_tr_examples = len(self.dialog_indices_tr)
                for j in range(self.epochs):

                       
                        #if j < 250:
                        #       self.startCountingErrors == True
                        # iterate through dialogs
                        
                        loss = 0.
                        random.shuffle(self.dialog_indices_tr)
                        for i, dialog_idx in enumerate(self.dialog_indices_tr):
                                # get start and end index
                                start, end = dialog_idx['start'], dialog_idx['end']
                                # train on dialogue
                                loss += self.dialog_train(self.dataset[start:end])
                                # print #iteration
                                sys.stdout.write('\r{}.[{}/{}]'.format(j+1, i+1, num_tr_examples))
                        print('\n\n:: {}.tr loss {}'.format(j+1, loss/num_tr_examples))
                        # evaluate every epoch
                        accuracy = self.evaluate()
                        self.accs.append(accuracy)
                        print(':: {}.dev accuracy {}\n'.format(j+1, accuracy))
                        #if accuracy > 0.98: # original threshold was 0.99
                        #       self.net.save() 
                        #       plt.plot(self.accs)
                        #       plt.xlabel("epochs")
                        #       plt.ylabel('accuracy')
                        #       plt.show()
                        #       break
                        if j == self.epochs-1:
                                #print("ACC: {}".format(float(sum(self.accs[349:]))/float(len(self.accs[249:]))))
                                #self.countErrors["ACCURACY"]= float(sum(self.accs[349:]))/float(len(self.accs[249:]))
                                #self.errorLog[dt.datetime.now()] = self.countErrors
                                #if accuracy > 0.95:
                                self.net.save()  # save any result after j iterations
                                #for key in self.countErrors.keys():
                        #               print("ACC: {}".format(float(sum(self.accs[349:]))/float(len(self.accs[249:]))))
                                #       self.countErrors[key] = self.countErrors[key]/ self.countPredicitions
                                #print(json.dumps(self.countErrors, indent=4))
                                #pickle.dump(self.accs, open("data/accuracies_trunc_09.p", "wb"))
                                #pickle.dump(self.loss, open("data/losses_trunc_09.p", "wb"))
                                #pickle.dump(self.at.dialog_acts, open("data/acts.p", "wb"))
                                #pickle.dump(self.at.dialog_act_ids, open("data/ids.p", "wb"))
                                #pickle.dump(self.dev_accs, open("data/dev_accuracies_00.p", "wb"))
                                #pickle.dump(self.dev_loss, open("data/dev_losses_00.p", "wb"))
                                print("Mean Accuracy: ", float(sum(self.accs[149:]))/float(len(self.accs[149:])))
                                print("Predictions LSTM Training: ", self.count_all_one_train)
                                print("LSTM ratio Training {}".format(float(self.count_all_one_train)/float(self.count_all_train)))
                                print("Predictions LSTM Evaluation: ", self.count_all_one_eval)
                                print("LSTM ratio Evaluation {}".format(float(self.count_all_one_eval)/float(self.count_all_eval)))


                                
                                plt.plot(self.accs)
                                plt.xlabel("epochs")
                                plt.ylabel('loss')
                                plt.show()
                
                                break


        def dialog_train(self, dialog):
                self.at.reset_action_mask()
                self.net.reset_state()
                try:
                        self.at.set_exercise(self.at.get_dialog_act_id(dialog[0][1],action_template=True))
                except:
                        print(dialog[0][1])
                        exit()
                self.at.automaton.reset_current_state()
                self.at.memory.reset_memory(self.at.exercise)
                loss = 0.
                self.at.initialize_am()
                self.at.automaton.reset_current_state()
                #error_code = re.compile(r"\[01\]+S")
                
                for (u,r) in dialog:
                        if r.startswith("intro"):
                                r = "intro"
                        r = self.at.get_dialog_act_id(r)
                        #print(r)
                        
                        u_emb = self.emb.encode(u)#HIER
                        #print('\nEmbedded Utterance, W2V:\n\n', u_emb)
                        u_bow = self.bow_enc.encode(u)#HIER
                        self.count_all_one_train += 1
                        
                        action_mask = self.at.am
                        # forward propagation
                        # train step
                        
                        features = np.concatenate((u_emb, u_bow, action_mask), axis=0)
                        lossValue , prediction = self.net.train_step(features, r, action_mask)
                        #current_state = self.at.automaton.current_state
                        #list_of_interest = [self.other_da[i] for i in range(len(self.other_da)) if action_mask[i] == 1]
                        #print("action mask: ",list_of_interest,"\ncurrent_state:",current_state.name,"\nprediction: ", self.other_da[prediction])
                        self.at.automaton.current_state,_ = self.at.walk(u, prediction)
                        #print(prediction)
                        #print(self.at.automaton.current_state.name)
                        
                        self.count_all_train +=1
                        #print("predicted: ", self.at.dialog_acts[prediction])
                        loss += lossValue
                        #loss += self.net.train_step(features, r)
                self.loss.append(loss/len(dialog))
                return loss/len(dialog)
        def evaluate(self):
                self.net.reset_state()
                dialog_accuracy = 0
                dialog_loss = 0
                errors = []
                
                for dialog_idx in self.dialog_indices_dev:
                        start, end = dialog_idx['start'], dialog_idx['end']
                        dialog = self.dataset[start:end]
                        num_dev_examples = len(self.dialog_indices_dev)
                        # reset network
                        self.net.reset_state()
                        try:
                                self.at.set_exercise(self.at.get_dialog_act_id(dialog[0][1],action_template=True))
                        except:
                                print(dialog)
                                exit()
                        self.at.memory.reset_memory(self.at.exercise)
                        self.at.initialize_am()
                        # iterate through dialog
                        correct_examples = 0
                        #last_action = np.zeros([self.action_size], dtype=np.float32)
                        prev_prediction = -1
                        self.at.automaton.reset_current_state()
                        prev_state = ""
                        i = 0
                        loss = 0
                        for (u,r) in dialog:
                                if r.startswith("intro"):
                                        r = "intro"
                                r = self.at.get_dialog_act_id(r)
                                i +=1
                                u_emb = self.emb.encode(u)#HIER
                                #print('\nEmbedded Utterance, W2V:\n\n', u_emb)
                                u_bow = self.bow_enc.encode(u)#HIER
                                prev_state = self.at.automaton.current_state.name
                                action_mask = self.at.am
                                features = np.concatenate((u_emb, u_bow, action_mask), axis=0)
                                prediction= self.net.forward(features,  action_mask, r)
                                #current_state = self.at.automaton.current_state
                                #list_of_interest = [self.other_da[i] for i in range(len(self.other_da)) if action_mask[i] == 1]
                                #print("action mask: ",list_of_interest,"\ncurrent_state:",current_state.name,"\nprediction: ", self.other_da[prediction])
                                self.at.automaton.current_state,_ = self.at.walk(u,prediction)
                                #self.count_all_eval +=1
                                #if prediction != r:
                                #       print("FROM: {}, with: {}, TO: {}, predicted: {}".format(prev_state, self.at.automaton.get_utterance_type(u), self.at.automaton.current_state.name, self.at.dialog_acts[prediction]))
                                #if self.startCountingErrors and prediction != r:
                                #       self.countErrors[self.at.dialog_acts[prediction] + ":" + self.at.dialog_acts[r]] +=1
                                #if self.startCountingErrors:
                                #       self.countPredicitions +=1
                                if prediction != r:
                                        errors.append("EXERCISE: {}, step {}, Previous State: {}, Previous Act: {}, Prediction: {} Actual Da: {}, Utterance: {}, Symbol: {}".format(self.at.exercise, i, prev_state,  self.at.dialog_acts[prev_prediction], self.at.dialog_acts[prediction], self.at.dialog_acts[r], u, self.at.automaton.get_utterance_type(u)))
                                prev_prediction = r
                                #print("Prediction: {} Actual Da: {}".format(self.at.dialog_acts[prediction],self.at.dialog_acts[r]))
                                #self.at.memory.update(prediction)
                                #last_action= np.zeros([self.action_size], dtype=np.float32)
                                #last_action[prediction-1] = 1

                                #prediction = self.net.forward(features)
                                
                                #print("predicted: ", self.at.dialog_acts[prediction])
                                #if prediction == r:
                                #       print(self.at.dialog_acts[r])
                                correct_examples += int(prediction == r)
                                self.count_all_eval += 1
                                #loss += loss_value[0]
                        # get dialog accuracy
                        dialog_accuracy += correct_examples/len(dialog)
                        #dialog_loss += loss / len(dialog)
                        
                if self.highest_accuracy > 0 and self.highest_accuracy -(dialog_accuracy/num_dev_examples) > 0.2:
                        for e in errors:
                                print(e)
                print(self.highest_accuracy -(dialog_accuracy/num_dev_examples))
                if self.highest_accuracy < dialog_accuracy/num_dev_examples:
                        self.highest_accuracy = dialog_accuracy/num_dev_examples
                self.dev_loss.append(dialog_loss/num_dev_examples)
                self.dev_accs.append(dialog_accuracy/num_dev_examples)
                print("dev_loss: {}".format(dialog_loss/num_dev_examples))
                return dialog_accuracy/num_dev_examples

if __name__ == '__main__':
        # setup trainer
        trainer = Trainer()
        # start training
        trainer.train()
