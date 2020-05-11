from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_graphviz
import nltk
import re
import numpy as np

BACKCHANNEL = re.compile(r"i'll do it|thanks|thank you|great|^ok[,\.\! ]*|good[ ,\.\!]*|<silence>|aha|mhm|^oki doki|yes|go ahead|keep going|yea", re.IGNORECASE)
AFFIRM = re.compile(r"correct|great|super|yes[,\.\! ]*|yes please|y[eu]p", re.IGNORECASE)
NEGATE = re.compile(r"no$|no +|nope|nah|not yet|not|wait", re.IGNORECASE)
NON_SPECIFIC = re.compile(r"what|how|don't know|didn't hear|say|didn't listen|wasn't listening|huh",re.IGNORECASE)
REPEAT = re.compile(r"again|repeat|more",re.IGNORECASE)
PROTEST = re.compile(r"stop|wait|halt|no more|i can ?nn?['o]?t|hold on|wait|one sec(ond)?",re.IGNORECASE)
READY = re.compile(r"all set|ready|let's go|go ahead|ok|start",re.IGNORECASE)
REST = re.compile(r"out of breath|rest|break|tired",re.IGNORECASE)
FINISH = re.compile(r"stop|enough|no more|finish|done",re.IGNORECASE)
NONUNDERSTANDING = re.compile(r"complicated|complex|confusing|not simple|ah*|don't understand|hard|difficult|what|huh",re.IGNORECASE)
YESNO = re.compile(r"should|my|do",re.IGNORECASE)
class Classifier():
    
    def __init__(self):
        self.utterance_classes = ["backchannel",'affirm','negate','non_specific','specific','repeat','protest','ready','rest','finish','nonunderstanding','yesno']
        self.sentence_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self._clf = DecisionTreeClassifier(random_state=0)
        X = []
        y = []
        
        with open("data/intentTraining_EN.txt") as infile:
            lines = infile.readlines()[3:]
            for i in range(len(lines)):
                if not len(lines[i]):
                    continue
                X.append([])
                if re.search(BACKCHANNEL,lines[i]):
                    X[i].append(1)
                else:
                    X[i].append(0)
                if re.search(AFFIRM,lines[i]):
                    X[i].append(1)
                else:
                    X[i].append(0)
                if re.search(NEGATE,lines[i]):
                    X[i].append(1)
                else:
                    X[i].append(0)
                if re.search(NON_SPECIFIC,lines[i]):
                    X[i].append(1)
                else:
                    X[i].append(0)
                
                parse = self.sentence_detector.tokenize(lines[i])
                X[i].append(int(len([nltk.pos_tag(nltk.word_tokenize(token)) for token in parse if nltk.pos_tag(token) in ["NN","VB", "VBD","VBG","VBN","VBN","VBP","VBP","VBZ"]]) < 1))
                if re.search(REPEAT,lines[i]):
                    X[i].append(1)
                else:
                    X[i].append(0)
                if re.search(PROTEST,lines[i]):
                    X[i].append(1)
                else:
                    X[i].append(0)
                if re.search(READY,lines[i]):
                    X[i].append(1)
                else:
                    X[i].append(0)
                if re.search(REST,lines[i]):
                    X[i].append(1)
                else:
                    X[i].append(0)
                if re.search(FINISH,lines[i]):
                    X[i].append(1)
                else:
                    X[i].append(0)
                if re.search(NONUNDERSTANDING,lines[i]):
                    X[i].append(1)
                else:
                    X[i].append(0)
                if re.search(YESNO,lines[i]):
                    X[i].append(1)
                else:
                    X[i].append(0)
            for line in lines:
                for i,utt_class in enumerate(self.utterance_classes):
                    if line.split("\t")[1].strip("\n") == utt_class:
                        y.append(i)
                
            X =np.array(X)  
            y = np.array(y)
            #print(X.shape)
            #print(y.shape)
            self._clf.fit(X,y)
    #dot =export_graphviz(clf)
    #print(clf.predict([[1,0,0]]))
    def predict(self,utt):
        m = []
        if re.search(BACKCHANNEL,utt):
            m.append(1)
        else:
            m.append(0)
        if re.search(AFFIRM,utt):
            m.append(1)
        else:
            m.append(0)
        if re.search(NEGATE,utt):
            m.append(1)
        else:
            m.append(0)
        if re.search(NON_SPECIFIC,utt):
            m.append(1)
        else:
            m.append(0)
        
        parse = self.sentence_detector.tokenize(utt)
        m.append(int(len([nltk.pos_tag(nltk.word_tokenize(token)) for token in parse if nltk.pos_tag(token) in ["NN","VB", "VBD","VBG","VBN","VBN","VBP","VBP","VBZ"]]) < 1))
        if re.search(REPEAT,utt):
            m.append(1)
        else:
            m.append(0)
        if re.search(PROTEST,utt):
            m.append(1)
        else:
            m.append(0)
        if re.search(READY,utt):
            m.append(1)
        else:
            m.append(0)
        if re.search(REST,utt):
            m.append(1)
        else:
            m.append(0)
        if re.search(FINISH,utt):
            m.append(1)
        else:
            m.append(0)
        if re.search(NONUNDERSTANDING,utt):
            m.append(1)
        else:
            m.append(0)
        if re.search(YESNO,utt):
            m.append(1)
        else:
            m.append(0)
        return self.utterance_classes[self._clf.predict([m])[0]]

#classifier = Classifier()
#while True:
    #x = input()
    #print(classifier.predict(x))
