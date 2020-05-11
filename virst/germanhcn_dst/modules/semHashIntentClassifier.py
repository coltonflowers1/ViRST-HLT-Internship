import pickle
import numpy as np
import json
import pandas as pd
import re
import sys
#from treetagger import TreeTagger
from nltk.corpus import stopwords
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
from sklearn.linear_model import LogisticRegression as LR
from sklearn.tree import DecisionTreeClassifier as DTC
from sklearn.naive_bayes import GaussianNB as GNB
from sklearn.decomposition import TruncatedSVD
from sklearn.model_selection import cross_val_score
from sklearn import preprocessing

#access different columns of Dataframe (string, pos, lemmata, nostops, hasInsult)
class KeySelector(BaseEstimator, TransformerMixin):

	def __init__(self,  key):
		self.key = key

	def fit(self, x, y=None):
		return self

	def transform(self, data):
		#print("DATA: {}, KEY:{}".format(data, self.key))
		return data[self.key]



with open("../data/intentTraining.txt")as corpus:
	data = {"text":[],"cat":[]} 
	
	for line in corpus:
		data["text"].append(line.split("\t")[0])
		data["cat"].append(line.split("\t")[1].strip("\n"))

	df = pd.DataFrame(data=data)

pipeline = Pipeline([
					#("chi",SelectKBest(chi2, k =500)),
					#("tree", DTC()),
					("clf", svm.SVC(kernel='rbf', C=6, gamma="scale",  probability=True)),
					#("classifier", svm.LinearSVC(C=1.0, penalty="l1", dual=False, max_iter =100000))
					#("logReg", LR(C=1.0, penalty="l1", dual=False, max_iter =100000))
					 ])
pipe = Pipeline([
				("union", FeatureUnion(
				transformer_list=[
					("char_ngram", Pipeline([
						("dataselection", KeySelector(key="text")),
						("cng", TfidfVectorizer(analyzer='char_wb', ngram_range=(4, 5), binary=True)),
						#("scaler",preprocessing.StandardScaler(copy=True, with_mean=False, with_std=True)),
						])),
					("char_ngram2", Pipeline([
						("dataselection", KeySelector(key="text")),
						("cng", TfidfVectorizer(analyzer='char', ngram_range=(4, 5), binary=True)),
						#("scaler",preprocessing.StandardScaler(copy=True, with_mean=False, with_std=True)),
						])),
					("bow", Pipeline([
						("dataselection", KeySelector(key="text")),
						("cng", TfidfVectorizer(ngram_range=(1,3), sublinear_tf=True)),
						])),
					],
					# weight components in FeatureUnion
				transformer_weights={
					'char_ngram': 1.0,
					"char_ngram2": 1.0,
					'bow':1.0,
				   
					},
				)),
				("classifier", pipeline)
				 ])


X_train, X_test, y_train, y_test = train_test_split(df, df)
model = pipe.fit(X_train, y_train.cat)
pickle.dump(model,open("../data/uttType.p", "wb"))
print(X_test)
print("F1 Score {}".format(f1_score(y_test.cat,model.predict(X_test), average="micro")))
print("Accuraccy Score offence {}".format(accuracy_score(y_test.cat, model.predict(X_test))))
scores = cross_val_score(pipe, df, df["cat"], cv=10)
print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
	u = ""
	print(model.classes_)
	#print(df.text)

	while u != "\n":
		u = input(":: ")
		n = {"text":[], "cat":[]}
		n["text"].append(u)
		n["cat"].append(None)
		df = pd.DataFrame(n)
		prediction = model.predict(df)

		for i in range(model.classes_.shape[0]):
			if model.predict(df) == model.classes_[i]:
				print("Preditction: {}, Confidence: {}".format(model.predict(df), model.predict_proba(df)[0][i]))
				break
elif len(sys.argv) > 1 and sys.argv[1] == "--i":
	with open("../data/tagged_virst_train_new_summary.txt", encoding="utf-8") as infile:
		for line in infile:
			if line =="\n":
				continue
			u = line.split("\t")[0]
			n = {"text":[], "cat":[]}
			n["text"].append(u)
			n["cat"].append(None)
			df = pd.DataFrame(n)
			prediction = model.predict(df)
			for i in range(model.classes_.shape[0]):
				if model.predict(df) == model.classes_[i]:
					print("Utteranc: {}, Preditction: {}, Confidence: {}".format(u, model.predict(df), model.predict_proba(df)[0][i]))
					break
			


else: 
	
	exit()