import modules.virstUtil as util
import modules.virstDST as dst
import modules.virstDataUtils as data_utils
import numpy as np
import re
import spacy
import modules.virstMemory_diff as memory
import json
import random
import gensim
import time
import random
import nltk
from itertools import chain
from collections import Counter
import pickle
class ActionTracker():
        """
        A class used to represent the action template structure, a nested dictionary.
         

        {
                exercise_1: {
                        entity_map: {
                                entity1: A list of instruction numbers containing the entity (Noun or full verb)
                                entity2: ...
                        }
                        dialog_act: {
                                text: A list of utterances corresponding to the dialog act.
                                da_index : the index of the dialog act 
                        }
                        part_description : {
                                1 : {
                                        text: A list of utterances corresponding to the dialog act.
                                        da_index : the index of the dialog act 
                                }
                                2: {
                                        ...
                                }
                        }
                                        
                }
                exercise_2: {
                        ...
                }
        } 

        Attributes
        -----------
        interact : bool
                A flag indicating if the mode is interactive (as oposed to train).
                If True dialog_acts and dialog_act_ids are loaded from data/acts.p and data/ids.p
                This is a hack with the purpose of persistence.

        model : spacy language model 
                A language model provided by spacy.

        sentence_detector : nltk tokenizer 
                A tokenizer used for sentence tokenization

        memory : memory object
                A memory tracking the sequence of instructions given to the user.
                Only part_description-acts are tracked.
        
        responses : list of tuples of list and int
                Each response is represented as a tuple. 
                The first element is a list containing the response as text and the corresponding dilaog act.
                The second element is the index of the dialog act.
        
        exercise : string
                The current exercise.

        dialog_acts : list
                A list of all dialog acts from the dataset with the original labeling schema.

        dialog_act_ids : list
                A list of indices corresponding to the dialog acts in dialog_acts in the dataset with the original labeling schema.

        action_templates : nested dict 
                Structure mapping dialog acts to their textual representations within the context their respective exercises.
                
                The dict is structured as follows:
                exercise (dict)
                        entity_map (dict)
                                entity: list of instruction numbers (list)
                        dialog_act (dict)
                                text: list of textual representations (list)
                                da_index: index of the dialog act (int)
                        part_description (dict)
                                instruction number : (dict)
                                        text: list of textual representations (list)
                                        da_index: index of the dialog act (int)

                Note that the dialog act part_description is structured 
                Instruction numbers are NOT dialog indices
                but a number indicating the position of an instruction within the sequence of instructions.
                i.e the number contained in the part_description tags e.g. part_description_1
        data : tuple
                A tuple containing the dataset, the dialog_indices, and the other_da from the dataset with the new labeling schema. 

        dataset : list
                A list of tuples of utterance and dialog_act pairs based on the dataset with the new labeling schema. 

        dialog_indices : list
                A list of dictionaries from the key words 'start' and 'end' to the respective starting and ending indices of dialogs from the data set with the new labeling schema.
                
        other_da : list
                A list of all dialog acts from the dataset with the new labeling schema.

        other_da_ids : list
                A list of indices corresponding to the dialog acts in dialog_acts in the dataset with the new labeling schema.

        exercises : list
                A list containing the names of all exercises represented in action_templates

        action_size : int
                The number of dialog acts 
        
        am : array
                Action mask of the size of action_size.

        dialog_acts_current_exercise : list
                A list of all dialog acts featured in the current exercise.

        automaton : automaton object
                A dialog state tracking automaton
        
        """


        def __init__(self,interact=False):
                self.interact = interact
                self.model = spacy.load('en_core_web_sm')
                self.sentence_detector = nltk.data.load('tokenizers/punkt/english.pickle')
                self.memory = memory.Memory()
                #allgemeines Gedächtnis
                self.responses = util.get_responses(with_indices=True)
                #glob. Variable für aktuelle Übung
                self.exercise = ""
                #liste von Dialogakten
                self.dialog_acts = list(set(util.get_dialog_acts()))
                self.dialog_acts.sort()
                self.dialog_act_ids = [self.get_dialog_act_id(dact,action_template = True) for dact in self.dialog_acts]
                self.data = data_utils.Data()
                self.dataset, self.dialog_indices, self.other_da = self.data.trainset
                self.other_da_ids = [self.get_dialog_act_id(dact) for dact in self.other_da]
                
                #print(self.dialog_acts)
                #liste von aTs (Dictionatries)
                self.action_templates = self.get_action_templates()
                #pickle.dump(self.action_templates, open("data/action_templates.p", "wb"))
                #print(json.dumps(self.action_templates, indent=4))
                self.exercises = list(self.action_templates.keys())
                #self.action_size = len(self.responses) + len(self.exercises)
                # action mask
                self.action_size = len(self.other_da)
                self.am = np.zeros([self.action_size], dtype=np.float32)
                self.automaton = dst.Automaton(self.memory)
                self.dialog_acts_current_exercise = []
                
        def get_data(self):
                return self.dataset, self.dialog_indices, self.other_da, self.other_da_ids
        ###################################
        #Hilfsfunktionen, die Zugrif, Größen o.ä. berechnen
        #für Initialisierung golb. Variablen 
        #
        ###################################

        # gibt Index eines Dialogakts zurück. Vorhersage des Systems wird Index sein
        def get_dialog_act_id(self, dact, action_template = False):
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
                if action_template:
                        das = self.dialog_acts
                else:
                        das = self.other_da
                for i in range(len(das)):
                        if dact == das[i]:
                                return i
                return 

        def set_exercise(self, da_index):
                """
                Function is called at the beginning of a new exercise
                in order to initialize all ecessary variables.

                Parameters
                ----------
                int
                        the index of the dialog act introducing the exercise.
                
                """
                self.reset_action_mask()
                self.exercise = self.dialog_acts[da_index]
                self.memory.max = len(self.action_templates[self.exercise]["part_description"].keys())
                self.automaton.reset_current_state()
                self.dialog_acts_current_exercise = list(self.action_templates[self.exercise].keys())
                self.automaton.flag_has_repeat = False
                self.automaton.flag_has_security = False
                self.automaton.flag_has_completed_one_run = False
                if "repeat_exercise" in self.dialog_acts_current_exercise:
                        self.automaton.flag_has_repeat = True
                if "security" in self.dialog_acts_current_exercise:
                        self.automaton.flag_has_security = True
                if self.exercise ==  "intro_entspannungsuebung":
                        self.automaton.relaxation = True
                else:
                        self.automaton.relaxation = False
                #print("MEMORYMAX = {}".format(self.memory.max))
                self.automaton.flag_run = 1
                self.automaton.entities = self.action_templates[self.exercise]["entity_map"]
                return

        def set_exercise_string(self, exercise):
                """
                Initializes all necessary variables at the beginning of a new exercise.
                (Does the same as set_exercise)

                Parameters
                ----------
                str
                        The name of the exercise.

                Returns 
                -------
                None
                
                """
                self.reset_action_mask()
                self.exercise = exercise
                self.memory.max = len(self.action_templates[self.exercise]["part_description"].keys())
                self.automaton.reset_current_state()
                
                self.dialog_acts_current_exercise =  list(self.action_templates[self.exercise].keys())
                self.automaton.flag_has_repeat = False
                self.automaton.flag_has_security = False
                self.automaton.flag_has_completed_one_run = False
                if "repeat_exercise" in self.dialog_acts_current_exercise:
                        self.automaton.flag_has_repeat = True
                if "security" in self.dialog_acts_current_exercise:
                        self.automaton.flag_has_security = True
                if exercise == "intro_entspannungsuebung":
                        self.automaton.relaxation = True
                else:
                        self.automaton.relaxation = False
                self.automaton.flag_run= 1
                self.automaton.entities = self.action_templates[self.exercise]["entity_map"]
                return
        

        def get_action_templates(self):
                """
                Builds action template structure from responses.

                Returns
                -------
                action_templates
                        The action template structure.

                Raises
                ------
                Exception 
                        Warning in case no exercise was detected.
                """
                action_templates={}
                exercise = ""
                for i in range(len(self.responses)):
                        tag = self.responses[i][0][1]
                        #if tag.startswith("part_description_"):
                                #self.dialog_acts.append("_".join(name.split("_")[:-1]))
                        #elif name.startswith("intro_"):
                                #self.dialog_acts.append(tag.split("_")[0])
                        if tag not in self.dialog_acts:
                                self.dialog_acts.append(tag)    
                        if tag.startswith("intro_"):
                                exercise = tag
                        if exercise == "":
                                raise Exception("WARNUNG: Keine Übung erkannt! {}".format(tag) )
                        if action_templates.get(exercise, 0) == 0:
                                action_templates[exercise]={}
                                action_templates[exercise]["entity_map"]={}
                        if tag.startswith("part_description"):
                                part = "_".join(tag.split("_")[:-1])
                                number = int(tag.split("_")[-1])
                                if action_templates[exercise].get(part, 0)==0:
                                        action_templates[exercise][part] = {}
                                        action_templates[exercise][part][number]= self.extract_actions(self.responses[i],self.get_dialog_act_id(tag) )
                                        self.fill_entity_map(action_templates[exercise], self.responses[i])
                                elif action_templates[exercise][part].get(number, 0)==0:
                                        action_templates[exercise][part][number] = self.extract_actions(self.responses[i],self.get_dialog_act_id(tag) )
                                        self.fill_entity_map(action_templates[exercise],self.responses[i])
                                else:
                                        self.update_action(action_templates[exercise][part][number], self.responses[i][0])
                                        self.fill_entity_map(action_templates[exercise], self.responses[i])
                        elif action_templates[exercise].get(tag, 0)==0:
                                action_templates[exercise][tag] = self.extract_actions(self.responses[i],self.get_dialog_act_id(tag) )
                                self.fill_entity_map(action_templates[exercise],self.responses[i])
                        else:
                                self.update_action(action_templates[exercise][tag], self.responses[i][0])
                                self.fill_entity_map(action_templates[exercise], self.responses[i])

                for exercise in action_templates.keys():
                        if "finish" not in action_templates[exercise].keys():
                                action_templates[exercise]["finish"]={"text":["All right then, let's stop." "All right, let's stop." "All right, let's stop practicing first."],
                                                                        "da_index":     self.get_dialog_act_id("finish")}
                        if "ask_finish" not in action_templates[exercise].keys():
                                action_templates[exercise]["ask_finish"]={"text":["Do you want to stop this exercise? It is important that you do it regularly", "Do you want to stop the exercise?.."],
                                                                        "da_index":     self.get_dialog_act_id("ask_finish")}
                        if "rest" not in action_templates[exercise].keys():
                                action_templates[exercise]["rest"]={"text":["Your pulse is still a bit too high. We still have to wait a bit before we go on", "Before we go on, we should wait until you are no longer so stressed"],
                                                                        "da_index":     self.get_dialog_act_id("rest")}
                        if "ask_rest" not in action_templates[exercise].keys():
                                action_templates[exercise]["ask_rest"]={"text":["Do you want to take a short break?..", "Shall we take a short break?", "Do you want to take a little breather?"],
                                                                        "da_index":     self.get_dialog_act_id("ask_rest")}
                        if "sys_wait" not in action_templates[exercise].keys():
                                action_templates[exercise]["sys_wait"]={"text":["<System waits for 30 seconds>"],
                                                                        "da_index":     self.get_dialog_act_id("sys_wait")}
                        if "sys_wait_rest" not in action_templates[exercise].keys():
                                action_templates[exercise]["sys_wait_rest"]={"text":["<System waits for 30 seconds>"],
                                                                        "da_index":     self.get_dialog_act_id("sys_wait_rest")}
                        if "wait_until_hundred" not in action_templates[exercise].keys():
                                action_templates[exercise]["wait_until_hundred"]={"text":["<System waits for 10 seconds>"],
                                                                        "da_index":     self.get_dialog_act_id("wait_until_hundred")}
                        if "init_rest" not in action_templates[exercise].keys():
                                action_templates[exercise]["init_rest"]={"text":["Your stress level is too high. We should take a short break", "You still have too high a stress level at the moment. We'd better take a short break."],
                                                                        "da_index":     self.get_dialog_act_id("init_rest")}
                        if "request_ready" not in action_templates[exercise].keys():
                                action_templates[exercise]["request_ready"]={"text":["Well, please let me know when you're ready.", "Ok, please let me know when you're ready."],
                                                                        "da_index":     self.get_dialog_act_id("request_ready")}
                        if "resume_exercise" not in action_templates[exercise].keys():
                                action_templates[exercise]["resume_exercise"]={"text":["Ok,your pulse is normal again"],
                                                                        "da_index":     self.get_dialog_act_id("resume_exercise")}
                # extract tracking entities
                #print(json.dumps(action_templates, indent=4))
                return action_templates

        def update_action(self, action, utterance):
                """
                Adds text representations to allready created dialog act representations within the action template structure.

                Parameters
                ----------
                action : dict
                        A dictionary that is the value of a dialog act within the action template structure.
                
                utterance : list
                        List containing a text representation of a dialog act and the string representation of the dialog act
                        i.e. the first element of a response tuple.
                        [text, dialog act]

                Returns
                -------
                None

                """
                action["text"].append(utterance[0])
                action["text"] = list(set(action["text"]))
                return

        def fill_entity_map(self, action_template, utterance):
                """
                Analyzes sentences and maps the lemmas of any token whos tag is either NN, VVFIN or VVINF to a list of instruction numbers
                corresponding to the instructions containing the found entities. 

                Parameters
                ---------
                action_template : dict
                        A dict representing an exercise within the action template structure

                utterance : Tuple
                        A response tuple from responses
                        ([text, dialog act], dialog act index) 

                Returns
                -------
                None

                """
                if not utterance[0][1].startswith("part_description"):
                        return
                #utterance = [[response, tag],da_index]
                sents = self.sentence_detector.tokenize(utterance[0][0])
                for s in sents:
                        parse = self.model(s)
                        for token in parse:
                                if token.tag_ in ["NN","NNS","VB", "VBD","VBG","VBN","VBN","VBP","VBP","VBZ"]:
                                        lemma = token.lemma_.lower()
                                        if action_template["entity_map"].get(token.lemma_, 0) ==0:
                                                action_template["entity_map"][lemma]=[]
                                                #print(utterance[0][1],token.tag_, action_template["entity_map"][token.tag_])
                                                action_template["entity_map"][lemma].append(int(utterance[0][1].split("_")[-1]))
                                                action_template["entity_map"][lemma] = list(set(action_template["entity_map"][lemma]))
                                        else:
                                                action_template["entity_map"][lemma].append(int(utterance[0][1].split("_")[-1]))
                                                action_template["entity_map"][lemma] = list(set(action_template["entity_map"][lemma]))
                return

        
        def extract_actions(self, utterance, da_index):
                
                """
                Creates a dict to serve as value for some dialog act in the action template structure.

                Parameters
                ----------
                utterance : tuple
                        A response tuple from responses.
                        ([text, dialog act], dialog act index) 
                
                
                Returns
                -------
                action : dict
                        A dictionary containing a list of text representations corresponding to some dialog act
                        and the index of that dialog act. This dict then serves as the value of a dialog act in the action template structure

                """
                action = {
                        "text" : [],
                        "da_index": da_index,
                 }
                action["text"].append(utterance[0][0])
                return action


        
        #Funktion gibt Liste mit Part_descriptions zurück, die ein Lemma aus einer Frage enthalten      
        def get_partdescs(self):
                """
                Creates a list of instructions that contain a lemma also contained in a question.

                Returns
                -------
                list of int 
                        A list of instruction numbers.
                """
                lemmaList = self.question_lemmata
                #print(lemmaList)
        #print(lemmaList)
                entMap =  self.action_templates[self.exercise]["entity_map"]
                #print(entMap)
        #print(self.action_templates[self.exercise]["entity_map"])
                part_descs = [entMap[lemma.lower()] for lemma in lemmaList if lemma.lower() in entMap.keys()]
                part_descs = list(chain.from_iterable(part_descs))
                #print(part_descs)
                return part_descs
##############################BUILD ACTIONAMSK WITH DST###################################

#Bedingungen für Dialog State Tracker, wie er in virstDST.py definiert ist,
#Reglieren den Lauf durch den Automaten und die Belegung des Actiontemplates
#Für eine graphische Darstellung des Automaten:
#s. viewDST.py
#
#Für eine Darstellung der allgemein in den Daten vorkommenden Übergänge:
# python modules/viewDAGraph.py data/tagged_virst_train.txt



        # INDIZES IN AM BEZIEHEN SICH AUF DIALOGAKTE, NICHT AUF SÄTZE

        # funktion für Part_description 
        def get_at_index_of_part(self, da, num_inst):
                """
                Gets the dialog act index of a certain instruction. 
                
                """
                if self.action_templates[self.exercise][da].get(num_inst, 0)==0:
                #print("GIBTS NICHT1 ", da, num_inst)
                        if num_inst == 0:
                                return self.action_templates[self.exercise]["part_description"][1]["da_index"]
                        #print("H",self.memory.get_last_action())
                        num_inst = self.memory.get_last_action()
                        
                return self.action_templates[self.exercise][da][num_inst]["da_index"]

        def get_at_index_of_part_for_summary(self, num_inst):
                ##not used in Colton's code
                if self.action_templates[self.exercise]["part_description"].get(n,("GIBTS NICHT2 ",  num_inst)):
                        if num_inst == 0:
                                return self.action_templates[self.exercise]["part_description"][1]["da_index"]
                                #print("G",self.memory.get_last_action())
                        num_inst == self.memory.get_last_action()
                return self.action_templates[self.exercise]["part_description"][num_inst]["da_index"]

        #setzt action mask auf null
        def reset_action_mask(self):
                self.am = np.zeros([self.action_size], dtype=np.float32)
                return

        #setzt alle Stellen in Action Mask, die Dialogakten der aktuellen Übung entsprechen auf eins
        def set_all_exercise_one(self):
                indcs = []
                #dialogakte sammeln
                das = [key for key in list(self.action_templates[self.exercise].keys()) if key != "entity_map"]
                #indizes sammeln
                for da in das:
                        if da == "part_description":
                                for key in self.action_templates[self.exercise][da].keys():
                                        indcs.append(self.action_templates[self.exercise][da][key]["da_index"])
                        else:   
                                indcs.append(self.action_templates[self.exercise][da]["da_index"])
                #enstprechende Stellen in action mask auf eins setzen
                indcs = [ind for ind in indcs if ind != None]
                for ind in indcs:
                        self.am[ind]=1
                return 

        def set_am_part_description(self, state):
        #print("ALSO: SET LAST DESC 1")
                if self.memory.get_last_action() == 0:
                #print("ALSO: SET LAST DESC MEM = 0")
                        self.am[self.get_at_index_of_part(state.name, 1)]=1
                        self.memory.update(1)
                        return 
                self.am[self.get_at_index_of_part(state.name, self.memory.get_last_action()+1)] = 1
                return

        def set_am_last_part_description(self, state):
        #print("ALSO: SET LAST DESC 2") 
                self.am[self.get_at_index_of_part(state.name, self.memory.get_last_action())] = 1
                return

        def set_am_summary(self, state):
                ##not used in colton's code
                self.am[self.get_at_index_of_part_for_summary(self.memory.get_last_action())] = 1
                return

        def set_am_for(self, state):
                """Uses the FST to make the action mask so that 1's in the action mask correspond only
                to states which are possible to transition to from the current state. 
                """
                if state.name in ["closing","finish","all_one"]:
                        self.set_all_exercise_one()
                        return
                else:
                        for new_state in self.automaton.state_to_state[state]:
                                if new_state == "all_one":
                                        continue
                                else:
                                        self.am[self.get_dialog_act_id(new_state)]=1
                if self.memory.is_at_end():
                        self.am[self.get_dialog_act_id("next")] = 0
                if self.automaton.flag_has_repeat == False:
                        self.am[self.get_dialog_act_id("repeat_exercise")] = 0
                if self.automaton.flag_has_security == False:
                        self.am[self.get_dialog_act_id("security")] = 0
                return
        def initialize_am(self):
                """Sets action mask so that it is only possible to predict 'intro'
                """
                self.am[self.get_dialog_act_id("intro")]=1
        #hier wird der nächste Zustand berechnet und die Action Mask belegt
        def walk(self,utt,prediction):
                """Moves the current state of the FST,sets the action mask for the next prediction, directs the memory, and returns the ultimate response text,which is possibly
                based on utt if the prediction is 'summary'.
                """
                prediction = self.other_da[prediction]
                current_state = self.automaton.current_state
                next_state = self.automaton.get_next_state(self.automaton.get_state(prediction).name)
                self.reset_action_mask()
                if next_state.name == "next":
                        self.memory.update()
                elif next_state.name == "from_top":
                        self.memory.reset_memory(self.exercise)
                elif next_state.name == "close_to_last":
                        self.memory.get_second_to_last()
                elif next_state.name == "summary":
                        sents = self.sentence_detector.tokenize(utt)
                        lemmata = []
                        for s in sents:
                                u = self.model(s)
                                lemmata +=  [token.lemma_.lower() for token in u]
                        self.question_lemmata = lemmata
                        partdesc=self.get_partdescs()
                        if partdesc == []:
                                self.set_am_for(next_state)
                                return next_state,"I'm sorry, I didn't understand, could you ask that in a different way?"
                        else:
                                self.memory.set_memory(min(partdesc))
                try:        
                        self.set_am_for(next_state)
                except:
                        print(current_state.name,next_state.name,[(key.name,self.automaton.state_to_state[key]) for key in self.automaton.state_to_state.keys()])
                        exit()

                text = self.get_text(prediction)
                
                return next_state,text               

        def set_am_by_index(self, index):
                ##not used in Colton's code.
                self.reset_action_mask()
                self.am[index] = 1
                return
        def get_text(self, prediction):
                """use the extracted action templates to determine a response text given the dialog act.
                """
                number = self.memory.get_last_action()
                if prediction in ["next","summary","from_top","close_to_last"]:   
                        return random.choice(self.action_templates[self.exercise]["part_description"][number]["text"])
                elif prediction == "intro":
                        return random.choice(self.action_templates[self.exercise][self.exercise]["text"])
                return random.choice(self.action_templates[self.exercise][prediction]["text"])
