'''
Created on 2016-3-29

@author: IRISBEST
'''
import numpy
import sys,os,time,random
from RepresentationLayer import RepresentationLayer
from Constants import *
import Eval
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



if __name__ == '__main__':


    dir = '/home/BIO/zhaozhehuan/relations/'
    dir = '/home/a914/zhaozhehuan/relations/'
    max_sent_len = 100
    max_triple_len = 30
    word_vec_dim = 50
    position_vec_dim = 20
    etype_vec_dim = 20
    dep_vec_dim = 20
    epoch_size = 200
    
    rep = RepresentationLayer(wordvec_file=dir + 'vecfile/pubmed.re.w50.slim.emb', dep_list_file=dir + 'dep.list',
                                frequency = 21840, max_sent_len=max_sent_len, max_triple_len=max_triple_len)

    '''
        channel one
    '''
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


    e1 = Input(shape=(1,), dtype='int32', name='entity1_type')
    e2 = Input(shape=(1,), dtype='int32', name='entity2_type')
    etype_vec_table = numpy.random.uniform(-1,1,(3, etype_vec_dim))
    etype_emb = Embedding(3, etype_vec_dim, \
                             weights = [etype_vec_table])
    e1_vec = etype_emb(e1)
    e1_vec = Flatten()(e1_vec)
    e2_vec = etype_emb(e2)
    e2_vec = Flatten()(e2_vec)


    # generate the input vector for LSTM
    concat_vec_c1 = Concatenate()([word_vec, p1_vec, p2_vec])
    concat_vec_c1 = Dropout(0.5)(concat_vec_c1)

    #dropout_W=0.5,dropout_U=0.5, 
    l_lstm_c1 = LSTM(50, dropout_W=0.5,dropout_U=0.5,activation='tanh')(concat_vec_c1)
    r_lstm_c1 = LSTM(50, dropout_W=0.5,dropout_U=0.5,activation='tanh', go_backwards=True)(concat_vec_c1)


    '''
        channel two
    '''
#     word1 = Input(shape=(max_triple_len,), dtype='int32', name='word1')
#     word1_vec = word_emb(word1)
# 
#     word2 = Input(shape=(max_triple_len,), dtype='int32', name='word2')
#     word2_vec = word_emb(word2)
#     
#     dep = Input(shape=(max_triple_len,), dtype='int32', name='dep')
#     dep_vec_table = numpy.random.uniform(-1,1,(171, dep_vec_dim))
#     for i in range(dep_vec_dim):
#         dep_vec_table[0][i] = 0.
#     dep_emb = Embedding(171, dep_vec_dim, \
#                              weights = [dep_vec_table], mask_zero=True)
#     dep_vec = dep_emb(dep)
 
    # generate the input vector for LSTM
#     concat_vec_c2 = Concatenate()([word1_vec, dep_vec, word2_vec])
#     concat_vec_c2 = Dropout(0.5)(dep_vec)
 
    #dropout_W=0.5,dropout_U=0.5, 
#     l_lstm_c2 = LSTM(50, dropout_W=0.5,dropout_U=0.5, activation='tanh')(concat_vec_c2)
#     r_lstm_c2 = LSTM(50, dropout_W=0.5,dropout_U=0.5, activation='tanh', go_backwards=True)(concat_vec_c2)

    
    '''
        combine two channels
    '''
    comb_lstm = Concatenate()([l_lstm_c1, r_lstm_c1])


    # flattened = Flatten()(bi_lstm)
    dense = Dense(50, activation='tanh')(comb_lstm)
#     dense = Concatenate()([dense, e1_vec, e2_vec])
    dense = Dense(30, activation='tanh')(dense)
#     dense = Dense(10, activation='tanh')(dense)
    predict = Dense(2, activation='softmax')(dense)
    
#     model = Model(inputs=[word, p1, p2, e1, e2], outputs=predict)
    model = Model(inputs=[word, p1, p2], outputs=predict)

    opt = RMSprop(lr=0.001, rho=0.9, epsilon=1e-06)
#    opt = Adagrad(lr=0.01, epsilon=1e-06)
#    opt = Adadelta(lr=1.0, rho=0.95, epsilon=1e-06)
#    opt = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08)
#    opt = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=opt)

#     intermediate_tensor_function = K.function([word, p1, p2], [predict])

    train_list = [ 'gen-dis.train.embed', 'che-dis.train.embed', 'che-che.train.embed', 'gen-gen.train.embed', 'liver.train']
    train_list = [ 'liver.train']

    instances_train = []
    for train_file in train_list:
        instances_train += [line.lower().strip() for line in open(dir + 'data/train/' + train_file)]
    
#     instances_train = [line.lower().strip() for line in open(dir + 'data/train/gen-gen.train.embed')]
    instances_test1 = [line.lower().strip() for line in open(dir + 'data/test/gen-gen.test.embed')]
    instances_test2 = [line.lower().strip() for line in open(dir + 'data/test/gen-dis.test.embed')]
    instances_test3 = [line.lower().strip() for line in open(dir + 'data/test/che-dis.test.embed')]
    instances_test4 = [line.lower().strip() for line in open(dir + 'data/test/che-che.test.embed')]
    instances_test = [line.lower().strip() for line in open(dir + 'data/test/liver.test')]

#     triple_instances_train = [line.lower().strip() for line in open(dir + 'data/Aim-10/train0.triples')]
#     triple_instances_test = [line.lower().strip() for line in open(dir + 'data/Aim-10/test0.triples')]

    label_array, e1_type_array, e2_type_array, \
        word_array, dis_e1_array, dis_e2_array, filtered = rep.represent_instances(instances_train)

#     word1_array, word2_array, dep_array = rep.represent_triple_instances(triple_instances_train, filtered)

    label_array_test1, e1_type_array_test1, e2_type_array_test1, \
        word_array_test1, dis_e1_array_test1, dis_e2_array_test1, filtered_test = rep.represent_instances(instances_test1)
     
    label_array_test2, e1_type_array_test2, e2_type_array_test2, \
        word_array_test2, dis_e1_array_test2, dis_e2_array_test2, filtered_test = rep.represent_instances(instances_test2)
         
    label_array_test3, e1_type_array_test3, e2_type_array_test3, \
        word_array_test3, dis_e1_array_test3, dis_e2_array_test3, filtered_test = rep.represent_instances(instances_test3)
         
    label_array_test4, e1_type_array_test4, e2_type_array_test4, \
        word_array_test4, dis_e1_array_test4, dis_e2_array_test4, filtered_test = rep.represent_instances(instances_test4)

    label_array_test, e1_type_array_test, e2_type_array_test, \
        word_array_test, dis_e1_array_test, dis_e2_array_test, filtered_test = rep.represent_instances(instances_test)


    best_f, best_f1, best_f4, best_f3, best_f2 = 0, 0, 0, 0, 0
    for epoch in xrange(epoch_size):
        print 'running the epoch:', (epoch + 1)
        model.fit([word_array, dis_e1_array, dis_e2_array],label_array, batch_size=128, epochs=1)
        
        answer_array_test = model.predict([word_array_test, dis_e1_array_test, dis_e2_array_test], batch_size=128)
#         p,r,f = Eval.eval_mulclass(label_array_test, answer_array_test)
#         if f > best_f1:
#             print 'New Best F-score for liver', f, p, r
#             best_f1 = f
#             model.save_weights('./dense-50-30-pos20.liver.in.train.h5')

        
        answer_array_test1 = model.predict([word_array_test1, dis_e1_array_test1, dis_e2_array_test1], batch_size=128)
#         p,r,f = Eval.eval_mulclass(label_array_test1, answer_array_test1)
#         if f > best_f1:
#             print 'New Best F-score for gen-gen', f, p, r
#             best_f1 = f
#             FileUtil.writeFloatMatrix(answer_array_test, dir + 'multi-results/gen-on-gen.out')
#             model.save_weights('./lstm_model.h5')
 
        answer_array_test2 = model.predict([word_array_test2, dis_e1_array_test2, dis_e2_array_test2], batch_size=128)
#         p,r,f = Eval.eval_mulclass(label_array_test2, answer_array_test2)
#         if f > best_f2:
#             print 'New Best F-score for gen-dis', f, p, r
#             best_f2 = f
     
        answer_array_test3 = model.predict([word_array_test3, dis_e1_array_test3, dis_e2_array_test3], batch_size=128)
#         p,r,f = Eval.eval_mulclass(label_array_test3, answer_array_test3)
#         if f > best_f3:
#             print 'New Best F-score for che-dis', f, p, r
#             best_f3 = f
             
        answer_array_test4 = model.predict([word_array_test4, dis_e1_array_test4, dis_e2_array_test4], batch_size=128)
#         p,r,f = Eval.eval_mulclass(label_array_test4, answer_array_test4)
#         if f > best_f4:
#             print 'New Best F-score for che-che', f, p, r
#             best_f4 = f
     
        p,r,f = Eval.eval_mulclass(numpy.concatenate((label_array_test1, label_array_test2, \
                                                  label_array_test3, label_array_test4, label_array_test), axis=0),\
                                   numpy.concatenate((answer_array_test1, answer_array_test2,\
                                                   answer_array_test3, answer_array_test4, answer_array_test), axis=0))
        if f > best_f:
            print 'New Best F-score for all ', f, p, r
            best_f = f
#             model.save_weights('./dense-50-30-pos20.liver.in.train.h5')
            
        p,r,f = Eval.eval_mulclass(label_array_test1, answer_array_test1)
        print '\tgen-gen', f, p, r
        p,r,f = Eval.eval_mulclass(label_array_test2, answer_array_test2)
        print '\tgen-dis', f, p, r
        p,r,f = Eval.eval_mulclass(label_array_test3, answer_array_test3)
        print '\tche-dis', f, p, r
        p,r,f = Eval.eval_mulclass(label_array_test4, answer_array_test4)
        print '\tche-che', f, p, r
        p,r,f = Eval.eval_mulclass(label_array_test, answer_array_test)
        print '\tliver', f, p, r
    # test_files = os.listdir(dir + 'data/uptodate_filter/')
    #
    # for file in test_files:
    #     instances = []
    #     instances_visual = []
    #     for line in open(dir + 'data/uptodate_filter/' + file):
    #         instances.append(line.strip())
    #         instances_visual.append(Corpus.change_embed_2_offset(line.strip()))
    #     label_array_test, e1_type_array_test, e2_type_array_test, e_len_array_test, \
    #         word_array_test, e_array_test, dis_e1_array_test, dis_e2_array_test = rep.represent_instances(instances)
    #     answer_array_test = model.predict([word_array_test, dis_e1_array_test, dis_e2_array_test, e_array_test, e1_type_array_test, e2_type_array_test], batch_size=128)
    #     intermediate_tensor = intermediate_tensor_function([word_array_test, dis_e1_array_test, dis_e2_array_test, e_array_test, e1_type_array_test, e2_type_array_test])
    #     x = intermediate_tensor[0]
    #     sample_size = x.shape[0]
    #     elem_size = numpy.nonzero(x[0][0])[0].size
    #     average = x.sum(2)/elem_size
    #     weight = softmax_me(average)
    #     print weight.shape
    #     before_list = ['<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">',
    #                    '<html>',
    #                    '<head>',
    #                    '<meta charset="UTF-8">',
    #                    '<title>uptodate</title>',
    #                    '</head>',
    #                    '<body style="font-family: Times New Roman;font-size:20px">',
    #                    '<font style="background-color: rgb(215,25,28)">Protein</font>&emsp;<font style="background-color: rgb(253,174,97)">DNA</font>&emsp;<font style="background-color: rgb(255,255,191)">RNA</font>&emsp;<font style="background-color: rgb(171,221,164)">Chemical</font>&emsp;<font style="background-color: rgb(0,208,255)">Disease</font>'
    #                     ]
    #     after_list = ['<br \>',
    #                   '</body>',
    #                   '</html>']
    #     list  = Eval.eval_mulclass2(answer_array_test, word_array_test, rep.index_2_word, weight, instances_visual)
    #     FileUtil.writeStrLines(dir + 'data/uptodate_out/' +  file + '.htm', before_list + list + after_list)