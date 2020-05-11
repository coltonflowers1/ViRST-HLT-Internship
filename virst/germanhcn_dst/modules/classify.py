from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_graphviz

import re
import numpy as np
clf = DecisionTreeClassifier(random_state=0)

BACKCHANNEL = re.compile(r"i'll do it|thanks|thank you|great|^ok[,\.\! ]*|good[ ,\.\!]*|<silence>|aha|mhm|^oki doki|yes|go ahead|keep going|yea", re.IGNORECASE)
AFFIRM = re.compile(r"correct|great|super|yes[,\.\! ]*|yes please|y[eu]p", re.IGNORECASE)
NEGATE = re.compile(r"no$|no +|nope|nah|not yet|not|wait|hold on|enough|one second", re.IGNORECASE)
X = []
y = []
with open("../data/intentTraining_EN.txt") as infile:
        lines = infile.readlines()
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
        for line in lines:
                if line.split("\t")[1].strip("\n") == "backchannel":
                        y.append(1)
                elif line.split("\t")[1].strip("\n") == "affirm":
                        y.append(2)
                else:
                        y.append(3) 
        
        X =np.array(X)  
        y = np.array(y)
        print(X.shape)
        print(y.shape)
        clf.fit(X,y)
        dot =export_graphviz(clf)
        print(clf.predict([[1,0,0]]))
        i = ""
        while (i != ":"):
                i = input(">>")
                m = []
                if re.search(BACKCHANNEL,i):
                        m.append(1)
                else:
                        m.append(0)
                if re.search(AFFIRM,i):
                        m.append(1)
                else:
                        m.append(0)
                if re.search(NEGATE,i):
                        m.append(1)
                else:
                        m.append(0)
                print(m)
                print(clf.predict([m]))
