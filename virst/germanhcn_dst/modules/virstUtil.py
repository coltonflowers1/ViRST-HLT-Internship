################
#Hilfsfunktionen für Daten verarbeitung etc.
#
################
import itertools
import re
def read_dialogs(errors=False, with_indices=False, dialogs= 'data/tagged_virst_train_new_summary_en.txt'):
        with open(dialogs, encoding='utf-8') as f:#'data/clean.txt', encoding='utf-8') as f:#   
                #dialogs ist liste von von listen von frage-antwort-paaren und tag [[frage, antwort, tag], [frage, antwort, tag]]
                dialogs = [row.split('\t') for row in  f.read().split('\n') ]
                #dialogs = filter_([ rm_index(row.split('\t')) for row in  f.read().split('\n') ])
                #print(dialogs)
                prev_idx = -1
                n = 1
                dialog_indices = []
                updated_dialogs = []
                if errors == False:
                        error = re.compile(r"[01]+S")
                        no_errors_dialogs = []
                        for i in range(len(dialogs)):
                                if not dialogs[i][0]:
                                        no_errors_dialogs.append(dialogs[i])
                                elif re.search(error, dialogs[i][1]) == None:
                                        no_errors_dialogs.append(dialogs[i])
                                else:
                                        while i < len(dialogs)-1 and dialogs[i][0]:
                                                i+=1
                        
                                        no_errors_dialogs.append(dialogs[i])
                                        
                        print(no_errors_dialogs[-10:])
                        dialogs = []
                        for i in range(len(no_errors_dialogs)):
                                if no_errors_dialogs[i] == [''] and no_errors_dialogs[i+1][0] != 'start':
                                        continue
                                dialogs.append(no_errors_dialogs[i])
                        
                #print(dialogs)
                for i, dialog in enumerate(dialogs):
                        if not dialogs[i][0]:
                                dialog_indices.append({'start' : prev_idx + 1, 'end' : i - n + 1})
                                prev_idx = i-n
                                n += 1
                        else:
                                updated_dialogs.append(dialog)
                if with_indices:
                        return updated_dialogs, dialog_indices[:-1]
                return updated_dialogs

#gibt liste von Äußerungen zurück
def get_utterances(dialogs=[], dialog_indices=[]):
        dialogs = dialogs if len(dialogs) else read_dialogs()
        #print(row[0] for row in dialogs)
        return [ row[0] for row in dialogs ]

# gibt liste von (Antworten, index_im_dialog) zurück
def get_responses(dialogs=[], with_indices = False):
        if  with_indices == False:
                dialogs = dialogs if len(dialogs) else read_dialogs()
                #for row in dialogs:
                        #print(row[1]) # find row with typo, error, whatever
                return [row[1] for row in dialogs ]
        else:
                dialogs = dialogs if len(dialogs) else read_dialogs(with_indices=True)
                responses = []
                indices = dialogs[1]
                for indx in indices:
                        n = 0
                        for i in range(indx["start"], indx["end"]):
                                #print(dialogs[0][i])
                                responses.append((dialogs[0][i][1:], i+n - i))
                                n+= 1
                #print(responses)
                return responses

def get_dialog_acts(dialogs=[]):
        dialogs = dialogs if len(dialogs) else read_dialogs()
        return [row[2] for row in dialogs]

def get_dialog_acts_from_file(dialogs):
        dialogs = read_dialogs(dialogs)
        return [row[2] for row in dialogs]

def get_dialog_acts_texts (dialogs=[]):
        dialogs = dialogs if len(dialogs) else read_dialogs()
        return [row[1] for row in dialogs]

def read_content():
        return ' '.join(get_utterances())

def flatten(listOfLists):
    return itertools.chain.from_iterable(listOfLists)

