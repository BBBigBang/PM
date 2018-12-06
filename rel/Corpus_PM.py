
from Constants import *
from tokenization import *
import FileUtil
import copy


'''
     it will replace '(', ')', '[', ']', '.' ahead of connect
     the words with slash
     since '(', ')', '[', ']', '.' will affect the following
     the finding coordinate clusters process 
'''
def connect_with_slash(text):
    splited = text.replace('(', '_').replace(')', '_').replace('[','_').replace(']','_')\
        .replace('/','_').replace('.','_').split(' ')
    if len(splited) > 1:
        return '_'.join(splited)
    else:
        return splited[0]

def connect_all_entities(sent, entity_offsets):
    begin, end =  -1, -1
    for offset in entity_offsets:
        begin = int(offset.split('-')[0])
        end = int(offset.split('-')[1])
        sent = sent[:begin] + connect_with_slash(sent[begin:end]) + sent[end:]
    return sent 

def change_embed_2_offset(sent):
    b_index = sent.find(E1_B)
    e_index = sent.find(E1_E)
    left = sent[:b_index].strip()
    E1 = sent[b_index + len(E1_B) : e_index].strip()
    right = sent[e_index + len(E1_E):].strip()
    sent = left + ' ' + E1 + ' ' + right
    offset1_b = len(left) + 1
    if left == '':
        sent = sent.strip()
        offset1_b -= 1
    offset1_e = offset1_b + len(E1)
    assert sent[offset1_b:offset1_e] == E1
    index_e1 = len(left.split())
        
    b_index = sent.find(E2_B)
    e_index = sent.find(E2_E)
    left = sent[:b_index].strip()
    E2 = sent[b_index + len(E2_B) : e_index].strip()
    right = sent[e_index + len(E2_E):].strip()
    sent = left + ' ' + E2 + ' ' + right
    offset2_b = len(left) + 1
    if left == '':
        sent = sent.strip()
        offset2_b -= 1

    offset2_e = offset2_b + len(E2)
    assert sent[offset2_b:offset2_e] == E2
    index_e2 = len(left.split())
    
    return str(offset1_b) + ' ' + str(offset1_e) \
        + ' ' + str(offset2_b) + ' ' + str(offset2_e)\
         , sent, index_e1, index_e2


def filter_double_symbols(text):
    return text.replace('-_','_').replace('_-','_')\
                .replace('/_','/').replace('_/','/')\
                .replace(',_', '_')\
                .replace('__','_').replace('__','_').replace('__','_')


def filter_pre_next_slash(text):

    while len(text) > 0 and (text[0] == '_' or text[0] == '-'):
        text = text[1:]
    while len(text) > 0 and (text[-1] == '_' or text[-1] == '-'):
        text = text[:-1]
    return text


def change_offset_2_embed(offset, sent):
    
    begin1 = int(offset.split()[0])
    end1 = int(offset.split()[1])                    
    begin2 = int(offset.split()[2])
    end2 = int(offset.split()[3])
    
    if begin1 > begin2:
        tempt = begin1
        begin1 = begin2
        begin2 = tempt
        tempt = end1
        end1 = end2
        end2 = tempt                

    left = ' '.join([filter_pre_next_slash(elem) for elem in filter_double_symbols(sent[:begin1]).split()])
    e1 = filter_pre_next_slash(filter_double_symbols(sent[begin1:end1]))
    middle = ' '.join([filter_pre_next_slash(elem) for elem in filter_double_symbols(sent[end1: begin2]).split()])
    e2 = filter_pre_next_slash(filter_double_symbols(sent[begin2:end2]))
    right = ' '.join([filter_pre_next_slash(elem) for elem in filter_double_symbols(sent[end2:]).split()])
    
    
    '''
        deal the circumstance that
        prot1/prot2 where only prot1 is the current entity
        or prot1-x where only prot1 is the current entity
    '''
    if len(left) > 0 and left[-1] == '/':
        left = left.rpartition(' ')[0] + ' '
    if len(middle) > 0 and middle[0] == '/':
        middle = ' ' + middle.partition(' ')[2]
    if len(middle) > 0 and middle[-1] == '/':
        middle = middle.rpartition(' ')[0] + ' '
    if len(right) > 0 and right[0] == '/':
        right = ' ' + right.partition(' ')[2]

    new_sent = left + ' ' + E1_B + ' ' + e1\
                    + ' ' + E1_E + ' ' + middle + ' ' + E2_B\
                    + ' ' + e2  + ' ' + E2_E + ' ' +  right

    if new_sent.endswith('.'):
        return new_sent[:-1].strip()

    return new_sent


def read_entity_term(entity_term):
    splited = entity_term.split('\t')
    begin = int(splited[0])
    end = int(splited[1])
    text = splited[2]
    type = splited[3]
    concept_id = splited[4].replace('|','_')
    
    return begin, end, text, type, concept_id


def extract_instance_from_abs(abs, e1_begin, e1_end, e2_begin, e2_end):
    end = abs.find('. ', e2_end)
    if end == -1:
        abs += '.'
    else:
        pre = abs[:end]
        while end != -1:
            if pre.endswith('i.e') or pre.endswith('i.v') \
                or pre.endswith('vs')\
                or pre.endswith('i.p') or pre.endswith('i.c'):
                end = abs.find('. ', end + 1)
            elif abs[end+2][0].isupper():
                break
            else:
                end = abs.find('. ', end + 1)
            pre = abs[:end]
        
    begin = abs[:end].rfind('. ')
    if begin == -1:
        begin = -2
    else:
        pre = abs[:begin]
        while begin != -1:
            if pre.endswith('i.e') or pre.endswith('i.v') \
                or pre.endswith('vs')\
                or pre.endswith('i.p') or pre.endswith('i.c'):
                begin = abs[:begin].rfind('. ')
            elif abs[begin+2][0].isupper():
                break
            else:
                begin = abs[:begin].rfind('. ')        
            pre = abs[:begin]
            
    if begin <= e1_begin and (end >= e2_end or end == -1):
        sent = abs[begin+2:end]
        offset = len(abs[:begin+2])
        sent = sent[:e1_begin-offset] + ' ' + E1_B + ' ' \
           + sent[e1_begin-offset: e1_end-offset] + ' ' + E1_E + ' '\
            + sent[e1_end-offset: e2_begin-offset] + ' ' + E2_B + ' '\
             + sent[e2_begin-offset: e2_end-offset] + ' ' + E2_E + ' '\
              + sent[e2_end-offset:]
        return sent
    else:
        return None

'''
    after inserting bbbbbx and eeeeex, some whitespace are appeared which
    casuse difference when changing to offset format.
    To solve above problem we will insert some whitespace in advance
'''
def insert_whitespace_around_some_symbols(sent_embed):
    sent_embed = sent_embed.replace('(', ' ( ').replace(')', ' ) ')\
                            .replace('/', ' / ').replace(']', ' ] ')\
                            .replace('  ', ' ').replace('  ', ' ')
    return sent_embed

def gen_insts_from_abstract(abstract, entities, entity_map):
    insts_embed = []
    insts_offset = []
    for i in range(len(entities)):
        for j in range(i+1, len(entities)):
            
            e1_b, e1_e, e2_b, e2_e = entities[i][0], entities[i][1], entities[j][0], entities[j][1]
            
            sent_embed = extract_instance_from_abs(abstract, e1_b, e1_e, e2_b, e2_e)
            
            if sent_embed is not None:
                
                sent_embed = insert_whitespace_around_some_symbols(sent_embed)
                
                if not sent_embed.endswith('.'):
                    sent_embed += ' .'

                inst_embed = 'false gene gene ' + sent_embed
                insts_embed.append(token_common(inst_embed))
                
                offset, sent,_,_ = change_embed_2_offset(sent_embed)
                inst_offset = 'false|' + offset + '|' + entity_map[entities[i]][1] + ' ' + entity_map[entities[j]][1] + '|' + sent + \
                                '|' +  str(e1_b) + ' ' + str(e1_e) + ' ' + str(e2_b) + ' ' + str(e2_e) + \
                                '|' + entity_map[entities[i]][2] + ' ' + entity_map[entities[j]][2]
                insts_offset.append(inst_offset)
            else:
                break
    
    return insts_embed, insts_offset
    

def gen_insts_from_abstracts(abstract_file):
    
    insts_embed_list = []
    insts_offset_list = []

    is_abs = True
    abstract = ''
    entities = []
    entity_map = {}
    for line in open(abstract_file):
        if line.strip() == '':
            insts_embed, insts_offset = gen_insts_from_abstract(abstract, entities, entity_map)
            insts_embed_list.extend(insts_embed)
            insts_offset_list.extend(insts_offset)
            entities = []
            entity_map = {}
            is_abs = True
            continue
        if is_abs:
            abstract = line.strip()
            is_abs = False
        else:
            begin, end, text, type, concept_id = read_entity_term(line.strip())
            entity_map[(begin, end)] = (text, type, concept_id)
            entities.append((begin, end))
    
    print 'Generate', len(insts_embed_list), 'instances successfully!'
    
    return insts_embed_list, insts_offset_list


def gen_insts_from_one_abstract(abstract, entity_list):
    
    entities = []
    entity_map = {}
    for entity in entity_list:
            entity_map[(entity[0], entity[1])] = (entity[2], entity[3], entity[4].replace('|', '_'))
            entities.append((entity[0], entity[1]))
    
    insts_embed, insts_offset = gen_insts_from_abstract(abstract, entities, entity_map)
    
    return insts_embed, insts_offset


'''
    process instances to input to the stanford parser
    1. the entities consists of several words will be connected
    2. the punctions like ",",";",etc. will be seperated by previous words
    3. 
'''
def process_insts_4_parser_bak(true_insts_list):
    inst_index_list = []
    sent_list = []
    e_types = []
    labels = []
    offsets = []
    old_offsets = []
    scores = []
    concept_ids = []
    pre_sent = '' #for connect entity words in the same sents
    pre_sent2 = '' #for generate RPT for do not parse repeated sents
    count = 0
    for line in true_insts_list:
        count += 1
        sent = line.split('|')[3]
        if sent != pre_sent and pre_sent != '':
            offset_set = set()
            for offset in offsets:
                offset_set.add(offset.split()[0] + '-' + offset.split()[1])
                offset_set.add(offset.split()[2] + '-' + offset.split()[3])
            
            sent = connect_all_entities(pre_sent, offset_set)
            
            for index in range(len(labels)):
                sent_embed = change_offset_2_embed(offsets[index], sent)
                sent_embed = token_4_parser(sent_embed)
                off, sent_offset, e1_index, e2_index = change_embed_2_offset(sent_embed)   
                inst_index_list.append(labels[index] + '\t' \
                                       + str(e1_index) + '\t' + str(e2_index) + '\t' \
                                       + sent_offset.split()[e1_index] + '\t' \
                                       + sent_offset.split()[e2_index] + '\t' + e_types[index] + '\t' + scores[index] \
                                       + '\t' + old_offsets[index] + '\t' + concept_ids[index])
                
                sent_list.append(sent_offset)
            
            labels = []
            offsets = []
            old_offsets = []
            e_types = []
            scores = []
            concept_ids = []
        
        splited = line.split('|')
        pre_sent = splited[3]     
        labels.append(splited[0])
        e_types.append(splited[2])
        offsets.append(splited[1])
        old_offsets.append(splited[4])
        scores.append(splited[5])
        concept_ids.append(splited[6])
        
        
    offset_set = set()
    for offset in offsets:
        offset_set.add(offset.split()[0] + '-' + offset.split()[1])
        offset_set.add(offset.split()[2] + '-' + offset.split()[3])
    
    sent = connect_all_entities(pre_sent, offset_set)
    
    for index in range(len(labels)):
        sent_embed = change_offset_2_embed(offsets[index], sent)
        sent_embed = token_4_parser(sent_embed)
        off, sent_offset, e1_index, e2_index = change_embed_2_offset(sent_embed)   
        inst_index_list.append(labels[index] + '\t' \
                               + str(e1_index) + '\t' + str(e2_index) + '\t' \
                               + sent_offset.split()[e1_index] + '\t' \
                               + sent_offset.split()[e2_index] + '\t' + e_types[index] + '\t' + scores[index] \
                               + '\t' + old_offsets[index] + '\t' + concept_ids[index])
        sent_list.append(sent_offset)
    
    return inst_index_list, sent_list

def process_insts_4_parser(true_insts_list):
    inst_index_list = []
    sent_list = []
    e_types = []
    labels = []
    offsets = []
    old_offsets = []
    scores = []
    concept_ids = []
    pre_sent = '' #for connect entity words in the same sents
    pre_sent2 = '' #for generate RPT for do not parse repeated sents
    count = 0
    for line in true_insts_list:
        count += 1
        sent = line.split('|')[3]
        if sent != pre_sent and pre_sent != '':
            offset_set = set()
            for offset in offsets:
                offset_set.add(offset.split()[0] + '-' + offset.split()[1])
                offset_set.add(offset.split()[2] + '-' + offset.split()[3])
            
            sent = connect_all_entities(pre_sent, offset_set)
            
            for index in range(len(labels)):
                sent_embed = change_offset_2_embed(offsets[index], sent)
                sent_embed = token_4_parser(sent_embed)
                off, sent_offset, e1_index, e2_index = change_embed_2_offset(sent_embed)   
                inst_index_list.append(labels[index] + '\t' \
                                       + str(e1_index) + '\t' + str(e2_index) + '\t' \
                                       + sent_offset.split()[e1_index] + '\t' \
                                       + sent_offset.split()[e2_index] + '\t' + e_types[index] + '\t' + scores[index] \
                                       + '\t' + old_offsets[index] + '\t' + concept_ids[index])
                
                if sent_offset == pre_sent2:
                    sent_list.append('RPT')
                else:
                    sent_list.append(sent_offset)
                    pre_sent2 = sent_offset
            
            labels = []
            offsets = []
            old_offsets = []
            e_types = []
            scores = []
            concept_ids = []
        
        splited = line.split('|')
        pre_sent = splited[3]     
        labels.append(splited[0])
        e_types.append(splited[2])
        offsets.append(splited[1])
        old_offsets.append(splited[4])
        scores.append(splited[5])
        concept_ids.append(splited[6])
        
        
    offset_set = set()
    for offset in offsets:
        offset_set.add(offset.split()[0] + '-' + offset.split()[1])
        offset_set.add(offset.split()[2] + '-' + offset.split()[3])
    
    sent = connect_all_entities(pre_sent, offset_set)
    
    for index in range(len(labels)):
        sent_embed = change_offset_2_embed(offsets[index], sent)
        sent_embed = token_4_parser(sent_embed)
        off, sent_offset, e1_index, e2_index = change_embed_2_offset(sent_embed)   
        inst_index_list.append(labels[index] + '\t' \
                               + str(e1_index) + '\t' + str(e2_index) + '\t' \
                               + sent_offset.split()[e1_index] + '\t' \
                               + sent_offset.split()[e2_index] + '\t' + e_types[index] + '\t' + scores[index] \
                               + '\t' + old_offsets[index] + '\t' + concept_ids[index])
        
        if sent_offset == pre_sent2:
            sent_list.append('RPT')
        else:
            sent_list.append(sent_offset)
            pre_sent2 = sent_offset
    
    return inst_index_list, sent_list

def get_wordlist_of_sent(embed_inst):
    splited = embed_inst.split(' ')
    word_list = []
    e1_index = -1
    e2_index = -1
    for elem in splited:
        if elem == E1_B:
            e1_index = len(word_list)
        elif elem == E2_B:
            e2_index = len(word_list)
        elif elem == E1_E or elem == E2_E:
            continue
        else:
            word_list.append(elem)
    return e1_index, e2_index, word_list


def is_the_same_entity(e1_index, e2_index, word_list):
    if word_list[e1_index].lower() == word_list[e2_index].lower():
        return True
    elif e2_index - e1_index == 2 and word_list[e1_index + 1] == '(':
        return True
    elif e2_index - e1_index == 3 and (word_list[e1_index+1] == '(' or word_list[e1_index+2] == '('):
        return True
    else:
        return False

def ignore_parances(word_list):
    
    if len(word_list) > 0 and word_list[0] == ')':
        word_list = word_list[1:]
    
    if len(word_list) > 0 and word_list[0] == '(':
        index = 0
        for word in word_list:
            if word == ')':
                word_list = word_list[index+1:]
                break
            else:
                index += 1
    
    copy = True
    new_word_list = []
    for word in word_list:
        if word == '(':
            copy = False
            continue
        elif word == ')':
            copy = True
            continue
        if copy:
            new_word_list.append(word)
    
    return new_word_list
    

def is_coordinate_relationship(e1_index, e2_index, word_list):
    
    if e1_index != 0:
        left = word_list[e1_index-1]
    else:
        left = ''
    
    if len(word_list) > e2_index+1:
        right = word_list[e2_index+1]
    else:
        right = ''
    
    word_list =  ignore_parances(word_list[e1_index+1:e2_index])
    
    coor_set = set([',','and','or'])
    comma_num = 0
    and_or_num = 0
    word_num = 0
    for word in word_list:
        if word == ',':
            comma_num += 1
        elif word == 'and' or word == 'or':
            and_or_num += 1
        else:
            word_num += 1
    if comma_num + and_or_num >=2:
        if word_num - comma_num - and_or_num == -1:
            return True
    else:
        if comma_num == 1 and word_num == 0:
            if left == ',' or right in coor_set:
                return True 
        elif and_or_num == 1 and word_num == 0:
            if left == ',':
                return True 
            
    return False



def filter_possible_negatives(insts_embed_list, insts_offset_list):
    
    insts_list = copy.deepcopy(insts_offset_list)
    
    filter_index_set = set()
        
    labels = []
    offsets = []
    pre_sent = '' #for connect entity words in the same sents
    count = 0
    for line in insts_list:
        sent = line.split('|')[3]
        if sent != pre_sent and pre_sent != '':
            offset_set = set()
            for offset in offsets:
                offset_set.add(offset.split()[0] + '-' + offset.split()[1])
                offset_set.add(offset.split()[2] + '-' + offset.split()[3])
            
            sent = connect_all_entities(pre_sent, offset_set)
            
            for index in range(len(labels)):
                sent_embed = change_offset_2_embed(offsets[index], sent)
                sent_embed = token_4_parser(sent_embed)
                e1_index, e2_index, word_list = get_wordlist_of_sent(sent_embed)
                if is_the_same_entity(e1_index, e2_index, word_list):
                    filter_index_set.add(count)
                    count += 1
                    continue
                elif is_coordinate_relationship(e1_index, e2_index, word_list):
                    filter_index_set.add(count)
                    count += 1
                    continue
                count += 1
           
            labels = []
            offsets = []
        
        splited = line.split('|')
        pre_sent = splited[3]     
        labels.append(splited[0])
        offsets.append(splited[1])
        
    offset_set = set()
    for offset in offsets:
        offset_set.add(offset.split()[0] + '-' + offset.split()[1])
        offset_set.add(offset.split()[2] + '-' + offset.split()[3])
    
    sent = connect_all_entities(pre_sent, offset_set)
    
    for index in range(len(labels)):
        sent_embed = change_offset_2_embed(offsets[index], sent)
        sent_embed = token_4_parser(sent_embed)
        e1_index, e2_index, word_list = get_wordlist_of_sent(sent_embed)

        if is_the_same_entity(e1_index, e2_index, word_list):
            filter_index_set.add(count)
            count += 1
            continue
        elif is_coordinate_relationship(e1_index, e2_index, word_list):
            filter_index_set.add(count)
            count += 1
            continue
        count += 1
        
    new_embed_list, new_offset_list = [], []
    
    for i in range(len(insts_embed_list)):
        if i not in filter_index_set:
            new_embed_list.append(insts_embed_list[i])
            new_offset_list.append(insts_offset_list[i])
    
    print 'Filtered ', len(insts_list)-len(new_embed_list), 'instances successfully!'
    
    return new_embed_list, new_offset_list


if __name__ == '__main__':


    input_file = 'C:/Users/ZZH/Desktop/abstracts.ner_nor'
 
    insts_embed_list, insts_offset_list = gen_insts_from_abstracts(input_file)
    new_embed_list, new_offset_list = filter_possible_negatives(insts_embed_list, insts_offset_list)
     
#     FileUtil.writeStrLines('C:/Users/ZZH/Desktop/filtered.inst.txt', new_inst_list)
#     FileUtil.writeStrLines('C:/Users/Think/Desktop/offset.tempt', insts_offset_list[3])
        


       
