from enum import Enum
import numpy as np
import spacy


#Wird im Moment nicht benutzt
""" This Module is currently not part of the system"""

class EntityTracker():

	def __init__(self):
		self.context_features = np.zeros(5, dtype=np.float32)
	#nimmt Paare: (utterance, index_im_dialog)
		self.size_context_features = len(self.context_features)
	def set_context_features(self, index):
		self.reset_context_features()
		self.context_features[index]=1
		return 

	def reset_context_features(self):
		self.context_features = np.zeros(5, dtype=np.float32)
		return 

	def get_context_features(self):
	   return self.context_features

	def action_mask(self):
		print('Not yet implemented. Need a list of action templates!')
