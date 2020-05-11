from bert_serving.client import BertClient
'''
        BERT Embedder

        1. With Bert Client connected to server, creates object to serve bert
        encoding requests.
        2. Initialize dictionary from sentences to bert embeddings
        3. Embed a sentence using the encode method. 

'''
class UtteranceEmbed():
        
        def __init__(self,dim = 768):
                self.bc = BertClient()
                self.encoding_dict = {}
                self.dim = dim

        def encode(self, utterance):
                if utterance not in self.encoding_dict:
                        encoding = self.bc.encode([utterance])[0]
                        self.encoding_dict[utterance] = encoding
                        if len(encoding) != self.dim:
                                print("wrong bert dimesions")
                        return encoding
                else:
                        encoding = self.encoding_dict[utterance]
                        return encoding
