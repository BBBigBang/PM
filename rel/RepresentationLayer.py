'''
Created on 2014-10-14

@author: IRISBEST
'''
import os, sys
import numpy as np
from Constants import *
import Corpus
import FileUtil
import random


class RepresentationLayer(object):
    
    
    def __init__(self, wordvec_file=None, frequency=None, scale=1, dep_list_file=None
                 , max_sent_len=80, max_triple_len=10, output_size=2):
        
        '''
        vec_size        :    the dimension size of word vector

        frequency       :    the threshold for the words left according to
                             their frequency appeared in the text
                             for example, when frequency is 10000, the most
                             frequent appeared 10000 words are considered
        
        scale           :    the scaling for the vectors' each real value
                             when the vectors are scaled up it will accelerate
                             the training process

        max_sent_len    :   all sentences will be cuted or padded to the max_sent_len size
        
        vec_talbe        :    a matrix each row stands for a vector of a word

        word_index        :    the map from word to corresponding index in vec_table
        
        distance_2_index    : the map from a word's relative distance to corresponding vector's index


        '''
        self.frequency = frequency
        self.scale = scale
        self.max_sent_len = max_sent_len
#         self.max_triple_len = max_triple_len

        self.vec_table, self.word_2_index, self.index_2_word, self.vec_size = self.load_wordvecs(wordvec_file)

        self.entity_type_2_index = {DISEASE:0, CHEMICAL:1, GENE:2}

        self.label_2_index = {TRUE:[1,0], FALSE:[0,1]}

        self.distance_2_index, self.dis_vec_table = self.load_dis_index_table()
        
#         self.dep_2_index = self.generate_dep_index_map(dep_list_file)

        self.y_dim = output_size



    def generate_dep_index_map(self, dep_list_file):
        if dep_list_file is None:
            print 'loss the important input,', 'Dep_list_file'
            exit(0)
        dep_2_index = {PADDING:0}
        index = 1
        for line in open(dep_list_file):
            if dep_2_index.has_key(line.strip()):
                continue
            else:
                dep_2_index[line.strip()] = index
                index += 1
        return dep_2_index
        



    def load_dis_index_table(self):
        dis_vec_list = []
        distance_2_index = {}
        index = 0
        for i in range(-self.max_sent_len, self.max_sent_len):
            distance_2_index[i] = index
            dis_vec_list.extend(self.int2bit_by_distance(i))
            index += 1
        
        dis_vec_table = np.array(dis_vec_list)
        dis_vec_table.resize(self.max_sent_len * 2, 10)
        
        distance_2_index[-self.max_sent_len] = self.max_sent_len
        distance_2_index[0] = 0
        dis_vec_table[0] = self.int2bit_by_distance(0)
        dis_vec_table[self.max_sent_len] = self.int2bit_by_distance(-self.max_sent_len)


        return distance_2_index, dis_vec_table


    def word_2_char_array(self, word_list):
        list = []
        for words in word_list:   
            for word in words:
                for char in word:
                    list.append(self.char_2_index[char])
                for i in range(self.char_size - len(word)):
                    list.append(0)
                
        
        array = np.array(list)
        array = array.reshape((array.shape[0]/self.char_size, self.char_size))
    
        return array            
            
            

    def load_wordvecs(self, wordvec_file):
        
        file = open(wordvec_file)
        first_line = file.readline()
        word_count = int(first_line.split()[0])
        dimension = int(first_line.split()[1])
        considered_words = 0
        
        # the extra 2 includes zero_mask and sparse_word
        if self.frequency != None:
            considered_words = self.frequency
        else:
            considered_words = word_count
            
        vec_table = np.zeros((considered_words + 2, dimension))
            
        word_2_index = {PADDING:0}
        index_2_word = {0:PADDING}
        padding_vector = np.zeros(dimension)
        for col in xrange(dimension):
            vec_table[0][col] = padding_vector[col]

        row = 1
        for line in file:
            if row < considered_words:
                line_split = line[:-1].split()
                word_2_index[line_split[0]] = row
                index_2_word[row] = line_split[0]
                for col in xrange(dimension):
                    vec_table[row][col] = float(line_split[col + 1])
                row += 1
            else:
                break
        
        word_2_index[SPARSE] = row
        index_2_word[row] = SPARSE
        sparse_vectors = np.zeros(dimension)
        for line in file:
            line_split = line[:-1].split()[1:]
            for i in xrange(dimension):
                sparse_vectors[i] += float(line_split[i])

        if word_count > considered_words:
            sparse_vectors /= (word_count - considered_words)

        for col in xrange(dimension):
            vec_table[row][col] = sparse_vectors[col]


        vec_table *= self.scale
        
        file.close()

        return vec_table, word_2_index, index_2_word, dimension



    def indexs_2_labels(self, indexs):
        labels = []
        
        for index in indexs:
            labels.append(self.index_2_label(index))
        
        return labels

    
    

    def generate_distance_features(self, left_part, e1, middle_part, e2, right_part):
        distance_e1 = []
        distance_e2 = []
        len_left = len(left_part)
        len_middle = len(middle_part)
        len_right = len(right_part)

        ### left part
        for i in range(len_left):
            # simplify of -(len_left - i)
            # for position feature about entry1
            distance_e1.append(i - len_left)

            # simplify of -(len_left - i + 1 + len_middle)
            # for position feature about entry2 where 1 stand for len of entry1
            distance_e2.append(i - len_left - 1 - len_middle)

        ### entry1 part
        for e in e1:
            # for position feature about entry1
            distance_e1.append(-self.max_sent_len)

            # for position feature about entry2
            distance_e2.append(-len_middle)

        ### middle part
        for i in range(len_middle):
            # for position feature about entry1
            distance_e1.append(i + 1)

            # simplify of -(len_middle - i)
            # for position feature about entry2
            distance_e2.append(i - len_middle)

        ### entry2 part
        for e in e2:
            # for position feature about entry1
            distance_e1.append(len_middle)

            # for position feature about entry2
            distance_e2.append(-self.max_sent_len)

        ### right part
        for i in range(len_right):
            if right_part[i] == PADDING:
                distance_e1.append(0)
                distance_e2.append(0)
            else:
                # for position feature about entry1
                # where the first 1 stand for the len of entry2
                distance_e1.append(len_middle + 1 + i + 1)
    
                # for position feature about entry2
                distance_e2.append(i + 1)

        return distance_e1, distance_e2


    def represent_instances(self, instances):

        label_list = []
        e1_type_list = []
        e2_type_list = []
        word_index_list = []
        distance_e1_index_list = []
        distance_e2_index_list = []
        filtered = set()
        index = 0
        sample_size = 0
        for instance in instances:
            label, e1_type, e2_type, \
                word_indexs, distance_e1_indexs, distance_e2_indexs = self.represent_instance(instance)
            if label == None:
                filtered.add(index)
                index += 1
                continue
            label_list.extend(self.label_2_index[label])
            e1_type_list.append(self.entity_type_2_index[e1_type])
            e2_type_list.append(self.entity_type_2_index[e2_type])
            word_index_list.extend(word_indexs)
            distance_e1_index_list.extend(distance_e1_indexs)
            distance_e2_index_list.extend(distance_e2_indexs)
            sample_size += 1
            index += 1


        label_array = np.array(label_list)
        label_array = label_array.reshape((sample_size, self.y_dim))

        e1_type_array = np.array(e1_type_list)
        e1_type_array = e1_type_array.reshape((sample_size,1))
        e2_type_array = np.array(e2_type_list)
        e2_type_array = e2_type_array.reshape((sample_size,1))

        word_array = np.array(word_index_list)
        word_array = word_array.reshape((sample_size, self.max_sent_len))

        dis_e1_array = np.array(distance_e1_index_list)
        dis_e1_array = dis_e1_array.reshape((sample_size, self.max_sent_len))

        dis_e2_array = np.array(distance_e2_index_list)
        dis_e2_array = dis_e2_array.reshape((sample_size, self.max_sent_len))
        

        return label_array, e1_type_array, e2_type_array, \
               word_array, dis_e1_array, dis_e2_array, filtered



    def represent_instance(self, instance):

        splited = instance.lower().split(' ')
        label = splited[0]
        e1_type = splited[1]
        e2_type = splited[2]
        sent = self.refresh_sent(splited[3:])

        index_e1_b, index_e1_e, index_e2_b, index_e2_e = -1, -1, -1, -1
        padding_num = 0

        # the extra 4 stands for the 4 words,
        # including entity1begin, entity1end,entity2begin, entity2end
        for index in range(self.max_sent_len + 4):
            if index > len(sent) - 1:
                padding_num += 1
                continue
            if sent[index] == E1_B:
                index_e1_b = index
            elif sent[index] == E1_E:
                index_e1_e = index
            elif sent[index] == E2_B:
                index_e2_b = index
            elif sent[index] == E2_E:
                index_e2_e = index

        # the max length sentence won't contain the
        # two entities
        if index_e2_e == -1:
            return None,None,None,None,None,None

        left_part = sent[:index_e1_b]
        e1 = sent[index_e1_b + 1: index_e1_e]
        middle_part = sent[index_e1_e + 1: index_e2_b]
        e2 = sent[index_e2_b + 1:index_e2_e]
        right_part = sent[index_e2_e + 1:] + [PADDING for i in range(padding_num)]

        distance_e1, distance_e2 = self.generate_distance_features(left_part, e1, middle_part, e2, right_part)

        distance_e1_index_list = self.replace_distances_with_indexs(distance_e1)
        distance_e2_index_list =  self.replace_distances_with_indexs(distance_e2)

        word_list = left_part + e1 + middle_part + e2 + right_part
        word_index_list = self.replace_words_with_indexs(word_list)


        return label, e1_type, e2_type,  word_index_list, distance_e1_index_list, distance_e2_index_list


    '''
        once the sentence length is large than max_sent_len
        it will be cutted surrounding the two entitys
        
    '''
    def refresh_sent(self, word_list):
        new_max_sent_len = self.max_sent_len + 4
        if len(word_list) > new_max_sent_len:
            e1_begin = 0
            e2_end = 0
            for i in range(len(word_list)):
                if word_list[i] == 'bbbbb1':
                    e1_begin = i
                if word_list[i] == 'eeeee2':
                    e2_end = i
                    break
            
            if e2_end - e1_begin < new_max_sent_len:
                core = word_list[e1_begin:e2_end+1]
                left = word_list[:e1_begin]
                right = word_list[e2_end+1:]
                for i in range(100):
                    if len(core) < new_max_sent_len:
                        if len(left) > i:
                            core.insert(0, left[-(i+1)])
                        if len(right) > i:
                            core.append(right[i])
                    else:
                        break
                if len(core) > new_max_sent_len:
                    if core[0] != 'bbbbb1':
                        core = core[1:]
                    else:
                        core.pop()
                        
                return core
            else:
                return word_list[e1_begin:e1_begin+new_max_sent_len]
    
        else:
            return word_list

            
            



    '''
        replace dep list with corresponding indexs
        
    '''
    def replace_deps_with_indexs(self, deps):
        
        dep_indexs = []
        for dep in deps:
            if self.dep_2_index.has_key(dep):
                dep_indexs.append(self.dep_2_index[dep])
            else:
                print 'IMPOSSIBLE!'
                exit(0)
        
        return dep_indexs


    '''
        replace word list with corresponding indexs
        
    '''
    def replace_words_with_indexs(self, words):
        
        word_indexs = []
        for word in words:
            if self.word_2_index.has_key(word):
                word_indexs.append(self.word_2_index[word])
            else:
                word_indexs.append(self.word_2_index[SPARSE])
        
        return word_indexs

    '''
        replace distance list with corresponding indexs

    '''

    def replace_distances_with_indexs(self, distances):

        distance_indexs = []
        for distance in distances:
            if self.distance_2_index.has_key(distance):
                distance_indexs.append(self.distance_2_index[distance])
            else:
                print 'Impossible! This program will stop!'
                sys.exit(0)

        return distance_indexs


    '''
        replace label list with corresponding indexs
        
    '''
    def replace_labels_with_indexs(self, labels):
        
        label_indexs = []
        for label in labels:
            if self.label_2_index.has_key(label):
                label_indexs.append(self.label_2_index[label])
            else:
                print 'Unexcepted label', label, 'in', self.scheme, 'Scheme'
                sys.exit()
        
        return label_indexs





    '''
        reprensent instance of (word, dep, word) triples
    
    '''
    def represent_triple_instance(self, instance):

        splited = instance.split('\t')
        words1 = []
        words2 = []
        deps = []

        for triple in splited:
            triple = triple[1:-1]
            words1.append(triple.split(', ')[0])
            deps.append(triple.split(', ')[1])
            words2.append(triple.split(', ')[2])
            
        for i in range(self.max_triple_len - len(deps)):
            words1.append(PADDING)
            words2.append(PADDING)
            deps.append(PADDING)


        word1_index_list = self.replace_words_with_indexs(words1)
        word2_index_list = self.replace_words_with_indexs(words2)
        dep_index_list = self.replace_deps_with_indexs(deps)

        return word1_index_list, word2_index_list, dep_index_list
    



    '''
        reprensent instances of (word, dep, word) triples
    
    '''
    def represent_triple_instances(self, instances, filtered_indexs):

        word1_list = []
        word2_list = []
        dep_list = []
        index = 0
        sample_size = 0
        for instance in instances:
            if index in filtered_indexs:
                index += 1
                continue
            word1_indexs, word2_indexs, dep_indexs = self.represent_triple_instance(instance)
            word1_list.append(word1_indexs)
            word2_list.append(word2_indexs)
            dep_list.append(dep_indexs)
            sample_size += 1
            index += 1


        word1_array = np.array(word1_list)
        word1_array = word1_array.reshape((sample_size, self.max_triple_len))

        word2_array = np.array(word1_list)
        word2_array = word2_array.reshape((sample_size, self.max_triple_len))

        dep_array = np.array(dep_list)
        dep_array = dep_array.reshape((sample_size, self.max_triple_len))

        return word1_array, word2_array, dep_array

    



 
    '''
        bit_array generated with the distance between 
        two entities where abs_num represents the distance
     
    '''
    def int2bit_by_distance(self,int_num, bit_len=10):
        
        bit_array = np.zeros(bit_len)
        if int_num > 0:
            bit_array[0] = 1
            
        abs_num = np.abs(int_num)
        if abs_num <= 5:
            for i in range(abs_num):
                bit_array[-i-1] = 1
        elif abs_num <= 10:
            for i in range(6):
                bit_array[-i-1] = 1
        elif abs_num <= 20:
            for i in range(7):
                bit_array[-i-1] = 1
        elif abs_num <= 30:
            for i in range(8):
                bit_array[-i-1] = 1
        else:
            for i in range(9):
                bit_array[-i-1] = 1
        return bit_array
            
            
    
    def int2bit_onehot(self, int_num, bit_len=8):
        bit_array = np.zeros(bit_len)
        bit_array[int_num] = 1
        return bit_array
    

    def int2bit(self, int_num, bit_len):
        # once the length of the bit_str
        # is smaller than bit_len, then
        # it will be filled by 0 
        
        if np.abs(int_num) >= 2 ** (bit_len - 1):
            print '********* int number overflow error ! *********'
            return None
        
        bit_array = np.zeros(bit_len) 
        # where the first bit is sign bit
        # 1 for postive and 0 for negtive
        # therefore it can represent
        # [-2**(bit_len-1) , 2**(bit_len-1)]
       
        bit_str = bin(int_num)
        if bit_str.startswith('-'):
            bit_str = bit_str[3:]
        else:
            bit_str = bit_str[2:]
            bit_array[0] = 1
        
        for i in range(-1, -len(bit_str) - 1, -1):
            bit_array[i] = bit_str[i]
        
        return bit_array


    def get0bit(self, bit_len):
        return np.zeros(bit_len)
    
    def get1bit(self, bit_len):
        return np.ones(bit_len)    


if __name__ == '__main__':
    rep = RepresentationLayer(wordvec_file='C:/Users/ZZH/Desktop/pubmed.w50.gene.emb',
                              frequency=10000, dep_list_file='C:/Users/ZZH/Desktop/dep.list')
    instances = [line.strip() for line in open('C:/Users/ZZH/Desktop/multi-re/ADE.embed')]
    
    # to print the instances indexs
    label_array, e1_type_array, e2_type_array,\
               word_array, dis_e1_array, dis_e2_array, filtered = rep.represent_instances(instances)
    
#     FileUtil.writeFloatMatrix(dis_e2_array, 'C:/Users/ZZH/Desktop/tempt.txt')
    
#     files = os.listdir('C:/Users/ZZH/Desktop/uptodate/')
#     for file in files:
#         instances = []
#         for instance in open('C:/Users/ZZH/Desktop/uptodate/' + file):
#             if len(instance.strip().split(' ')) - 7 < 80:
#                 instances.append(instance.strip())
#         FileUtil.writeStrLines('C:/Users/ZZH/Desktop/uptodate/' + file + '.filter', instances)
# 
#     rep.represent_instances(instances)
        # label, e1_type, e2_type, len_e, e_index_list, word_index_list, distance_e1_index_list, distance_e2_index_list = rep.represent_instance(instance)
        # print instance
        # print e_index_list
        # print word_index_list
        # print distance_e1_index_list
        # print distance_e2_index_list
        # print label, e1_type, e2_type, len_e

            
