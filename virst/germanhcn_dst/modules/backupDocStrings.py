import spacy
import nltk
import pickle
import pandas as pd


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

	Arguments
	---------
	automaton : dict()
		implemetation of the automaton 
	all_states : list()
		list of all states used in the automaton
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
		self.current_state = self.get_state("intro")
		self.memory = memory
		self.sentence_detector = nltk.data.load('tokenizers/punkt/german.pickle')
		self.utt_clf = pickle.load(open("data/uttType.p", "rb"))
		self.flag_run = 1
		self.flag_has_repeat = False
		self.flag_has_security = False
		self.flag_has_read_descriptions = False
		self.relaxation = False
		self.question_lemmata = []
		self.model = spacy.load('de_core_news_sm') 
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
		exceptions : list of str
			list of nomes of states to be excluded. 

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
		if  self.memory.progress() == self.memory.max:
			return True
		return False
	

	def predict(self,utt):
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
		partDescription = State("part_description")
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
		self.all_states += [intro, askReady, requestReady, generalDescription, askDescription,partDescription,summary, closing, repeatExercise, initRest, rest, sysWait, sysWaitRest, askRest,security, askFinish, finish, waitUntilHundred, resumeExercise, allOne]

		#Transitions
		#
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
		self.add_transition(askReady,"part_desc_exhausted", askDescription)
		self.add_transition(askReady,"ask_ready_to_ask_description", askDescription)

		self.add_transition(generalDescription, "protest", requestReady)
		self.add_transition(generalDescription, "backchannel", requestReady)
		self.add_transition(generalDescription, "non_specific", askDescription)
		self.add_transition(generalDescription, "nonunderstanding", askDescription)
		self.add_transition(generalDescription, "repeat", partDescription)
		self.add_transition(generalDescription, "specific", summary)
		self.add_transition(generalDescription, "difficult", askDescription)
		self.add_transition(generalDescription, "part_desc_exhausted_security", security)
		self.add_transition(generalDescription, "part_desc_exhausted_repeat", sysWait)
		self.add_transition(generalDescription, "part_desc_exhausted", sysWait)

		self.add_transition(generalDescription, "protest", askDescription)
		self.add_transition(generalDescription, "backchannel_relaxation", partDescription)

		self.add_transition(partDescription, "repeat", askDescription)
		self.add_transition(partDescription, "nonunderstanding", askDescription)
		self.add_transition(partDescription, "affirm", partDescription)
		self.add_transition(partDescription, "backchannel", partDescription)
		self.add_transition(partDescription, "specific", summary)
		self.add_transition(partDescription, "non_specific", partDescription)
		self.add_transition(partDescription, "part_desc_exhausted_repeat", sysWait)
		self.add_transition(partDescription,  "part_desc_exhausted_security", security)
		self.add_transition(partDescription,  "part_desc_exhausted", sysWait)

		self.add_transition(summary, "backchannel", partDescription)
		self.add_transition(summary, "non_specific",summary)
		self.add_transition(summary, "part_desc_exhausted_security",security)
		self.add_transition(summary, "part_desc_exhausted",sysWait)
		self.add_transition(summary, "part_desc_exhausted_repeat", sysWait)

		self.add_transition(repeatExercise, "specific", partDescription)
		self.add_transition(repeatExercise, "non_specific", repeatExercise)
		self.add_transition(repeatExercise, "backchannel", askDescription)
		self.add_transition(repeatExercise, "part_desc_exhausted", askDescription)
		self.add_transition(repeatExercise, "part_desc_exhausted_repeat_end", sysWait)

		self.add_transition(rest, "100", askReady)
		self.add_transition(rest, "backchannel" ,waitUntilHundred)

		self.add_transition(askDescription, "negate_repeat_exercise", repeatExercise)
		self.add_transition(askDescription, "affirm", partDescription)
		self.add_transition(askDescription, "backchannel", partDescription)
		self.add_transition(askDescription, "specific", summary)
		self.add_transition(askDescription, "non_specific", askDescription)
		self.add_transition(askDescription, "negate", sysWait)
		self.add_transition(askDescription, "negate_security", security)
		self.add_transition(askDescription, "repeat", partDescription)

		self.add_transition(requestReady, "backchannel", sysWaitRest)
		self.add_transition(requestReady, "affirm", sysWaitRest)
		self.add_transition(requestReady, "non_specific", requestReady)
		self.add_transition(requestReady, "ready", generalDescription)
		self.add_transition(sysWaitRest, "ready", generalDescription) # Bedingung schreiben! noch nicht alles verbraucht.
		self.add_transition(sysWaitRest, "specific", summary)
		self.add_transition(sysWaitRest, "backchannel", askReady)
		

		self.add_transition(askRest, "affirm", requestReady)
		self.add_transition(askRest, "negate", partDescription)
		#self.add_transition(askRest, "negate_", partDescription)
		self.add_transition(askRest, "non_specific", askRest)

		self.add_transition(sysWait, "specific", summary)
		self.add_transition(sysWait, "repeat_exercise", repeatExercise)
		self.add_transition(sysWait, "wait", closing) #<-----  wait als Eingabe in Bedingungnen einfügen: alles verbraucht und backchannel
		self.add_transition(sysWait, "backchannel", askReady)
		
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

		self.add_transition_from_all(initRest, "200", exceptions=[closing, initRest, rest, askRest, finish])
		self.add_transition_from_all(allOne, "unknown", exceptions=[closing, initRest, intro, rest, finish])
		self.add_transition_from_all(askRest, "rest", exceptions=[closing,  allOne, askRest,  rest, finish, initRest])
		self.add_transition_from_all(askFinish, "finish", exceptions=[closing,  allOne, intro, askFinish, finish])
		self.add_transition_from_all(summary, "specific", exceptions=[closing,  allOne, intro, finish, rest])
		return 

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
		pred, conf = self.predict(utt)
		
		if utt =="start":
			return "intro"
		elif utt == "200":		
			return "200"
		elif utt == "100":	
			return "100"
		if self.current_state == None or conf < 0.2:
		
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
		
		elif self.current_state.name == "sys_wait" and self.last_description_read() and pred == "backchannel" and self.flag_has_repeat and self.flag_run >= 2:
			return "wait"

		elif self.current_state.name == "sys_wait" and self.last_description_read() and pred == "backchannel" and self.flag_has_repeat and self.flag_run ==1:
			self.flag_run +=1
			return "repeat_exercise"

		elif self.current_state.name == "sys_wait" and self.last_description_read() and pred == "backchannel" and not self.flag_has_repeat:
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
		elif self.last_description_read() and not self.flag_has_repeat  and pred == "backchannel" and  self.flag_has_security:
		#print("HIER: ", 17)
			return "part_desc_exhausted_security"
		#part_description -> repeat_exercise
		#letzte Anweisun vorgelesen, erster Durchlauf, sieht wiederholung vor, hat security
		

		#elif self.last_description_read() and re.search(self.BACKCHANNEL, utt) and  self.flag_has_repeat and not self.flag_has_completed_one_run and self.flag_has_security: 
		#	self.flag_has_completed_one_run = True
		#	return "part_desc_exhausted_security"

		elif self.flag_has_repeat  and self.current_state.name =="ask_description"  and pred == "negate" and self.flag_run > 1 and not self.flag_has_security:
		#print("HIER: ", 18)
			return "negate_repeat_exercise"
		elif self.flag_has_repeat  and self.current_state.name == "repeat_exercise"  and pred == "backchannel" and self.flag_run > 1:			
		#print("HIER: ", 19)
			return "part_desc_exhausted_repeat_end"
		
		#elif pred == "rest":			
		#print("HIER: ", 21)
		#	return "rest"
		
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
			return "specific"
		
		else:
		#print("HIER: ", 38)
			return pred