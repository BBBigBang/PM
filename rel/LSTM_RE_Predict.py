'''
Created on 2016-3-29

@author: IRISBEST
'''
import numpy
import sys,os,time,random
from RepresentationLayer import RepresentationLayer
from Constants import *
import FileUtil
import Corpus

from keras import models
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Activation
from keras.layers import Embedding, Input
from keras.layers import LSTM, SimpleRNN
from keras.layers.merge import Concatenate
from keras.layers.convolutional import Conv1D, MaxPooling1D
from keras.layers.core import Reshape,Lambda, Flatten, RepeatVector,Permute
from keras.optimizers import RMSprop, SGD, Adam, Adadelta, Adagrad
from keras.layers.wrappers import TimeDistributed, Bidirectional
from keras import backend as K
from Constants import home_dir

model_file = home_dir + 'data/liver.in.train.h5'
max_sent_len = 100
word_vec_dim = 50
position_vec_dim = 20


def load_model(model_file, home_dir):

    rep = RepresentationLayer(wordvec_file=home_dir + 'data/pubmed.re.w50.slim.emb',
                                frequency = 21840, max_sent_len=max_sent_len)

    word = Input(shape=(max_sent_len,), dtype='int32', name='word')
    word_emb = Embedding(rep.vec_table.shape[0], rep.vec_table.shape[1],
                         weights = [rep.vec_table], mask_zero=True)
    word_vec = word_emb(word)

    p1 = Input(shape=(max_sent_len,), dtype='int32', name='position1')
    p2 = Input(shape=(max_sent_len,), dtype='int32', name='position2')
    dis_vec_table = numpy.random.uniform(-1,1,(max_sent_len * 2, position_vec_dim))
    for i in range(position_vec_dim):
        dis_vec_table[0][i] = 0.
    position_emb = Embedding(max_sent_len * 2, position_vec_dim, \
                             weights = [dis_vec_table], mask_zero=True)
    p1_vec = position_emb(p1)
    p2_vec = position_emb(p2)

    # generate the input vector for LSTM
    concat_vec = Concatenate()([word_vec, p1_vec, p2_vec])
    concat_vec = Dropout(0.5)(concat_vec)

    #dropout_W=0.5,dropout_U=0.5, 
    l_lstm = LSTM(50, dropout=0.5,recurrent_dropout=0.5,activation='tanh')(concat_vec)
    r_lstm = LSTM(50, dropout=0.5,recurrent_dropout=0.5,activation='tanh', go_backwards=True)(concat_vec)

    comb_lstm = Concatenate()([l_lstm, r_lstm])

    # flattened = Flatten()(bi_lstm)
    dense = Dense(50, activation='tanh')(comb_lstm)
    dense = Dense(30, activation='tanh')(dense)
#     dense = Dense(10, activation='tanh')(dense)
    predict = Dense(2, activation='softmax')(dense)
    
    model = Model(inputs=[word, p1, p2], outputs=predict)

    opt = RMSprop(lr=0.001, rho=0.9, epsilon=1e-06)
    model.compile(loss='categorical_crossentropy', optimizer=opt)

    model.load_weights(model_file)
    
    return model, rep

def binary_relation_extraction(instances_test, model, rep):
    label_array_test, _, _, \
        word_array_test, dis_e1_array_test, dis_e2_array_test, filtered_test = rep.represent_instances(instances_test)

    answer_array_test = model.predict([word_array_test, dis_e1_array_test, dis_e2_array_test], batch_size=128)
    return answer_array_test, filtered_test


def get_true_insts(insts_offset_list, answer_array_test, filtered_index, threshold=0.5):
    
    '''
        filtered_index contains the indexs of instances whose lengths are longer
        than the max_sent_len and be removed before
    '''
    assert len(insts_offset_list) == len(answer_array_test) + len(filtered_index)
    rest_insts_offset = []
    for i in range(len(insts_offset_list)):
        if i not in filtered_index:
            rest_insts_offset.append(insts_offset_list[i])
    
    
    assert len(rest_insts_offset) == len(answer_array_test)
    true_inst_list = []
    index = 0
    for elem in answer_array_test[:,0]:
        if elem > threshold:
            if rest_insts_offset[index].split('|')[2] == 'disease disease':
                if elem > 0.9:
                    true_inst_list.append(rest_insts_offset[index] + '|' + str(elem))
            else:
                true_inst_list.append(rest_insts_offset[index] + '|' + str(elem))
        
        index += 1 
    
    return true_inst_list   

if __name__ == '__main__':

    model_file = ''
    instances_test = [line.lower().strip() for line in open(dir + 'data/test/liver.test')]
    binary_relation_extraction(model_file, instances_test)
    

            
    
    
    
    
    
