from sklearn.feature_extraction.text import TfidfVectorizer, \
															CountVectorizer

from sklearn.pipeline import make_pipeline

from sklearn.neighbors import NearestNeighbors

import spacy

import random


class BrownC:
	def __init__(self, path, \
							corpus_file, \
							brown_c=128, \
							brw_p='prep/brown-cluster-master/', \
							brw_x='wcluster --text ', brw_x2= ' --c '):
		##globals
		
		self.brown_c = str(brown_c)
		self.brw_p = 'input-c'#later
		self.brw_e = '.out/'
		self.clusters = {}
		
		self.make_brw(brw_p + brw_x + path + corpus_file + brw_x2)
	
	def make_brw(self, str_x):
		
		os.system('./' + str_x + self.brown_c)
		print('haeh?')
		self.get_save_brw()
		#self.clean()
	
	def get_save_brw(self, brw_p='-p1', brw_f='paths'):
		with open(self.brw_p + self.brown_c + brw_p + self.brw_e + brw_f, 'r') as f:
			
			for line in f:
				line = line.split('\t')
				self.clusters[line[1]] = line[0]	#binary string itself
			
	
	def clean(self):
		os.system('rm -rf ' + self.brw_p + '*' + self.brw_e)
	
	
	def get(self, word, as_str=False):
		if as_str:
			return self.clusters.get(word, '+$+') #later
			
		else:
			return int(self.clusters.get(word, '+$+'), 2) #later
	









def get_stop_words(stop_words_file='german_stopwords.txt'):
	with open(stop_words_file) as f:
		return sorted([line.strip() for line in f])




class CosineSimilarityVectors:
	def __init__(self, ngram_range_in=1,\
							stop_words_list=get_stop_words()):
		self.Parser = spacy.load('de')
		
		self.pipe = make_pipeline()
		
		if ngram_range_in > 1:
			##BoW
			self.CountVec = CountVectorizer(tokenizer=self.tok_lem,\
													stop_words=stop_words_list,
													ngram_range=(1,ngram_range_in))
			##CosineSim
			self.Tfidf = TfidfVectorizer(ngram_range=(1,ngram_range_in))
		else:
			self.CountVec = CountVectorizer(tokenizer=self.tok_lem,\
													stop_words=stop_words_list)
			self.Tfidf = TfidfVectorizer()
		
	
	def tok_lem(self, sentence):
		return [item.lemma_.lower() \
						for item in self.Parser(sentence) \
						if not item.is_punct]
		
	def cosine_vecs(self, sentences):
		tfidf = self.Tfidf.fit_transform(sentences)
		return (tfidf * tfidf.T).toarray()
		
	










def get_interview(questions=True, \
						responses=False, \
						file_name='wolfgang.txt'):
	corp_out = []
	
	with open(file_name) as f:
		line_bef = ''
		if questions and responses:
			for line in f:
				if line_bef:
					corp_out.append(line_bef + '\t' + line.strip())
					line_bef = ''
				else:
					line_bef = line.strip()
				
		elif questions:
			for line in f:
				if line_bef:
					corp_out.append(line_bef)
					line_bef = ''
				else:
					line_bef = line.strip()
				
		else:#only responses
			for line in f:
				if line_bef:
					corp_out.append(line.strip())
					line_bef = ''
				else:
					line_bef = line.strip()
			
	return corp_out






def make_dialogs(utt_res):
	resp = set()
	responses_us = []
	alt_utts = dict()
	dialogs = [[]]
	#u, r = u_r.split('\t')
	
	for u_r in utt_res:
		u, r = u_r.split('\t')
		if not r in resp:
			resp.add(r)
			dialogs[-1].append((u, r))
		else:
			if r in alt_utts:
				alt_utts[r].append(u)
			else:
				alt_utts[r] = []
		
	return dialogs, alt_utts
		


			

utt_res = get_interview(questions=True, responses=True)


ori_dia, alt_utts = make_dialogs(utt_res)



#print(ori_dia[0])
dias = []
#print('---')
#print('---')
with open('dialog_indices.txt', 'r') as g:
	dialog_indices = [eval(l) for l in g]
	for i, dia_i in enumerate(dialog_indices):
		dias.append(ori_dia[0][dia_i[0] : dia_i[-1]+1])

for d in dias:
	for idx, (q,a) in enumerate(d):
		print(idx+1, q+'\t'+a)
	print()
exit()





more_dia = ori_dia.copy()

buffer_list = []

for index, ut_re in enumerate(ori_dia[0]):
	if ut_re[1] in alt_utts:
		for alt_utt in alt_utts[ut_re[1]]:
			for dia_bef in more_dia:
				buffer_list.append(dia_bef.copy())
				buffer_list[-1][index] = (alt_utt, ut_re[1])
		more_dia +=  buffer_list
		buffer_list = []





#zu teuer
new_dialogs = []
with open('hier') as f:
	with open('dialog_indices.txt') as g:
		dialog_indices = [eval(l) for l in g]
		#print(dialog_indices)
		buf = []
		for line in f:
			line = line.strip()
			if line:
				buf.append(line)
				
			else:
				
				for dia_i in dialog_indices:
					new_dialogs.append(buf[dia_i[0] : dia_i[-1]+1])
				buf.clear()
					
#print('------------------------------------------------')

for dia in new_dialogs:
	for inde, p in enumerate(dia):
		print(inde+1, p)
	print()
#print('------------------------------------------------')
exit()








utt = get_interview()

unseen_test = utt[:round(len(utt) * 1/4)]

utt = utt[round(len(utt) * 1/4):]

SimilarityVectors = CosineSimilarityVectors()

x = SimilarityVectors.cosine_vecs(utt)

top_n = 5

random_idc = set()
while(len(random_idc) != top_n):
	random_idc.add(random.randint(0, len(x)-1))
print('------------------------------------')
print(random_idc)
print('------------------------------------\n')
test = [x[y] for y in random_idc]

for alg in ['ball_tree', 'kd_tree']:
	
	print('Used Search Algorithm :', alg)

	nneighbors = NearestNeighbors(n_neighbors=top_n, \
											algorithm=alg).fit(x)

	dist, idc = nneighbors.kneighbors([x[y] for y in random_idc])

	print()
	for i, idx in enumerate(random_idc):
		print('Looking for neighbors of : "', utt[idx], '"')
		for k, j in enumerate(idc[i]):
			print('Index :', j, '\nDistance :', dist[i][k], '\n' + utt[j])
		print()
			
	print('Indices :', idc, '\nDistances :', dist)
	print('------------------------------------\n')



