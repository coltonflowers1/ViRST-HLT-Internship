#######################
#Author: Erik Haegert
#Klasse implementiert einfaches Dialoggedächtnis
########################



class Memory():
	"""
	A class used to represent the dialogue memory.

		Attributes
		-----------
		exercise : str
			The name of current exercise
		action_memory : list
			The memory tracking the sequence of instructions given to the user
		max : int
			A number indicating the number of instructions contained in the current exercise
	"""
	
	def __init__(self):
		self.exercise = ""
		self.action_memory = []
		self.max = 0
		return 
	
	
	def set_exercise(self, exercise):
		"""
		Sets exercise to the current exercise.

		Parameters
		----------
		exercise :	str 

		Returns
		-------
		Null
		"""

		self.exercise = exercise
		return 

	def update(self,action):
		"""
		Adds the number of an instruction given to the user to the memory.

		Parameters
		----------
		action : int

		Returns
		-------
		Null
		"""

		self.action_memory.append(action)
		return 

	def get_last_action(self):
		"""
		Returns the number of last instruction given to the user.
		In case all instructions have allready been given -1 is returned

		Returns
		-------
		int
			The number of the last instruction given to the user.
			Zero if no instruction has yet been given.
			-1 if all instructions of the current exercise have allready been given.
		"""
		if len(self.action_memory)== 0:
			return 0
		if self.action_memory[-1] == self.max:
			return self.max
		return self.action_memory[-1]

	def reset_memory(self, exercise):
		"""
		Resets action_memory to an empty list. 
		Sets exercise to the current exercise.

		Parameters
		----------
		exercise : str

		Returns
		-------
		Null
		"""
		self.action_memory = []
		self.exercise = exercise
		return 


	def is_in_memory(self,action):
		"""
		Checks if a certain instruction has allready been given to the user.

		Parameters
		----------
		action : int

		Returns
		-------
		bool
			True if action is in actionmemory else False.	
		"""
		if action in self.action_memory: 
			return True 
		return False

	#gibt Fortschritt in Reihenfolge der Anweisungen zurück	
	# (=wie weit ist man, abgesehen von Wiederholungen, bisher schon gekommen?) 
	def progress(self):
		"""
		Returns the progress made at the moment of calling of the function
		i.e. the instruction with the highest number so far.
		
		Returns
		-------
		int
			Highest instruction number given to the user so far. 	
		"""
		if len(self.action_memory):
			return max(self.action_memory)
		return 0
