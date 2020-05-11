import modules.virstUtil as util
import modules.virstEntities as ET
'''
        Train
        1. Prepare training examples from dataset with new labeling schema
                1.1 Format 'utterance \t action_template_id\n'
        2. Prepare dev set
        3. Organize trainset as list of dialogues
'''

class Data():

        def __init__(self):
                #Liste von etity-objekten 
                # {"execise":"Dehnübung","text": "Bla", "participants":{}, "participants_pos": {}}
        
                # prepare data
                self.trainset = self.prepare_data()
        def prepare_data(self):
                # get dialogs from file
                dialogs, dialog_indices = util.read_dialogs(with_indices=True,dialogs='data/tagged_virst_train_new_summary_en_diff.txt')
                #dialogs = [[utterance, response, tag], [utterance,response, tag]]
                # get utterances: liste von Äußerungen
                utterances = util.get_utterances(dialogs)               
                # get responses: Liste von Antworten 
                responses = util.get_responses(dialogs)
                self.dialog_acts = util.get_dialog_acts(dialogs)
                trainset = []
                for u,d in zip(utterances, self.dialog_acts):
                        trainset.append((u,d))
                self.dialog_acts_order = list(set(["intro" if dialog_act.startswith("intro") else dialog_act for dialog_act in util.get_dialog_acts(dialogs) ]))
                self.dialog_acts_order.sort()
                self.dialog_acts = [self.get_dialog_act_id(dact) for dact in self.dialog_acts]
                #responses ist liste von Antworindizes
                #responses = [ self.get_template_id(response, responses) for response in responses]            
                #trainset: [(äußerung1, da_index), (äußerung2, da_index)]
                return trainset, dialog_indices, self.dialog_acts_order


        def get_template_id(self, response, responses):
                for i in range(len(responses)):
                        if response == responses[i]:
                                return i
                return -1
        
        def get_dialog_act_id(self, dact):
                """
                Returns the id of a given dialog act.

                Parameters
                ----------
                dact : str
                        A string denoting a dialog act.

                Returns
                -------
                int
                        The index corresponding to the given dialog act. 
                        None if dialog act does not exist.
                """
                for i in range(len(self.dialog_acts_order)):
                        if dact == self.dialog_acts_order[i]:
                                return i
                return 

        
