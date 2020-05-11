import tensorflow as tf
from tensorflow.contrib.layers import xavier_initializer as xav
import os

import numpy as np

class LSTM_net():

        def __init__(self, obs_size, action_size, nb_hidden=128): # action_size=16 in english models

                self.obs_size = obs_size
                self.nb_hidden = nb_hidden
                self.action_size = action_size
                
                def variable_summarize(var):
                        mean = tf.reduce_mean(var)
                        tf.summary.scalar('mean',mean)
                        stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
                        tf.summary.scalar('stddev', stddev)
                        tf.summary.scalar('max', tf.reduce_max(var))
                        tf.summary.scalar('min', tf.reduce_min(var))
                        tf.summary.histogram('histogram', var)   

                def __graph__():
                        tf.reset_default_graph()

                        # entry points
                        features_ = tf.placeholder(tf.float32, [1, obs_size], name='input_features')
                        init_state_c_, init_state_h_ = ( tf.placeholder(tf.float32, [1, nb_hidden]) for _ in range(2) )
                        action_ = tf.placeholder(tf.int32, name='ground_truth_action')
                        # action_mask disabled (line 22, 49, 74, 96, 112)
                        action_mask_ = tf.placeholder(tf.float32, [action_size], name='action_mask')

                        # input projection
                        with tf.name_scope("input"):
                                with tf.name_scope("weights"):
                                        Wi = tf.get_variable('Wi', [obs_size, nb_hidden],
                                                        initializer=xav())
                                        variable_summarize(Wi)
                                with tf.name_scope("biases"):
                                        bi = tf.get_variable('bi', [nb_hidden],
                                                        initializer=tf.constant_initializer(0.))
                                        variable_summarize(bi)

                        # add relu/tanh here if necessary
                                with tf.name_scope("projected_features"):
                                
                                        projected_features = tf.matmul(features_, Wi) + bi
                                        tf.summary.histogram('histogram',projected_features)

                        lstm_f = tf.contrib.rnn.LSTMCell(nb_hidden, state_is_tuple=True)

                        lstm_op, state = lstm_f(inputs=projected_features, state=(init_state_c_, init_state_h_))

                        # reshape LSTM's state tuple (2,128) -> (1,256)
                        state_reshaped = tf.concat(axis=1, values=(state.c, state.h))

                        # output projection

                        with tf.name_scope("outputs"):
                                with tf.name_scope("weights"):
                                        Wo = tf.get_variable('Wo', [2*nb_hidden, action_size],
                                                        initializer=xav())
                                        variable_summarize(Wo)
                                with tf.name_scope("biases"):
                                        bo = tf.get_variable('bo', [action_size],
                                                initializer=tf.constant_initializer(0.))
                                        variable_summarize(bo)
                        # get logits
                                with tf.name_scope("logits"):
                                        logits = tf.matmul(state_reshaped, Wo) + bo
                                        tf.summary.histogram('histogram',logits)
                        # probabilities
                        #  normalization : elemwise multiply with action mask
                        
                        probs = tf.multiply(tf.squeeze(tf.nn.softmax(logits)), action_mask_)
                        
                        #print("PROBS : ", probs)
                        # prediction
                        prediction = tf.argmax(probs, dimension=0)

                        # loss
                        loss = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=action_,name ="loss")

                        tf.summary.scalar('loss', tf.squeeze(loss))

                        # train op
                        train_op = tf.train.AdadeltaOptimizer(0.1).minimize(loss)



                        # attach symbols to self
                        self.loss = loss
                        self.prediction = prediction
                        self.probs = probs
                        self.logits = logits
                        self.state = state
                        self.train_op = train_op

                        # attach placeholders
                        self.features_ = features_
                        self.init_state_c_ = init_state_c_
                        self.init_state_h_ = init_state_h_
                        self.action_ = action_
                        self.action_mask_ = action_mask_
                        self.merged = tf.summary.merge_all()
                        

                # build graph
                __graph__()

                # start a session; attach to self
                sess = tf.Session()
                self.sess = sess
                #initialize the summary folder
                if not os.path.exists('summaries'):
                        os.mkdir('summaries')
                if not os.path.exists(os.path.join('summaries','first')):
                        os.mkdir(os.path.join('summaries','first'))
                self.summ_writer = tf.summary.FileWriter(os.path.join('summaries','first'), self.sess.graph)
                sess.run(tf.global_variables_initializer())
                # set init state to zeros
                self.init_state_c = np.zeros([1,self.nb_hidden], dtype=np.float32)
                self.init_state_h = np.zeros([1,self.nb_hidden], dtype=np.float32)
                self.step_number = 0

             

        # forward propagation
        def forward(self, features, action_mask, action_t, print_top=False):
                # forward
                probs, prediction, state_c, state_h = self.sess.run( [self.probs, self.prediction, self.state.c, self.state.h], 
                                        feed_dict = { 
                                                self.features_ : features.reshape([1,self.obs_size]), 
                                                self.init_state_c_ : self.init_state_c,
                                                self.init_state_h_ : self.init_state_h,
                                                self.action_mask_ : action_mask
                                                })
                # maintain state                
                self.init_state_c = state_c
                self.init_state_h = state_h
                # return argmax         
                if print_top:
                        #print(probs)
                        top_probs = [(0.0, -1)]
                        for i, p in enumerate(probs):
                                for j, (p2, _) in enumerate(top_probs[:5]):
                                        if p > p2:
                                                top_probs.insert(j, (p, i))
                                                break
                        
                        for top_prob, idx in top_probs[:5]:
                                if idx >= 0:
                                        print(idx, '\t', top_prob ,'\t', action_t[idx])         
                #top_probs = [i for i, p in enumerate(probs)]
                return prediction

        # training
        def train_step(self, features, action, action_mask):
                if self.step_number % 1000 == 0:
                        prediction, _, loss_value,merged, state_c, state_h= self.sess.run( [self.prediction, self.train_op, self.loss,self.merged, self.state.c, self.state.h],
                                                feed_dict = {
                                                        self.features_ : features.reshape([1, self.obs_size]),
                                                        self.action_ : [action],
                                                        self.init_state_c_ : self.init_state_c,
                                                        self.init_state_h_ : self.init_state_h,
                                                        self.action_mask_ : action_mask
                                                        })
                        self.summ_writer.add_summary(merged,self.step_number)
                        self.loss_sum = merged
                else:
                        prediction, _, loss_value,state_c, state_h= self.sess.run( [self.prediction, self.train_op, self.loss, self.state.c, self.state.h],
                                                feed_dict = {
                                                        self.features_ : features.reshape([1, self.obs_size]),
                                                        self.action_ : [action],
                                                        self.init_state_c_ : self.init_state_c,
                                                        self.init_state_h_ : self.init_state_h,
                                                        self.action_mask_ : action_mask
                                                        })
                #print(action_mask)
                self.init_state_c = state_c
                self.init_state_h = state_h
                self.step_number += 1
                return loss_value, prediction
                

        def reset_state(self):
                # set init state to zeros
                self.init_state_c = np.zeros([1,self.nb_hidden], dtype=np.float32)
                self.init_state_h = np.zeros([1,self.nb_hidden], dtype=np.float32)

        # save session to checkpoint
        def save(self):
                saver = tf.train.Saver()
                saver.save(self.sess, 'ckpt/hcn.ckpt', global_step=0)
                print('\n:: saved to ckpt/hcn.ckpt \n')

        # restore session from checkpoint
        def restore(self):
                saver = tf.train.Saver()
                ckpt = tf.train.get_checkpoint_state('ckpt/')
                if ckpt and ckpt.model_checkpoint_path:
                        print('\n:: restoring checkpoint from', ckpt.model_checkpoint_path, '\n')
                        saver.restore(self.sess, ckpt.model_checkpoint_path)
                else:
                        print('\n:: <ERR> checkpoint not found! \n')

