import gensim
import numpy as np
from modules.virstUtil import read_dialogs
import spacy


class UtteranceEmbed():

	# add path to pretrained model
	#beim training von 'german.model' wurde gross-kleinschreibung beachtet!, und unique woerter nicht dabei (z.b. "wildschwein-problem")
	def __init__(self, dataset, fname='data/glove_en_model.bin', dim=300): #training data in
		self.dim = dim
		self.to_repl = str.maketrans({'ä' : 'ae',\
												'ö' : 'oe',\
												'ü' : 'ue',\
												'Ä' : 'Ae',\
												'Ö' : 'Oe',\
												'Ü' : 'Ue',\
												'ß' : 'ss'})
		try:
			print(':: load saved word2vec model, umlauts and sharp s are  NOT replaced')
			#self.model = gensim.models.word2vec.Word2Vec.load(fname)
			self.model =  gensim.models.KeyedVectors.load_word2vec_format(fname, binary=True)
		except:
			print(':: creating new word2vec model, not yet, exiting')
			exit('w2v No model!!')
			self.create_model(dataset)
			self.model = gensim.models.word2vec.Word2Vec.load(fname)


	def encode(self, utterance):
		#utterance = utterance.translate(self.to_repl)
		embs = [ self.model[word.lower()] for word in utterance.split(' ') if word and word.lower() in self.model.vocab]
		# average of embeddings
		if len(embs):
			return np.mean(embs, axis=0)
		else:
			return np.zeros([self.dim],np.float32)

	# train new model: add path to corpus
	def create_model(self, dataset):
		#sentences = word2vec.LineSentence('data/news.2010.de.shuffled.corpus')
		sentences = []
		p = spacy.load('en')
		for u, at in dataset:
			sentences.append([it.lemma_ for it in p(u.lower().strip()) if not (it.is_stop or \
																									it.is_bracket or \
																									it.is_space or \
																									it.is_punct)])

		model = gensim.models.word2vec.Word2Vec(sentences, size=self.dim, min_count=1)
		model.save('data/english.model')
		print(':: model saved to data/english.model')





#class UtteranceEmbed():
	
	#def __init__(self):
		
