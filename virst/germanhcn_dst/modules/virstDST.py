import spacy
import nltk
import pickle
import pandas as pd
import modules.classify2 as classify2


class State():
        """
        A class used to represent the states of the DST-Automaton.

        Attributes
        -----------
        name : str
                The name of the state   
        """
        
        def __init__(self, name):
                self.name = name


class Automaton(State):
        """
        A class to represent the DST-Automaton

        Attributes
        ---------
        automaton : dict()
                implemetation of the automaton 
        all_states : list()
                list of all states used in the automaton
        state_to_state: set()
                dictionary from a state to a set containing every state to which a transition from the key state exists
        current_state : State object
                state currently active during dialogue parsing
        memory : memory object
                memory tracking the which instructions have been read
        sentence_detector : nltk.punkt
                nltk sentence tokenizer
        utt_clf : sklearn classifier (svm)
                a classifier used to classify utterance types
        flag_run : int
                a flag indicating how many runs of the current exercise have been performed in exercises involving repettitions.
        flag_has_repeat : bool
                a flag indicatin whether the current exercise involves repettitions
        flag_has_security : bool
                a flag indicating whether the current exercise has security advices
        flag_has_read_descritption : bool
                a flag indicating whether any descritptions have been read at any time
        relaxation : bool
                a flag indicating if the current exeercise is a relaxation exercise. 
                In that case instructions have to be read one by one.
        question_lemmata : list
                a list providing access to lemmata of tokens in specific questions
        model : spacy language model (de)
                a german language model for the extraction of lemmata
        """
        def __init__(self, memory):
                self.automaton = {}
                self.all_states = []
                self.buildEmptyAutomaton()
                self.state_to_state = self.make_state_to_state_dict()
                self.current_state = self.get_state("intro")
                self.memory = memory
                self.sentence_detector = nltk.data.load('tokenizers/punkt/english.pickle')
                self.utt_clf = pickle.load(open("data/uttType.p", "rb"))
                self.flag_run = 1
                self.classifier = classify2.Classifier()
                self.flag_has_repeat = False
                self.flag_has_security = False
                self.flag_has_read_descriptions = False
                self.relaxation = False
                self.question_lemmata = []
                self.model = spacy.load('en_core_web_sm') 
        ###########################     
        #Funktionen für den Bau des Automaten
        #
        #
        ###############################
        def reset_current_state(self):
                """resets current_state to 'intro'
                
                should be called at every beginning of a new exercise
                """
                self.current_state = self.get_state("intro")
                return  
                
        def has_state(self, state):
                """checks if state is a state of the DST-automaton 
                
                Parameters
                ----------
                state : state object

                Returns
                -------
                bool
                        True if state is a state of the DST-automaton else False
                """             
                if self.automaton.get(state, 0) == 0:
                        return False
                return True

        def get_state(self, name):
                """ 
                returns state corresponding to name.

                Parameters
                ----------
                name : str
                        the name of the state to be retrieved

                Returns
                -------
                state object
                        the state corresponding to name. 
                
                Raises
                ------
                NotImplementedError
                        if no state corresponding to name is found      
                """
                if type(name)== State:
                        return name
                if name.startswith("part_description_"):
                        name = "_".join(name.split("_")[:-1])
                if name.startswith("intro_"):
                        name = name.split("_")[0]
                for state in self.all_states:
                        if state.name == name:
                                return state
                if state == None:
                        raise NotImplementedError("No State named {} found in DST-Automaton!".format(name))

        def has_transition(self, state, symb):
                """
                checks if outgoing transition with symb exists from state.

                Parameters
                ----------
                state : state object
                        the state the ransitions of which are being checked
                
                symb : str
                        input symbol for the transition looked for.
                        symb should be in the set of types returned by get_utterance_type(). 

                Returns
                -------
                bool
                        True if state is a state of the DST-automaton and state has an outgoing transition with symb. Else False.
                """
                if self.has_state(state) == True:
                        if self.automaton[state].get(symb, 0) != 0:
                                return True
                        return False
                return False

        def add_transition(self, fromstate, symb, tostate):
                """
                adds a transition with symb from fromstate to tostate.
                if fromstate is not part of the automaton yet fromstate is added first.

                Parameters
                ----------
                fromstate : state object
                        the state from which a transition with symb is to be added
                symb : str
                        the symbol with which a transition from from state to tostate is to be added. 
                        symb should be in the set of types returned by get_utterance_type(). 
                tostate : state object
                        the state to which a transition with symb is to be added
                
                Returns
                -------
                None 

                """
                if self.has_state(fromstate) == False:
                        self.add_state(fromstate)
                        self.automaton[fromstate][symb]=tostate
                        return 
                self.automaton[fromstate][symb]=tostate
                return
        
        def make_state_to_state_dict(self):
                """ gets dictionary from a state to a set containing every state to which a transition from the key state exists

                Parameters
                ----------
                tostate : state object
                        the state targeted with the added transition
                symb : str
                        the symbol with shich the transition is made.
                        symb should be in the set of types returned by get_utterance_type(). 
                exceptions : list of str, optional
                        list of names of states to be excluded 

                Returns
                -------
                the dictionary from states to possible transition states. 
                """
                shorter_dic = {}
                for state in self.automaton:
                        shorter_dic[state] = set()
                        for symb in self.automaton[state]:
                                shorter_dic[state].add(self.automaton[state][symb].name)
                return shorter_dic
                        
        def add_transition_from_all(self, tostate, symb, exceptions=[]):
                """ adds a transition with symb from every state ot included in exceptions to tostate. 
                        existing transitions from an state with the same symbol are overwritten due to the determinism of the automaton

                Parameters
                ----------
                tostate : state object
                        the state targeted with the added transition
                symb : str
                        the symbol with shich the transition is made.
                        symb should be in the set of types returned by get_utterance_type(). 
                exceptions : list of str, optional
                        list of names of states to be excluded 

                Returns
                -------
                None
                """
                for state in self.all_states:
                        if state not in exceptions:
                                self.add_transition(state, symb, tostate)
                return

        def add_state(self, state):
                """add state to automaton 
                
                Parameters
                ----------
                state : state object
                        the state to be added to the automaton
                Returns
                -------
                None
                """
                self.automaton[state] = {}
                return 

        def last_description_read(self):
                """
                checks if the last instruction of the current exercise has been read yet

                Returns
                -------
                bool
                        True if the last instruction of the current exercise has been read else False.
                """
                if  self.memory.action_memory == self.memory.max:
                        return True
                return False
        

        def predict2(self,utt):
                """
                predicts type of utterance.

                Parameters
                ----------
                utt : str
                        the utterance to be classified

                Returns
                -------
                tuple
                        a tuple of the predicted class and a confidence score of the prediction
                """
                n = {"text":[], "cat":[]}
                n["text"].append(utt)
                n["cat"].append(None)
                df = pd.DataFrame(n)
                prediction =  self.utt_clf.predict(df)
                for i in range(self.utt_clf.classes_.shape[0]):
                        if prediction == self.utt_clf.classes_[i]:
                                #print("Preditction: {}, Confidence: {}".format(self.utt_clf.predict(df), self.utt_clf.predict_proba(df)[0][i]))
                                return prediction[0], self.utt_clf.predict_proba(df)[0][i]

        def predict(self,utt):
                return self.classifier.predict(utt)
                
                
                
        def get_next_state(self, prediction):
                """
                finds type of utterance (symb) and returns state reached with it

                Parameters
                ----------
                utterance : str
                        the utterance of a patient

                Returns
                -------
                state object
                """
                #ordne die Äußerung einem der Äußerungstypen zu
                next_state = self.get_state(prediction)
                #print("ÄUßERUNGSTYP: ", symb)
                #if symb != "unkown":
                #       print(symb)
                #falls der aktuelle Zustand keine Ausgehenden Kanten hat
                #gib ihn wieder zurück???? closing / all_one
                if self.automaton.get(self.current_state,0)==0:
                        print(2,prediction)
                       #print(1)
                ##print("KEINE AUSGEHENDEN KANTEN {}".format(self.current_state.name))
                        if self.last_description_read():
                                print(3,prediction)
                                #print("last_description_read")
                                return self.current_state
                        else:
                                print(4,prediction)
                                #print("last_description_not_read")
                                self.current_state = self.get_state("all_one")
                                return self.current_state
                #falls der Zustand keinen Übergang mit dem 
                # aktuellen Symbol hat gib all_one zurück
                if len(self.automaton[self.current_state]) == 0:
                        print(5,prediction)
                        #print(2)
                        #print("len = 0")
                        return self.get_state("all_one")
                #sonst gib den mit dem aktuellen Symbol erreichten Zustand zurück
                else:
                        
                        #print(3)
                        #print("else: ",self.automaton[self.current_state])
                        #print(self.current_state.name)
                        for symb in self.automaton[self.current_state]:
                                if self.automaton[self.current_state][symb] == next_state:
                                        #print(next_state.name)
                                        return next_state
                #print(4)
                print(" NONE: current_state:{}   prediction:{}".format(self.current_state.name, prediction))

                        

        def buildEmptyAutomaton(self):
                """
                builds dialogue state tracking automaton for Virst.

                Returns
                -------
                None
                """
                intro = State("intro")
                askReady = State("ask_ready")
                requestReady = State("request_ready")
                generalDescription = State("general_description")
                askDescription= State("ask_description")
                #partDescription = State("part_description")
                summary = State("summary")
                closing = State("closing")
                repeatExercise = State("repeat_exercise")
                initRest = State("init_rest")
                rest = State("rest")
                sysWait = State("sys_wait")
                sysWaitRest = State("sys_wait_rest")
                askRest = State("ask_rest")
                security = State("security")
                askFinish = State("ask_finish")
                finish = State("finish")
                waitUntilHundred = State("wait_until_hundred")
                resumeExercise = State("resume_exercise")
                allOne = State("all_one")
                from_top = State("from_top")
                next_part = State("next")
                close_to_last = State("close_to_last")
                self.all_states += [intro, askReady, requestReady, generalDescription, askDescription,summary,next_part,close_to_last,from_top, closing, repeatExercise, initRest, rest, sysWait, sysWaitRest, askRest,security, askFinish, finish, waitUntilHundred, resumeExercise, allOne]

                #Transitions
                self.add_transition(intro, "intro", intro)
                self.add_transition(intro, "non_specific", intro)
                self.add_transition(intro, "backchannel", askReady)
                self.add_transition(intro, "affirm", askReady)

                self.add_transition(askReady,"non_specific", askReady)
                self.add_transition(askReady, "negate", requestReady)
                self.add_transition(askReady, "protest", requestReady)  
                self.add_transition(askReady,"affirm", generalDescription)
                self.add_transition(askReady,"backchannel", generalDescription)
                self.add_transition(askReady,"ready", generalDescription)
                self.add_transition(askReady,"part_desc_exhausted", generalDescription)
                self.add_transition(askReady,"askDescription", askDescription)
                self.add_transition(askReady,"ask_ready_to_ask_description", askDescription)
                self.add_transition(askReady,"finish",finish)

                self.add_transition(askFinish,"finish",finish)
                self.add_transition(askFinish,"next_part",next_part)
                self.add_transition(askFinish,"generalDescription",generalDescription)
                self.add_transition(askFinish,"ask_ready",askReady)
                self.add_transition(askFinish,"requestReady",requestReady)
                self.add_transition(askFinish,"from_top",from_top)
                self.add_transition(askFinish,"close_to_last",close_to_last)
                self.add_transition(askFinish,"askDescription",askDescription)
                
                #self.add_transition(generalDescription, "protest", requestReady)
                self.add_transition(generalDescription, "backchannel", requestReady)
                self.add_transition(generalDescription, "non_specific", askDescription)
                self.add_transition(generalDescription, "nonunderstanding", askDescription)
                self.add_transition(generalDescription, "from_top", from_top)
                self.add_transition(generalDescription, "next", next_part)
                self.add_transition(generalDescription, "close_to_last", close_to_last)
                self.add_transition(generalDescription, "specific", summary)
                self.add_transition(generalDescription, "difficult", askDescription)
                self.add_transition(generalDescription, "part_desc_exhausted_security", security)
                self.add_transition(generalDescription, "part_desc_exhausted_repeat", sysWait)
                self.add_transition(generalDescription, "part_desc_exhausted", sysWait)
                self.add_transition(generalDescription, "protest", askDescription)
                self.add_transition(generalDescription, "backchannel_relaxation", next_part)

                self.add_transition(next_part, "repeat", askDescription)
                self.add_transition(next_part, "nonunderstanding", askDescription)
                self.add_transition(next_part, "affirm", next_part)
                self.add_transition(next_part, "backchannel", next_part)
                self.add_transition(next_part, "specific", summary)
                self.add_transition(next_part, "non_specific", next_part)
                self.add_transition(next_part, "part_desc_exhausted_repeat", sysWait)
                self.add_transition(next_part,  "part_desc_exhausted_security", security)
                self.add_transition(next_part,  "part_desc_exhausted", sysWait)

                self.add_transition(from_top, "repeat", askDescription)
                self.add_transition(from_top, "nonunderstanding", askDescription)
                self.add_transition(from_top, "affirm", next_part)
                self.add_transition(from_top, "backchannel", next_part)
                self.add_transition(from_top, "specific", summary)
                self.add_transition(from_top, "non_specific", next_part)
                self.add_transition(from_top, "part_desc_exhausted_repeat", sysWait)
                self.add_transition(from_top,  "part_desc_exhausted_security", security)
                self.add_transition(from_top,  "part_desc_exhausted", sysWait)
                self.add_transition(from_top,  "close_to_last", close_to_last)

                self.add_transition(close_to_last, "repeat", askDescription)
                self.add_transition(close_to_last, "nonunderstanding", askDescription)
                self.add_transition(close_to_last, "affirm", next_part)
                self.add_transition(close_to_last, "backchannel", next_part)
                self.add_transition(close_to_last, "specific", summary)
                self.add_transition(close_to_last, "non_specific", next_part)
                self.add_transition(close_to_last, "part_desc_exhausted_repeat", sysWait)
                self.add_transition(close_to_last,  "part_desc_exhausted_security", security)
                self.add_transition(close_to_last,  "part_desc_exhausted", sysWait)
                
                self.add_transition(summary, "backchannel", next_part)
                self.add_transition(summary, "close_to_last", close_to_last)
                self.add_transition(summary, "from_top", from_top)
                self.add_transition(summary, "non_specific",summary)
                self.add_transition(summary, "part_desc_exhausted_security",security)
                self.add_transition(summary, "part_desc_exhausted",sysWait)
                self.add_transition(summary, "part_desc_exhausted_repeat", sysWait)

                self.add_transition(repeatExercise, "specific", summary)
                self.add_transition(repeatExercise,"from_top",from_top)
                self.add_transition(repeatExercise, "non_specific", repeatExercise)
                self.add_transition(repeatExercise, "backchannel", askDescription)
                self.add_transition(repeatExercise, "part_desc_exhausted", askDescription)
                self.add_transition(repeatExercise, "part_desc_exhausted_repeat_end", sysWait)

                self.add_transition(rest, "100", askReady)
                self.add_transition(rest, "backchannel" ,waitUntilHundred)

                self.add_transition(askDescription, "negate_repeat_exercise", repeatExercise)
                self.add_transition(askDescription, "affirm", from_top)
                self.add_transition(askDescription, "backchannel", from_top)
                self.add_transition(askDescription, "specific", summary)
                self.add_transition(askDescription, "non_specific", askDescription)
                self.add_transition(askDescription, "negate", sysWait)
                self.add_transition(askDescription, "next_part", next_part)
                self.add_transition(askDescription, "close_to_last", close_to_last)
                self.add_transition(askDescription, "negate_security", security)
                #self.add_transition(askDescription, "repeat", partDescription)

                self.add_transition(requestReady, "backchannel", sysWaitRest)
                self.add_transition(requestReady, "affirm", sysWaitRest)
                self.add_transition(requestReady, "non_specific", requestReady)
                self.add_transition(requestReady, "ready", generalDescription)
                self.add_transition(sysWaitRest, "ready", generalDescription) # Bedingung schreiben! noch nicht alles verbraucht.
                self.add_transition(sysWaitRest, "specific", summary)
                self.add_transition(sysWaitRest, "backchannel", askReady)
                

                self.add_transition(askRest, "affirm", requestReady)
                self.add_transition(askRest, "negate", next_part)
                self.add_transition(askRest, "from_top", from_top)
                self.add_transition(askRest, "close_to_last",close_to_last)
                #self.add_transition(askRest, "negate_", partDescription)
                self.add_transition(askRest, "non_specific", askRest)

                self.add_transition(sysWait, "specific", summary)
                self.add_transition(sysWait, "non_specific", requestReady)
                self.add_transition(sysWait, "repeat_exercise", repeatExercise)
                self.add_transition(sysWait, "wait", closing) #<-----  wait als Eingabe in Bedingungnen einfügen: alles verbraucht und backchannel
                self.add_transition(sysWait, "backchannel", askReady)
                self.add_transition(sysWait, "summary", summary)
                self.add_transition(sysWait, "from_top", from_top)
                self.add_transition(sysWait, "next_part", next_part)
                self.add_transition(sysWait, "close_to_last",close_to_last)
                
                self.add_transition(security, "difficult", askDescription)
                self.add_transition(security, "non_specific", security)
                self.add_transition(security, "backchannel", sysWait)

                self.add_transition(askFinish, "affirm", finish)
                self.add_transition(askFinish, "non_specific", askFinish)
                self.add_transition(askFinish, "finish", finish)
                self.add_transition(askFinish,"negate", askDescription)

                self.add_transition(initRest, "200", waitUntilHundred)
                self.add_transition(initRest, "non_specific", initRest)
                self.add_transition(initRest, "backchannel", waitUntilHundred)

                self.add_transition(waitUntilHundred, "100", resumeExercise)
                self.add_transition(waitUntilHundred, "200",rest)

                self.add_transition(resumeExercise, "backchannel", askDescription)
                self.add_transition(resumeExercise, "affirm", askDescription)
                self.add_transition(resumeExercise, "non_specific", resumeExercise)
                self.add_transition(resumeExercise, "backchannel_resume_from_start", askReady)

                #self.add_transition(closing,"closing",closing)
                #self.add_transition(finish,"finish",finish)

                self.add_transition_from_all(initRest, "200", exceptions=[closing, initRest, rest, askRest, finish])
                self.add_transition_from_all(allOne, "unknown", exceptions=[closing, initRest, intro, rest, finish])
                self.add_transition_from_all(askRest, "rest", exceptions=[closing,  allOne, askRest,  rest, finish, initRest])
                self.add_transition_from_all(askFinish, "finish", exceptions=[closing,  allOne, askFinish, finish])
                self.add_transition_from_all(summary, "specific", exceptions=[closing,  allOne, intro, finish, rest])

                self.add_transition_to_all(closing, "cl")
                self.add_transition_to_all(finish, "f1")
                self.add_transition_to_all(allOne,"unknown",exceptions = [initRest, intro])

                return 
        def add_transition_to_all(self,state,symb,exceptions=[]):
                """
                Adds transition from the given state to every state minus those listed in the exceptions. 

                Parameters
                ----------
                state: state_object
                        state from which transitions are drawn from. 
                symb: str
                        label to be given to every transition
                        
                exceptions: list
                        list of states


                Returns
                -------
                Null
                """
                for tostate in self.all_states:
                        if tostate not in exceptions:
                                self.add_transition(state, tostate.name, tostate)
                
        def get_utterance_type(self, utt):
                """
                gets type of utterance taking the current state of the dialogue parsing in account.

                Parameters
                ----------
                utt : str
                        a utterance made by the bot user.
                
                Returns
                -------
                str
                        type of the utterance. 
                
                """
                #pred, conf = self.predict(utt)
                pred = self.predict(utt)
                if utt =="start":
                        return "intro"
                elif utt == "200":              
                        return "200"
                elif utt == "100":      
                        return "100"
                #print(conf)
                if self.current_state == None: #or conf < .45: #rechtsoben = 0.0 linksoben = 0.1 stimmT!!
                
                        return "unknown"                        
                
                elif (self. current_state.name == "sys_wait_rest") and (pred == "backchannel" or pred == "affirm"):
                        return "backchannel"

                elif self.current_state.name =="ask_ready" and self.flag_run >=2 and (pred == "backchannel" or pred == "affirm" or pred == "repeat"):
                        return "ask_ready_to_ask_description"
                elif self.current_state.name =="general_description" and self.relaxation and (pred == "backchannel" or pred == "affirm"):               
                        return "backchannel_relaxation" 
                elif self.current_state.name =="general_description" and pred == "backchannel" and self.flag_has_repeat  and  self.flag_run ==1 and not self.flag_has_security:
                        return "part_desc_exhausted_repeat"     
                elif self.current_state.name =="ask_description" and pred == "negate" and self.flag_has_security  and  self.flag_run ==1:
                        return "negate_security"        
                #general description, erster Durchlauf, sieht wiederholung vor, hat security
                elif self.current_state.name =="general_description" and  pred == "backchannel" and self.flag_has_repeat  and  self.flag_run ==1 and self.flag_has_security:
                        return "part_desc_exhausted_security"
                #für den Fall, dass hochgezählt werden muss (wiederholung vorgesehen)
                elif self.current_state.name =="security" and  pred == "backchannel" and self.flag_has_repeat  and  self.flag_run ==1:
                        return "backchannel"
                
                elif self.current_state.name == "sys_wait" and self.last_description_read() and (pred == "backchannel" or pred =="affirm" or pred =="ready") and self.flag_has_repeat and self.flag_run >= 2:
                        return "wait"

                elif self.current_state.name == "sys_wait" and self.last_description_read() and (pred == "backchannel" or pred =="affirm"or pred =="ready") and self.flag_has_repeat and self.flag_run ==1:
                        self.flag_run +=1
                        return "repeat_exercise"

                elif self.current_state.name == "sys_wait" and self.last_description_read() and(pred == "backchannel" or pred =="affirm"or pred =="ready") and not self.flag_has_repeat:
                        self.flag_run +=1
                        return "wait"
                
                #general_description vorgelesen, keine Wiederholung vorgesehen, keine security
                elif self.current_state.name == "general_description" and  (pred == "backchannel" or pred == "affirm")  and not self.flag_has_repeat and not self.flag_has_security:
                        return "part_desc_exhausted"

                elif self.last_description_read() and  pred == "backchannel" and not self.flag_has_security:
                        return "part_desc_exhausted"            
                
                elif self.current_state.name == "ask_description" and  pred == "negate"  and self.flag_has_repeat and not self.flag_has_security and self.flag_run > 1:
                        self.flag_run +=1
                        return "part_desc_exhausted"
                elif self.current_state.name == "ask_description" and  pred == "negate"  and self.flag_has_repeat and not self.flag_has_security and self.flag_run ==1:
                        self.flag_run +=1
                        return "part_desc_exhausted_repeat"
                #general_description vorgelesen, keine Wiederholung vorgesehen, hat security
                elif self.current_state.name == "general_description" and pred == "backchannel" and not self.flag_has_repeat and self.flag_has_security:
                        return "part_desc_exhausted_security"
                elif self.current_state.name == "general_description" and pred == "negate" and self.flag_has_security:
                #print("HIER: ", "15b")
                        return "negate_security"
                elif self.current_state.name == "summary" and self.last_description_read() and pred == "backchannel" and not self.flag_has_repeat and self.flag_has_security:
                #print("HIER: ", 16)
                        return "part_desc_exhausted_security"
                #letzte part_description vorgelsen, keine Wiederholung, hat security
                elif self.current_state.name != "security" and self.last_description_read() and not self.flag_has_repeat  and pred == "backchannel" and  self.flag_has_security:
                #print("HIER: ", 17)
                        return "part_desc_exhausted_security"
                #part_description -> repeat_exercise
                #letzte Anweisun vorgelesen, erster Durchlauf, sieht wiederholung vor, hat security
                

                #elif self.last_description_read() and re.search(self.BACKCHANNEL, utt) and  self.flag_has_repeat and not self.flag_has_completed_one_run and self.flag_has_security: 
                #       self.flag_has_completed_one_run = True
                #       return "part_desc_exhausted_security"

                elif self.flag_has_repeat  and self.current_state.name =="ask_description"  and pred == "negate" and self.flag_run > 1 and not self.flag_has_security:
                #print("HIER: ", 18)
                        return "negate_repeat_exercise"
                elif self.flag_has_repeat  and self.current_state.name == "repeat_exercise"  and pred == "backchannel" and self.flag_run > 1:                   
                #print("HIER: ", 19)
                        return "part_desc_exhausted_repeat_end"
                
                #elif pred == "rest":                   
                #print("HIER: ", 21)
                #       return "rest"
                
                        #diese Bedingungen greifen, falls Pause gemacht wurde bevor irgendwelche Anweisungen vorgelesen wurden
                elif self.current_state.name == "resume_exercise" and self.flag_has_read_descriptions == False and pred == "backchannel":                       
                        self.flag_run += 1
                #print("HIER: ", 23)
                        return "backchannel_resume_from_start"

                elif self.last_description_read() and pred == "backchannel" and  self.flag_has_repeat and self.flag_run ==1 and not self.flag_has_security: 
                        #self.flag_run +=1
                #print("HIER: ", 5)
                        return "part_desc_exhausted_repeat"

                elif self.last_description_read() and pred == "backchannel" and  self.flag_has_repeat and self.flag_run ==1 and self.flag_has_security: 
                        self.flag_run +=1
                #print("HIER: ", "5b")
                        return "part_desc_exhausted_security"

                elif pred == "backchannel" and not self.last_description_read():                                                
                #print("HIER: ", 24)
                        return "backchannel"
                
        
                elif (self.current_state.name == "request_ready" or self.current_state.name == "ask_ready") and  (pred == "ready" or pred == "backchannel"):
                #print("HIER: ", 32)
                        return "ready"

                elif pred == "specific" or pred == "yesno":
                #print("HIER: ", 24)
                        sents = self.sentence_detector.tokenize(utt)
                
                        #tags = []
                        lemmata = []
                        
                        for s in sents:
                                u = self.model(s)
                                #tags += [token.tag_ for token in u]
                                lemmata +=  [token.lemma_.lower() for token in u]
                        self.question_lemmata = lemmata
                        #print(lemmata)
                        return "specific"
                
                else:
                #print("HIER: ", 38)
                        return pred
