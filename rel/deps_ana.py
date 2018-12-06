# -*- coding: utf-8 -*-

import Generate_index
import Generate_entitytype
import output_json
import copy
import HTM_present as htm
import ADE_model as ADE
import GAD_model as GAD
import DDI_model as DDI
import PPI_model as PPI
import FileUtil
import json
from Constants import home_dir

''' the modification dependencies
'''
mod_set = set(['amod', 'advmod', 'compound', 'compound:prt', 'nummod', 'mwe'])

''' The clause dependencies
'''
clause_set = set(['advcl', 'acl', 'csubj', 'ccomp', 'csubjpass', 'acl:relcl', 'parataxis'])

'''
'''
transferable_set = mod_set.union(set(['conj:and', 'conj:or']))

''' this deps are used to find out modification words
'''
supplement_set = set(['amod', 'compound', 'compound:prt', 'nmod:of', 'nmod:with'])

'''
    some deps are filtered.
    like 'det', 'case', etc.
'''
dep_rest = set()
def initial_filtered_deps():
    for line in open(home_dir + 'files/deps.rest'):
        dep_rest.add(line.strip())

def exchange_tokens(token1, token2):
    tempt = token1
    token1 = token2
    token2 = tempt
    return token1, token2

'''
    change the format 
    from
        token1 -> set(token2s)
    to
        token1 -> list(token2s)
'''
def change_dep_fb_format(dep_map_list):
    new_dep_map_list = []
    for dep_map in dep_map_list:
        new_dep_map = {}
        for token1, token2s in dep_map.items():
            token2_list = []
            for token2 in token2s:
                token2_list.append(token2)
            token2_list.sort()
            new_dep_map[token1] = token2_list
        new_dep_map_list.append(new_dep_map)
    return new_dep_map_list

def read_dep_file(filename):
    sent_list = []
    pos_list = []
    dep_list = []
    dep_dir_list = []
    dep_f_list = []
    mod_dep_list = []

    dep_f = {}  # token1 -> set(token2s), which considers no direction
    dep = {}  # (token1, token2) -> dep, which considers no direction
    dep_dir = {}  # (token1, token2) -> dep, which considers the direction
    mod_dep = {}  # token -> list[mod_tokens]
    whitespace_index = 0
    for line in open(filename):
        if line.strip() == '':
            whitespace_index += 1
            continue

        if whitespace_index % 2 == 0:
            # new record
            # record the previous sentence's information
            if whitespace_index != 0:
                dep_list.append(dep)
                dep_dir_list.append(dep_dir)
                dep_f_list.append(dep_f)
                mod_dep_list.append(mod_dep)
            dep = {}
            dep_dir = {}
            dep_f = {}
            mod_dep = {}

            # new sentence's words and POSs
            sent = ['ROOT']
            pos = ['ROOT']
            splited = line.strip().split(' ')
            for elem in splited:
                sent.append(
                    elem.rpartition('/')[0].replace('-LRB-', '(').replace('-RRB-', ')').replace('-LSB-', '[').replace(
                        '-RSB-', ']'))
                pos.append(elem.rpartition('/')[2])
            sent_list.append(sent)
            pos_list.append(pos)
        else:
            # new dep triple
            dep_type = line.partition('(')[0]
            if dep_type in dep_rest \
                    or dep_type.startswith('nmod') \
                    or dep_type.startswith('conj') \
                    or dep_type.startswith('compound'):

                # word1
                token1 = line.replace('-LRB-', '(').replace('-RRB-', ')').replace('-LSB-', '[').replace('-RSB-', ']') \
                    .partition(', ')[0].rpartition('-')[2]

                while token1.endswith("'"):
                    token1 = token1[:-1]
                token1 = int(token1)

                # word2
                token2 = \
                line.strip().replace('-LRB-', '(').replace('-RRB-', ')').replace('-LSB-', '[').replace('-RSB-', ']') \
                    .rpartition('-')[2][:-1]

                while token2.endswith("'"):
                    token2 = token2[:-1]
                token2 = int(token2)

                if token1 == token2:
                    continue

                ''' get the modification deps information with direction
                    where token1 is modified by token2
                '''
                if dep_type in mod_set:
                    if mod_dep.has_key(token1):
                        mod_dep[token1].append(token2)
                    else:
                        mod_dep[token1] = [token2]

                ''' get the dep information with direction
                '''
                if dep_dir.has_key((token1, token2)):
                    ''' Circle will not be found in the normal parsed graph
                        except for the acl:relcl clause
                        Therefore, the acl:relcl dep will be deleted to demage the circle.
                    '''
                    if dep_type == 'acl:relcl':
                        pass
                    elif dep_dir[(token1, token2)] == 'acl:relcl':
                        dep_dir[(token1, token2)] = dep_type
                    elif dep_dir[(token1, token2)] != dep_type:
                        print 'there is a circle !'
                else:
                    dep_dir[(token1, token2)] = dep_type

                ''' considering the linear order where token1 must ahead of token2
                '''
                if token1 > token2:
                    token1, token2 = exchange_tokens(token1, token2)

                ''' get the dep information on the linear order
                '''
                if dep.has_key((token1, token2)):
                    ''' Circle will not be found in the normal parsed graph
                        except for the acl:relcl clause
                        Therefore, the acl:relcl dep will be deleted to demage the circle.
                    '''
                    if dep_type == 'acl:relcl':
                        pass
                    elif dep[(token1, token2)] == 'acl:relcl':
                        dep[(token1, token2)] = dep_type
                    elif dep[(token1, token2)] != dep_type:
                        print 'there is a circle !'
                else:
                    dep[(token1, token2)] = dep_type

                ''' get the map information where the key is token1 
                    and the values are the list of token2s 
                '''
                if dep_f.has_key(token1):
                    dep_f[token1].add(token2)
                else:
                    dep_f[token1] = {token2}

    # the last sentence's dep information
    dep_list.append(dep)
    dep_dir_list.append(dep_dir)
    dep_f_list.append(dep_f)
    mod_dep_list.append(mod_dep)

    return sent_list, pos_list, dep_list, dep_dir_list, \
           change_dep_fb_format(dep_f_list), mod_dep_list

''' Replace acl, advcl and xcomp with acl:mark, advcl:mark and xcomp:mark
    if there is no corresponding mark dep, then the 'none' is used.
    where the mark is commonly be 'that', 'where', etc.
'''
def append_markdep_type(deps, deps_dir, token1, token2, mark='none'):
    deps_dir[(token1, token2)] = deps_dir[(token1, token2)] + ':' + mark
    if deps.has_key((token1, token2)):
        deps[(token1, token2)] = deps[(token1, token2)] + ':' + mark
    elif deps.has_key((token2, token1)):
        deps[(token2, token1)] = deps[(token2, token1)] + ':' + mark

def delete_edge(dep_fs, deps, deps_dir, token1, token2):
    if deps_dir.has_key((token1, token2)):
        deps_dir.pop((token1, token2))

    if token1 > token2:
        tempt = token1
        token1 = token2
        token2 = tempt

    if deps.has_key((token1, token2)):
        deps.pop((token1, token2))

    popkey_list = []
    for key, values in dep_fs.items():
        if key == token1:
            if len(values) == 1:
                popkey_list.append(key)
            else:
                values.remove(token2)
    for popkey in popkey_list:
        dep_fs.pop(popkey)

''' Delete the mark dep after put this mark information
    into corresponding clause deps(acl, advcl and xcomp) with
    'append_markdep_type' function
'''
# 对acl, advcl, xcomp这三种关系进行处理,token1 token2为关系连接的两个词
def deal_dep_with_mark(sent, deps, deps_dir, dep_fs, token1, token2):
    ''' find out corresponding mark dep
    '''
    mark_list = []
    for (t1, t2), value in deps_dir.items():
        if value == 'mark' and t1 == token2:
            mark_list.append((t1, t2))

    if len(mark_list) == 0:
        append_markdep_type(deps, deps_dir, token1, token2)
    elif len(mark_list) == 1:
        mark = sent[mark_list[0][1]]
        append_markdep_type(deps, deps_dir, token1, token2, mark)
    else:
        ''' when more than one mark are found
            we will choose the one nearest the token2
        '''
        distance = 100
        mark = None
        for _, mark_index in mark_list:
            if token2 - mark_index < distance:
                mark = sent[mark_index]
                distance = token2 - mark_index
        if mark is not None:
            append_markdep_type(deps, deps_dir, token1, token2, mark)
        else:
            print 'nao sha lei here'

    ''' Delete the corresponding mark dep
    '''
    for t1, t2 in mark_list:
        delete_edge(dep_fs, deps, deps_dir, t2, t1)

def process_clause_dep(sent, deps, deps_dir, dep_fs):
    for (token1, token2), dep in deps_dir.items():
        '''
            The acl:relcl type is deleted when reading the dep file
            and here the following three deps: acl, advcl and xcomp are consider
            as all these deps associate with mark dep type. 
        '''
        # deal the deps acl.advcl,xcomp,replace them with 'dep:mark', then delete the mark dep
        if dep == 'acl' or dep == 'advcl' or dep == 'xcomp':
            deal_dep_with_mark(sent, deps, deps_dir, dep_fs, token1, token2)

''' find out corresponding index in current sent
    for two entities as that one token may be
    splited after parsing
'''
def find_entity_index(inst, sent):
    if inst == (25, 36, 'B-cell_lymphoma', 'razoxane'):
        print 'hehe'

    distance = inst[1] - inst[0]
    index1, index2 = -1, -1
    # before and after two words not after three words
    for i in range(10):
        left_offset = inst[0] - i
        if left_offset >= 0 and sent[left_offset] == inst[2]:
            index1 = left_offset
            break

        right_offset = inst[0] + i
        if right_offset < len(sent) and sent[right_offset] == inst[2]:
            index1 = right_offset
            break

    for i in range(10):
        left_offset = index1 + distance - i
        if left_offset >= 0 and left_offset < len(sent) and sent[left_offset] == inst[3].strip():
            index2 = left_offset
            break

        right_offset = index1 + distance + i
        if right_offset < len(sent) and sent[right_offset] == inst[3].strip():
            index2 = right_offset
            break

    return index1, index2

def generate_graph(dep_fs, deps):
    dep_set = set()
    for key, value in deps.items():
        dep_set.add(key)

    graph = {}
    for key, values in dep_fs.items():
        for value in values:
            if (key, value) in dep_set:
                if graph.has_key(key):
                    graph[key].append(value)
                else:
                    graph[key] = [value]

                if graph.has_key(value):
                    graph[value].append(key)
                else:
                    graph[value] = [key]
            elif (value, key) in dep_set:
                print 'hhhh'
    return graph

'''detect if there exist direct connection between
   entity and entity with conj:and dep type
   this dep will be filtered
'''
def detect_direct_and_edge(graph, index1, index2, deps_dir):
    has_and_dep = False
    if deps_dir.has_key((index1, index2)) and deps_dir[(index1, index2)] == 'conj:and':
        has_and_dep = True
    elif deps_dir.has_key((index2, index1)) and deps_dir[(index2, index1)] == 'conj:and':
        has_and_dep = True

    if has_and_dep:
        if len(graph[index1]) > 1:
            graph[index1].remove(index2)
        elif len(graph[index1]) == 1:
            print 'hhhhhhhhhhh'

        if len(graph[index2]) > 1:
            graph[index2].remove(index1)
        elif len(graph[index2]) == 1:
            print 'hhhhhghhhhh'

# get the shortest path between start and end(two entities)
def shortestPath(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if not graph.has_key(start):
        return None
    shortest = None
    for node in graph[start]:
        if node not in path:
            newpath = shortestPath(graph, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest

# e1, e2, e1_ext, e2_ext, rest_ext, path, graph = analyze_inst_by_parser(inst, sent, dep_fs, deps, deps_dir, mod_dep)
def analyze_inst_by_parser(inst, sent, dep_fs, deps, deps_dir, mod_dep, count):
    index1, index2 = find_entity_index(inst, sent)
    if index1 == -1 or index2 == -1:
        print 'missed entities ----> ', count
        return None, None, None, None, None, None, None

    graph = generate_graph(dep_fs, deps)

    # delete the and dep between two entities
    detect_direct_and_edge(graph, index1, index2, deps_dir)

    path = shortestPath(graph, index1, index2, [])

    if path is None:
        print 'find no path'
        return None, None, None, None, None, None, None

    ''' find out first entity's connected tokens
        except the one on the shortest path
    '''
    e1_ext = []
    for index in graph[index1]:
        if index != path[1] and abs(index - index1) < 10:
            # the extended edge is not the clasue type
            if (deps_dir.has_key((index1, index)) and deps_dir[(index1, index)] not in clause_set) \
                    or (deps_dir.has_key((index, index1)) and deps_dir[(index, index1)] not in clause_set):
                e1_ext.append(index)

    ''' find out second entity's connected tokens
        except the ones on the shortest path
    '''
    e2_ext = []
    for index in graph[index2]:
        if index != path[-2] and abs(index - index2) < 10:
            # the extended edge is not the clasue type
            if (deps_dir.has_key((index2, index)) and deps_dir[(index2, index)] not in clause_set) \
                    or (deps_dir.has_key((index, index2)) and deps_dir[(index, index2)] not in clause_set):
                e2_ext.append(index)

    ''' find out the tokens' connected tokens
        except the ones on the shortest path
    '''
    rest_ext = []
    for i in range(1, len(path) - 1):
        for index in graph[path[i]]:
            if index != path[i - 1] and index != path[i + 1] and abs(index - path[i]) < 10:
                # the extended edge is not the clasue type
                if (deps_dir.has_key((path[i], index)) and deps_dir[(path[i], index)] not in clause_set) \
                        or (deps_dir.has_key((index, path[i])) and deps_dir[(index, path[i])] not in clause_set):
                    rest_ext.append(index)

    return index1, index2, e1_ext, e2_ext, rest_ext, path, graph

'''
    Get the dep sequence on the shortest path
'''
def get_path_deps(path, sent, deps_dir):
    path_deps = []
    for i in range(len(path) - 1):
        if deps_dir.has_key((path[i], path[i + 1])):
            path_deps.append(deps_dir[(path[i], path[i + 1])])
        elif deps_dir.has_key((path[i + 1], path[i])):
            path_deps.append(deps_dir[(path[i + 1], path[i])])
        else:
            print 'gan sha lei'
    return path_deps

def deps_main():
    ''' processing start...
    '''
    # get the index from corpus
    #Generate_index.generate_indexFile()

    dir = '../files/'
    initial_filtered_deps()

    sent_list, pos_list, dep_list, dep_dir_list, dep_f_list, mod_dep_list = read_dep_file(dir + 'liver.true.sent.par')

    inst_list = [(int(line.split(' ')[1]), int(line.split(' ')[2]), line.split(' ')[3], \
        line.strip().split(' ')[4]) for line in open(dir + 'liver.true.indexs')]
    

    # to be continued ...
    # inst_list = []
    # entity_type = []
    # for inst_elem in list_indexs:
    #     inst_list.append((int(line.split(' ')[1]), int(line.split(' ')[2]), line.split(' ')[3], line.strip().split(' ')[4]))
    #     entity_type.append(inst_elem.split(' ', 5)[5].replace(' ', '-').strip())

    # index_set = set()
    # for i in open(dir + 'train0.t'):
    #     index_set.add(int(i))

    tongji = 0
    count = 0
    miss_count = 0
    no_path = 0
    sumnum = 0
    fail = 0
    notinDic = 0
    notmatch = 0
    pattern_match = 0
    htm_present = ['<htm>\n', '<body>\n', '<BR>',
                   '<font style = "color:red" > Key Words </font>'
                   + '&emsp;<font style = "color:blue" > Modification Words </font>'
                   + '&emsp;<font style = "color:green" > Entity </font>',
                   '<br><BR>']
    
    # get the entity type
    entity_type = []
    entity_type = Generate_entitytype.getTypes(dir + 'liver.true.txt')
    entity_type_index = 0

    # JSON parameter
    nodes_list = []
    edge_list = []
    json_data = {}

    for inst, sent, deps, deps_dir, dep_fs, mod_dep in zip(inst_list, sent_list, dep_list, dep_dir_list, dep_f_list, mod_dep_list):
        
        # replace the ROOT by index which started 0
        sent[0] = str(count)
        if len(sent) > 3:
        #if len(sent) > 3 and count in index_set:

            process_clause_dep(sent, deps, deps_dir, dep_fs)

            # e1,e2为实体索引；ext为与实体连接的关系，不包括最短路径上的关系；rest为路径上其他词涉及的关系，不包括实体
            e1, e2, e1_ext, e2_ext, rest_ext, path, graph = analyze_inst_by_parser(inst, sent, dep_fs, deps, deps_dir, mod_dep, count)

            # if e1 is None:
            #     print count, 'missed the entities'
            #     continue
            
            if path is not None:
                # collect the deps on the path
                path_deps = get_path_deps(path, sent, deps_dir)

                # key = []
                # pattern, mod1, key, mod2, e1_mods, e2_mods = DDI.pattern_key_word(deps_dir, path_deps, path, graph, dep_fs, deps)

                # test......
                # if pattern == 'pattern6':
                #     print '11111111111111111111111111111111111111111111111111'
                #     print 'path:      ', path
                #     print 'path_deps: ', path_deps
                #     print 'key:       ', key
                #     print 'word:      ', sent[key[0]]
                #     print 'deps:      ', deps
                #     print sent
                #     print '11111111111111111111111111111111111111111111111111'
                #     # ADE.processing_ADE(pattern, mod1, key, mod2, e1_mods, e2_mods, htm_present, e1, e2, e1_ext, e2_ext, rest_ext, path, graph, \
                #     #     inst, sent, deps, deps_dir, dep_fs, mod_dep)
                #     mod1s, mod2s, sub_key = htm.supplement(sent, e1, e2, graph, deps_dir, mod1, key[0], mod2)
                #     htm_present.append(htm.htm_represent(sent, e1, e2, mod1s, mod2s, key, sub_key))

                # ADE.processing_ADE(pattern, mod1, key, mod2, e1_mods, e2_mods, htm_present, e1, e2, e1_ext, e2_ext, rest_ext, path, graph, \
                #     inst, sent, deps, deps_dir, dep_fs, mod_dep)

                types = entity_type[entity_type_index]
                key = []

                if (types=='gene-disease') or (types=='disease-gene') or (types=='gene-gene') or (types=='phenotype-gene'):
                    pattern, mod1, key, mod2, e1_mods, e2_mods = GAD.pattern_key_word(deps_dir, path_deps, path, graph, dep_fs, deps)
                    if pattern != 'missed':
                        pattern_match += 1
                        print 'GAD: ', count, pattern
                    key = GAD.processing_GAD(pattern, mod1, key, mod2, e1_mods, e2_mods, htm_present, e1, e2, e1_ext, e2_ext, rest_ext, path, graph, \
                        inst, sent, deps, deps_dir, dep_fs, mod_dep)
                elif (types=='chemical-disease') or (types=='disease-chemical') or (types=='disease-phenotype') or (types=='gene-chemical') or (types=='chemical-gene'):
                    pattern, mod1, key, mod2, e1_mods, e2_mods = ADE.pattern_key_word(deps_dir, path_deps, path, graph, dep_fs, deps)
                    if pattern != 'missed':
                        pattern_match += 1
                        print 'ADE: ', count, pattern
                    key = ADE.processing_ADE(pattern, mod1, key, mod2, e1_mods, e2_mods, htm_present, e1, e2, e1_ext, e2_ext, rest_ext, path, graph, \
                        inst, sent, deps, deps_dir, dep_fs, mod_dep, count)
                elif types=='chemical-chemical':
                    tongji += 1
                    pattern, mod1, key, mod2, e1_mods, e2_mods = DDI.pattern_key_word(deps_dir, path_deps, path, graph, dep_fs, deps)
                    if pattern != 'missed':
                        pattern_match += 1
                        print 'DDI: ', count, pattern
                    key = DDI.processing_DDI(pattern, mod1, key, mod2, e1_mods, e2_mods, htm_present, e1, e2, e1_ext, e2_ext, rest_ext, path, graph, \
                        inst, sent, deps, deps_dir, dep_fs, mod_dep)
                else:
                    pattern, mod1, key, mod2, e1_mods, e2_mods = PPI.pattern_key_word(deps_dir, path_deps, path, graph, dep_fs, deps)
                    if pattern != 'missed':
                        pattern_match += 1
                        print 'PPI: ', count, pattern
                    key =PPI.processing_PPI(pattern, mod1, key, mod2, e1_mods, e2_mods, htm_present, e1, e2, e1_ext, e2_ext, rest_ext, path, graph, \
                        inst, sent, deps, deps_dir, dep_fs, mod_dep)
                if len(key) != 0:
                    output_json.gen_jsonData(inst, types, sent, key, nodes_list, edge_list)
            else:
                print 'fucking O-> fucking O-> coming O---> ', count
        count += 1
        entity_type_index += 1
    htm_present.extend(['<BR><BR>', '</body>\n', '</htm>\n'])
    json_data = output_json.generate_JSONfile(nodes_list, edge_list)
    #json_str = json.dumps(json_data)
    output_json.writeJson('../files/HTML/liver_data.json', json_data)
    print 'pattern_match: ', pattern_match
    print 'DDI tongji: ', tongji
    print nodes_list[0]
    print edge_list[0]
    print len(nodes_list)
    print len(edge_list)
    FileUtil.writeStrLines('../files/HTML/liver.htm', htm_present)