from virstTrain import Trainer
from virstInteract import InteractiveSession
import sys
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.pipeline import FeatureUnion
# create pipeline for combining features etc.
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, label_ranking_average_precision_score, accuracy_score
from sklearn import svm


class KeySelector(BaseEstimator, TransformerMixin):

	def __init__(self,  key):
		self.key = key

	def fit(self, x, y=None):
		return self

	def transform(self, data):
		#print("DATA: {}, KEY:{}".format(data, self.key))
		return data[self.key]



if len(sys.argv) > 10:
	exit('ERROR : Too many arguments\nAvailable arguments : [train, interact, verbose, update, write_to_file, train_ratio=(unsigned int "/" unsigned int), epochs=(unsigned int), topics=(unsigned int), ngram_size=(unsigned int)]')

elif len(sys.argv) < 2:
	exit('ERROR : Not enough arguments supplied : [train, interact, verbose, update, write_to_file, train_ratio=(unsigned int "/" unsigned int), epochs=(unsigned int), topics=(unsigned int), ngram_size=(unsigned int)]')


train = False
interact = False
ratio = 5/6
epochs = 800
verbose = False
update = False
write_to_file = False

for arg in sys.argv[1:]:

	if arg == 'train':
		train = True

	elif arg == 'interact':
		interact = True

	elif arg == "verbose":
		verbose = True

	elif arg == "update":
		update = True

	elif arg == "write_to_file":
		
		write_to_file = True

	elif arg[:11] == 'train_ratio':
		if arg[13:]:
			nom_den = arg[12:].split('/')
			if len(nom_den) != 2:
				exit('ERROR : No ratio found, maybe " / " missing, or too many " / "?')
			else:
				if nom_den[0] == '0':
					exit('ERROR : Nominator equals 0')
				if nom_den[1] == '0':
					exit('ERROR : Denominator equals 0!!!')

				if nom_den[0].isdigit() and nom_den[1].isdigit():
					nomi = int(nom_den[0])
					deno = int(nom_den[1])
				else:
					exit('ERROR : Ratio does not consist of digits')
				if nomi > deno:
					exit('ERROR : Nominator > Denominator, no ratio')
				ratio = nomi/deno
		else:
			exit('ERROR : train_ratio not specified, try " train_ratio=1/2 "')

	elif arg[:6] == 'epochs':
		if arg[7:] and arg[7:].isdigit():
			epochs = int(arg[7:])
		else:
			exit('ERROR : Either num of epochs not specified or num of epochs does not consist of digits')

	else:
		exit('ERROR : Wrong mode "{}": [train, interact, update, train_ratio=(unsigned int "/" unsigned int), epochs=(unsigned int), topics=(unsigned int), ngram_size=(unsigned int)]'.format(arg))



#type(topics) == str !


trainer = Trainer(train_ratio=ratio, \
						epochs=epochs, \
						train_whole=train, \
						)

if train:
	trainer.train()

if interact:
	iteractive_session = InteractiveSession()

	iteractive_session.interact(verbose, update, write_to_file)
