# -*- coding: utf-8 -*-
'''
Created on 2015-5-7

@author: IRISBEST
'''
import string
import sys, os, re
import FileUtil
from Constants import *

entity_type_map = {'drug':'chemical', 'protein':'gene','disease':'disease','dna':'gene','rna':'gene'}



def luoling_token4(infile, outfile):
    punctuation1 = ['.', '!', '?', '"']
    punctuation2 = ['•', '●', '-', ':', ';', '%', '+', '=', '~', '#', '$', '&', '*', '/', '@', \
                    '"', '?', '!', '[', ']', '{', '}', '(', ')', '<', '>', \
                    '→', '↓', '←', '↔', '↑', '≃', '⁺', '···', '®', '≧', '≈', '⋅⋅⋅', '·', '…', '‰', '€', '≥', '∼', \
                    'Δ', '≤', 'δ', '™', '•', '∗', '⩾', 'Σ', 'Φ', '∑', 'ƒ', '≡', '═', 'φ', 'Ψ', '˙', 'Π', '≫']
    punctuation3 = [',']  # tokened when there are whitespace arrounding
    punctuation4 = ["'"]  # 's or s', etc.
    fin = open(infile, 'r')
    fout = open(outfile, 'w')
    for line in fin:
        line = line.strip()
        for pun in punctuation2:
            line = line.replace(pun, " " + pun + " ")
        # print(line)
        if line != '':
            if line[-1] in punctuation1:
                line = line[:-1] + " " + line[-1] + " "

        new_line = ""
        i = 0

        while (len(line) != 0):
            if (i == len(line) - 1):
                new_line = new_line + line[0:i + 1]
                break
            elif line[i] in punctuation3:
                if line[i - 1] == ' ' or line[i + 1] == ' ':
                    new_line = new_line + line[:i] + " " + line[i] + " "
                    line = line[i + 1:]
                    i = 0
                else:
                    i = i + 1
            else:
                i = i + 1

        line = new_line + " "
        new_line = ""
        i = 0
        while (len(line) != 0):
            if (i == len(line) - 1):
                new_line = new_line + line[0:i + 1]
                break
            elif line[i] in punctuation4:
                if line[i - 1] == ' ' or line[i + 1] == ' ':
                    new_line = new_line + line[:i] + " " + line[i] + " "
                    line = line[i + 1:]
                    i = 0
                elif line[i + 1] == 's' and line[i + 2] == ' ':
                    new_line = new_line + line[:i] + " " + line[i] + "s "
                    line = line[i + 2:]
                    i = 0
                else:
                    i = i + 1
            else:
                i = i + 1

        words = new_line.split()
        new_line = ""
        for word in words:
            new_line += word + " "

        fout.write(new_line + "\n")



def process_punctuations(text):
    
    text = text.replace('-',' - ')\
                .replace(', ',' , ')\
                .replace('+',' + ')\
                .replace('>',' > ')\
                .replace('<',' < ')\
                .replace('/', ' / ')\
                .replace('; ', ' ; ')\
                .replace(': ', ' : ')\
                .replace('? ', ' ? ')\
                .replace(" '", " ")\
                .replace("'s ", " 's ")\
                .replace("s' ", "s 's ")\
                .replace("' ", " ")\
                .replace(")", " ) ")\
                .replace("(", " ( ")\
                .replace("]", " ] ")\
                .replace("[", " [ ")\
                .replace("}", " } ")\
                .replace("{", " { ")\
                .replace('"', '')\
                .replace('!', '')\
                .replace('#', '')\
                .replace('$', '')\
                .replace('&', '')\
                .replace('*', '')\
                .replace('@', '')\
                .replace('~', '')\
                .replace('|', '')\
                .replace('%', '')\
                .replace('  ', ' ')\
                .replace('  ', ' ')\
                .replace('  ', ' ')
    return text

          


def translator(frm='', to='', delete='', keep=None):
    if len(to) == 1:
        to = to * len(frm)
    
    trans = string.maketrans(frm, to)
    if keep is not None:
        trans_all = string.maketrans('', '')
        delete = trans_all.translate(trans_all, keep.translate(trans_all, delete))
        
    def translate(s):
        return s.translate(trans, delete)
        
    return translate


def filter_non_ascii(input, extra=" .,-—+<>/;:?'[]{}()"):

    ascii_only = translator(keep=string.ascii_letters + string.digits + extra)
    
    return ascii_only(input)


def filter_non_ascii2(input, extra=" .,-_+<>/;:?'[]{}()"):
    ascii_only = translator(keep=string.ascii_letters + string.digits + extra)

    return ascii_only(input)

def generate_offset(sent):
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
    return sent, offset1_b, offset1_e, offset2_b, offset2_e

def change_embed_2_offset(sent):
    splited = sent.split(' ')
    flag = splited[0]
    e1_type = splited[1]
    e2_type = splited[2]
    sent = ' '.join(splited[3:])
    sent, e1_begin, e1_end, e2_begin, e2_end = generate_offset(sent)
    instance = flag + '(none)|' + str(e1_begin) + ' ' + str(e1_end) + \
                ' ' + str(e2_begin) + ' ' + str(e2_end) + \
                '|gene(protein) gene(protein)' + sent + '|0000|aim'
    return instance




def change_offset_2_embed(sent):
    splited = sent.split('|')
    label = splited[0].partition('(')[0]
    e1_type = splited[2].partition('(')[0]
    e2_type = splited[2].partition(') ')[2].partition('(')[0]
    indexs = [int(elem) for elem in splited[1].split(' ')]
    text = splited[3][:indexs[0]] + E1_B \
           + splited[3][indexs[0]: indexs[1]] + E1_E\
            + splited[3][indexs[1]: indexs[2]] + E2_B\
             + splited[3][indexs[2]: indexs[3]] + E2_E\
              + splited[3][indexs[3]:]
    text = text.replace('  ', ' ').replace('  ', ' ')
    instance = label + ' ' + e1_type + ' ' + e2_type + ' ' + text

    return instance


def writeStrLines(fileName, strlist):
    writeObj = open(fileName, 'w')
    writeObj.write('\n'.join(strlist))
    writeObj.close()

def get_first_index_and_type(sentence):
    disease_index = sentence.find('<disease>')
    drug_index = sentence.find('<drug>')
    protein_index = sentence.find('<protein>')
    rna_index = sentence.find('<rna>')
    dna_index = sentence.find('<dna>')
    first = 100000
    first_type = None
    if disease_index != -1 and disease_index < first:
        first = disease_index
        first_type = 'disease'
    if drug_index != -1 and drug_index < first:
        first = drug_index
        first_type = 'drug'
    if protein_index != -1 and protein_index < first:
        first = protein_index
        first_type = 'protein'
    if rna_index != -1 and rna_index < first:
        first = rna_index
        first_type = 'rna'
    if dna_index != -1 and dna_index < first:
        first = dna_index
        first_type = 'dna'
    return first, first_type

def generate_offsets_for_sentence(sentence):
    entity_types, offsets = [], []
    first, first_type = get_first_index_and_type(sentence)
    while first != 100000:
        first_end = sentence.find('</' + first_type + '>')
        left = sentence[:first].strip()
        entity = sentence[first + len(first_type) + 2:first_end].strip()
        right = sentence[first_end + len(first_type) + 3:].strip()
        sentence = left + ' ' + entity + ' ' + right
        if len(left) == 0:
            begin = 0
        else:
            begin = len(left) + 1
        end = begin + len(entity)
        entity_types.append(first_type)
        offsets.append((begin,end))
        first, first_type = get_first_index_and_type(sentence)

    return  sentence, entity_types, offsets



def generate_instances_offset(sentence, entity_types, offsets, sent_id):
    instances = []
    for i in range(len(offsets)):
        for j in range(i+1, len(offsets)):
            e1 = sentence[offsets[i][0]:offsets[i][1]]
            e2 = sentence[offsets[j][0]:offsets[j][1]]
            between_them = sentence[offsets[i][1]:offsets[j][0]]
            if between_them.find('(') != -1 and between_them.find(')') == -1:
                pass
            elif between_them.find('[') != -1 and between_them.find(']') == -1:
                pass
            elif between_them.find(':') != -1:
                pass
            elif between_them.find('—') != -1:
                pass
            elif e1.strip() == e2.strip():
                pass
            else:
                instances.append('false(none)|' + str(offsets[i][0]) + ' ' + str(offsets[i][1]) +
                             ' ' + str(offsets[j][0]) + ' ' + str(offsets[j][1]) + '|' +
                             entity_type_map[entity_types[i]] + '(' + entity_types[i] + ')' + ' ' +
                             entity_type_map[entity_types[j]] + '(' + entity_types[j] + ')' + '|' + sentence +
                             '||' + sent_id)
    return instances



def generate_instances_from_luoling_uptodate(sentence, sent_id):
    if len(sentence.split(' ')) > 100:
        return None
    sentence = sentence.replace('<disease> tumor </disease>', 'tumor') \
            .replace('<disease> cancer </disease>', 'cancer') \
        .replace('<disease> tumors </disease>', 'tumors') \
        .replace('<disease> cancers </disease>', 'cancers') \
        .replace('<disease> Tumor </disease>', 'Tumor') \
            .replace('<disease> Cancer </disease>', 'Cancer')\
            .replace('-','_')
    sentence = filter_non_ascii(sentence)
    entity_num = sentence.count('<disease>') + sentence.count('<dna>') + \
                sentence.count('<drug>') + sentence.count('<protein>') + sentence.count('<rna>')
    if entity_num < 2:
        return None

    sentence, entity_types, offsets = generate_offsets_for_sentence(sentence)
    instances = generate_instances_offset(sentence, entity_types, offsets, sent_id)

    return instances


def findout_two_entitys(sent):
    entity_list = []
    for i in range(len(sent)):
        if sent[i].startswith('disease_'):
            entity_list.append((str(i),'disease'))
        elif sent[i].startswith('chemical_'):
            entity_list.append((str(i), 'chemical'))
        elif sent[i].startswith('gene_'):
            entity_list.append((str(i), 'gene'))
        else:
            pass

    return entity_list

def get_all_parents(e_index, dep, parent_indexs, pos):

    if dep.has_key(e_index):
        parents = dep[e_index]
        for parent in parents:
            if parent[0] not in parent_indexs:
                parent_indexs.add(parent[0])
                if not pos[int(parent[0])].startswith('V'):
                    get_all_parents(parent[0], dep, parent_indexs, pos)
            else:
                break
    else:
        return

def direct_interaction(e1_index, e2_index, dep):
    if dep.has_key(e1_index):
        e1_parents = dep[e1_index]
        for parent in e1_parents:
            if parent[0] == e2_index:
                return parent[1]

    if dep.has_key(e2_index):
        e2_parents = dep[e2_index]
        for parent in e2_parents:
            if parent[0] == e1_index:
                return parent[1]

    return None


def analyze_common_parents(common, e1, e2, pos):
    left = []
    right = []
    middle = []
    for parent in common:
        if e1 < parent and parent < e2:
            middle.append(parent)
        elif e1 < parent and e2 < parent:
            right.append(parent)
        elif e1 > parent and e2 > parent:
            left.append(parent)

def generate_visual_format(sent):
    list = ['<BR>']
    for i in range(1, len(sent)):
        if sent[i].startswith('chemical_'):
            list.append('<font style="background-color: rgb(171,221,164)"> ' + sent[i][9:].replace('_', ' ') + ' </font>')
        elif sent[i].startswith('disease_'):
            list.append('<font style = "background-color: rgb(0,208,255)" > ' + sent[i][8:].replace('_', ' ') + ' </font>')
        elif sent[i].startswith('gene_'):
            list.append('<font style = "background-color: rgb(215,25,28)" > ' + sent[i][5:].replace('_', ' ') + ' </font>')
        elif sent[i].startswith('key_'):
            list.append('<font style = "color:#FF0000" > ' + sent[i][4:].replace('_', ' ') + ' </font>')
        elif sent[i].startswith('subkey_'):
            list.append('<font style = "color:#68228B" > ' + sent[i][7:].replace('_', ' ') + ' </font>')
        else:
            list.append(sent[i])

    return ' '.join(list)


def extract_relations(sent_list, pos_list, dep_list):
    relations = []
    for sent, pos, dep in zip(sent_list, pos_list, dep_list):
        # print sent
        entity_list = findout_two_entitys(sent)
        if len(entity_list) < 2:
            continue
        e1_index = entity_list[0][0]
        e1_type = entity_list[0][1]
        e2_index = entity_list[1][0]
        e2_type = entity_list[1][1]
        direct = direct_interaction(e1_index, e2_index, dep)
        if direct is not None:
            continue
        e1_parent_indexs = set()
        e2_parent_indexs = set()
        get_all_parents(e1_index, dep, e1_parent_indexs, pos)
        get_all_parents(e2_index, dep, e2_parent_indexs, pos)
        common_parents = e1_parent_indexs.intersection(e2_parent_indexs)
        if len(common_parents) > 0:
            middle_common = []
            for parent_index in common_parents:
                if int(e1_index) < int(parent_index) and int(parent_index) < int(e2_index):
                    middle_common.append(parent_index)
            if len(middle_common) > 0:
                count = 0
                # for the main interaction word
                for middle in middle_common:
                    if sent[int(middle)] == 'have' or sent[int(middle)] == 'has' or sent[int(middle)] == 'had':
                        pass
                    elif pos[int(middle)].startswith('V'):
                        sent[int(middle)] = 'key_' + sent[int(middle)]
                        count += 1
                    if count == 3:
                        break
                # for the sub interaction word
                e1_parent = dep[e1_index]
                if e1_parent[0][1] == 'nmod:of' or e1_parent[0][1] == 'nmod:in'\
                    or e1_parent[0][1] == 'nmod:via'or e1_parent[0][1] == 'nmod:with':
                    if e1_parent[0][0] not in middle_common:
                        sent[int(e1_parent[0][0])] = 'subkey_' + sent[int(e1_parent[0][0])]
                e2_parent = dep[e2_index]
                if e2_parent[0][1] == 'nmod:of' or e2_parent[0][1] == 'nmod:in'\
                    or e2_parent[0][1] == 'nmod:via'or e2_parent[0][1] == 'nmod:with':
                    if e2_parent[0][0] not in middle_common:
                        sent[int(e2_parent[0][0])] = 'subkey_' + sent[int(e2_parent[0][0])]
                if count > 0:
                    relations.append(generate_visual_format(sent))

    return relations



if __name__ == '__main__':

    dir = 'C:/Users/ZZH/Desktop/Aim-10/'
    train_instances = []
    for line in open(dir + 'train0.txt'):
        train_instances.append(process_punctuations(change_offset_2_embed(line.strip())).lower())
    FileUtil.writeStrLines(dir + 'train0.token', train_instances)

#     dir_s = '/home/BIO/zhaozhehuan/relations/'
#     dir_up = 'C:/Users/ZZH/Desktop/ouput/'
#     dir_re = 'C:/Users/ZZH/Desktop/relations/'
#     dir_pa = 'C:/Users/ZZH/Desktop/parser/'
#     files = os.listdir(dir_pa)
#     for file in files:
#         print file
#         sent_list, pos_list, dep_list = read_stanford_parser_file(dir_pa + file)
#         relations = extract_relations(sent_list, pos_list, dep_list)
#         before_list = ['<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">',
#                        '<html>',
#                        '<head>',
#                        '<meta charset="UTF-8">',
#                        '<title>uptodate</title>',
#                        '</head>',
#                        '<body style="font-family: Times New Roman;font-size:20px">',
#                        '<font style="background-color: rgb(215,25,28)">Protein</font>&emsp;<font style="background-color: rgb(253,174,97)">DNA</font>&emsp;<font style="background-color: rgb(255,255,191)">RNA</font>&emsp;<font style="background-color: rgb(171,221,164)">Chemical</font>&emsp;<font style="background-color: rgb(0,208,255)">Disease</font>',
#                        '<br><br>',
#                        '<font style = "color:#FF0000" > Relation Word </font>&emsp;<font style = "color:#68228B" > Entity Association Word </font>',
#                        '<br>'
#                         ]
#         after_list = ['<br \>',
#                       '</body>',
#                       '</html>']
#         writeStrLines(dir_re + file.partition('.')[0] + '.htm', before_list + relations + after_list)

#     emb_slim = gen_slim_emb(dir_s + 'pubmed.w100.emb',
#                  dir_s + 'vocab.txt')
#     writeStrLines(dir_s + 'pubmed.w100.emb.slim', emb_slim)

    # files = os.listdir(dir_up)
    # for file in files:
    #     file_short = file.split(' ')[0]
    #     line_index = 0
    #     list = []
    #     for line in open(dir_up + file):
    #         instances = generate_instances_from_luoling_uptodate(line.strip(), file_short + ' ' + str(line_index))
    #         line_index += 1
    #         if instances is not None:
    #             list.extend(instances)
    #
    #     list2 = []
    #     for line in list:
    #         list2.append(change_offset_2_embed_4_parser(line.strip()))
    #
    #     writeStrLines(dir_up + file_short + '.4.parser', list2)

    # luoling_token4(dir_up + 'Contrast.4.parser', dir_up + 'Contrast.token')