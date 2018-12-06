# -*- coding: utf-8 -*-
import HTM_present as htm
from Constants import home_dir

mod_set = set(['amod', 'advmod', 'compound', 'compound:prt', 'nummod', 'mwe'])

clause_set = set(['advcl', 'acl', 'csubj', 'ccomp', 'csubjpass', 'acl:relcl', 'parataxis'])

transferable_set = mod_set.union(set(['conj:and', 'conj:or']))

supplement_set = set(['amod', 'compound', 'compound:prt', 'nmod:of', 'nmod:with'])

''' A-appos-Key-nmod:x-B
'''
def key_word_pattern1(path, path_deps, dep_fs, deps):
    key = []
    if len(path_deps) == 2:
        if path_deps[0] == 'appos' and path_deps[1].startswith('nmod') and path[0] < path[1]:
            key.append(path[1])
    if len(key) == 1:
        tags = []
        for keys, values in dep_fs.items():
            for value in values:
                if value == key[0]:
                    tags.append((keys, value))
                elif keys == key[0]:
                    tags.append((keys, value))
                else:
                    continue
        for tag in tags:
            if deps.has_key((tag[0], tag[1])) and (deps[(tag[0], tag[1])] == 'compound' or deps[(tag[0], tag[1])] == 'amod'):
                if abs(tag[0] - tag[1]) == 1:
                    if tag[0] == path[1]:
                        key = [tag[0], tag[1]]
                    else:
                        key = [tag[1], tag[0]]
            elif deps.has_key((tag[1], tag[0])) and (deps[(tag[1], tag[0])] == 'compound' or deps[(tag[1], tag[0])] == 'amod'):
                if abs(tag[0] - tag[1]) == 1:
                    if tag[0] == path[1]:
                        key = [tag[0], tag[1]]
                    else:
                        key = [tag[1], tag[0]]

    return None, key, None

''' A-nmod:of-Key-dobj-X-nmod:x-B
'''
def key_word_pattern2(path, path_deps, graph, dep_fs, deps, deps_dir):
    key = []
    mod1 = None
    mod2 = None
    if len(path_deps) == 3:
        if path_deps[0] == 'nmod:of' \
                and path_deps[1] == 'dobj' \
                and path_deps[2].startswith('nmod'):
            key.append(path[1])
    elif len(path_deps) == 4:
        if path_deps[0] == 'nmod:of' \
                and path_deps[1] == 'dobj' \
                and path_deps[2].startswith('nmod:') \
                and path_deps[3] == 'nmod:of':
            mod2 = path[3]
            key.append(path[1])
    if len(key) == 1:
        tags = []
        for keys, value in deps.items():
            if keys[0] == path[2]:
                tags.append((keys[0], keys[1]))
            else:
                continue
        dep_list = ['nmod:after', 'nmod:during', 'nmod:by', 'nmod:with', 'nmod:to', 'nmod:following', 'nmod:as', 'nmod:in', 'nmod:at']
        for tag in tags:
            if deps[(tag[0], tag[1])] in dep_list:
                #if (abs(int(tag[0])-int(tag[1])) < abs(int(path[0])-int(path[-1]))) and (abs(int(tag[1])-int(path[-1])) < 5):
                key = []
                key.append(0)
            else:
                continue
    return mod1, key, mod2

''' A-nsubj-Key-dobj-B
'''
def key_word_pattern3(path, path_deps, dep_fs, deps):
    key = []
    flag_path = 0
    mod1 = None
    mod2 = None
    if len(path_deps) == 2:
        if (path_deps[0] == 'nsubj' or path_deps[0] == 'nsubjpass') \
                and path_deps[1] == 'dobj':
            key.append(path[1])
            flag_path = 1
    elif len(path_deps) == 3:
        if path_deps[0] == 'nmod:of' and \
                (path_deps[1] == 'nsubj' or path_deps[1] == 'nsubjpass') \
                and path_deps[2] == 'dobj':
            mod1 = path[1]
            key.append(path[2])
            flag_path = 2
        elif (path_deps[0] == 'nsubj' or path_deps[0] == 'nsubjpass') \
                and path_deps[1] == 'dobj' \
                and path_deps[2] == 'nmod:of':
            key.append(path[1])
            flag_path = 1
            mod2 = path[2]
    elif len(path_deps) == 4:
        if path_deps[0] == 'nmod:of' and \
                (path_deps[1] == 'nsubj' or path_deps[1] == 'nsubjpass') \
                and path_deps[2] == 'dobj' \
                and path_deps[3] == 'nmod:of':
            mod1 = path[1]
            key.append(path[2])
            flag_path = 2
            mod2 = path[3]
    if len(key) == 1:
        tags = []
        for keys, values in dep_fs.items():
            for value in values:
                if value == key[0]:
                    tags.append((keys, value))
                elif keys == key[0]:
                    tags.append((keys, value))
                else:
                    continue
        for tag in tags:
            if deps.has_key((tag[0], tag[1])) and (deps[(tag[0], tag[1])] == 'compound' or \
                deps[(tag[0], tag[1])] == 'amod' or deps[(tag[0], tag[1])] == 'advmod'):
                if abs(int(tag[0]) - int(tag[1])) == 1:
                    if flag_path == 1:
                        if tag[0] == path[1]:
                            key = [tag[0], tag[1]]
                        else:
                            key = [tag[1], tag[0]]
                    elif flag_path == 2:
                        if tag[0] == path[2]:
                            key = [tag[0], tag[1]]
                        else:
                            key = [tag[1], tag[0]]
            elif deps.has_key((tag[1], tag[0])) and (deps[(tag[1], tag[0])] == 'compound' or \
                deps[(tag[1], tag[0])] == 'amod' or deps[(tag[1], tag[0])] == 'advmod'):
                if abs(int(tag[0]) - int(tag[1])) == 1:
                    if flag_path == 1:
                        if tag[0] == path[1]:
                            key = [tag[0], tag[1]]
                        else:
                            key = [tag[1], tag[0]]
                    elif flag_path == 2:
                        if tag[0] == path[2]:
                            key = [tag[0], tag[1]]
                        else:
                            key = [tag[1], tag[0]]
    return mod1, key, mod2

'''A-nsubj-X-dobj-Key-nmod:x-B
'''
def key_word_pattern4(path, path_deps, dep_fs, deps):
    key = []
    mod1 = None
    mod2 = None
    flag_path = 0
    if len(path_deps) == 3:
        if (path_deps[0] == 'nsubj' or path_deps[0] == 'nsubjpass') \
                and path_deps[1] == 'dobj' and path_deps[2].startswith('nmod:'):
            key.append(path[2])
            flag_path = 1
    elif len(path_deps) == 4:
        if path_deps[0] == 'nmod:of' and \
                (path_deps[1] == 'nsubj' or path_deps[1] == 'nsubjpass') \
                and path_deps[2] == 'dobj' and path_deps[3].startswith('nmod:'):
            mod1 = path[1]
            key.append(path[3])
            flag_path = 2
        elif (path_deps[0] == 'nsubj' or path_deps[0] == 'nsubjpass') \
                and path_deps[1] == 'dobj' and path_deps[2].startswith('nmod:') \
                and path_deps[3] == 'nmod:of':
            key.append(path[2])
            flag_path = 1
            mod2 = path[3]
    elif len(path_deps) == 5:
        if path_deps[0] == 'nmod:of' and \
                (path_deps[1] == 'nsubj' or path_deps[1] == 'nsubjpass') \
                and path_deps[2] == 'dobj' and path_deps[3].startswith('nmod:') \
                and path_deps[4] == 'nmod:of':
            mod1 = path[1]
            key.append(path[3])
            flag_path = 2
            mod2 = path[4]
    if len(key) == 1:
        tags = []
        for keys, values in dep_fs.items():
            for value in values:
                if value == key[0]:
                    tags.append((keys, value))
                elif keys == key[0]:
                    tags.append((keys, value))
                else:
                    continue
        for tag in tags:
            if deps.has_key((tag[0], tag[1])) and (deps[(tag[0], tag[1])] == 'nmod:of' or \
                deps[(tag[0], tag[1])] == 'nmod:following'):
                tags2 = []
                for keys, values in dep_fs.items():
                    for value in values:
                        if value == path[0]:
                            tags2.append((keys, value))
                        elif keys == path[0]:
                            tags2.append((value, keys))
                        else:
                            continue
                for tag2 in tags2:
                    if deps.has_key((tag2[0], tag2[1])) and deps[(tag2[0], tag2[1])] == 'nmod:of':
                        key = [tag2[0]]
                        mod1 = None
                        break
            elif deps.has_key((tag[0], tag[1])) and (deps[(tag[0], tag[1])] == 'compound' or \
                deps[(tag[0], tag[1])] == 'amod' or deps[(tag[0], tag[1])] == 'advmod'):
                if abs(int(tag[0]) - int(tag[1])) == 1:
                    if flag_path == 1:
                        if tag[0] == path[2]:
                            key = [tag[0], tag[1]]
                        else:
                            key = [tag[1], tag[0]]
                    elif flag_path == 2:
                        if tag[0] == path[3]:
                            key = [tag[0], tag[1]]
                        else:
                            key = [tag[1], tag[0]]
            elif deps.has_key((tag[1], tag[0])) and (deps[(tag[1], tag[0])] == 'compound' or \
                deps[(tag[1], tag[0])] == 'amod' or deps[(tag[1], tag[0])] == 'advmod'):
                if abs(int(tag[0]) - int(tag[1])) == 1:
                    if flag_path == 1:
                        if tag[0] == path[2]:
                            key = [tag[0], tag[1]]
                        else:
                            key = [tag[1], tag[0]]
                    elif flag_path == 2:
                        if tag[0] == path[3]:
                            key = [tag[0], tag[1]]
                        else:
                            key = [tag[1], tag[0]]
            else:
                pass

    return mod1, key, mod2

''' A-nmod:x-Key-nmod:x-B
'''
def key_word_pattern5(path, path_deps, dep_fs, deps):
    key = []
    mod1 = None
    mod2 = None
    if len(path_deps) == 2:
        if path_deps[0].startswith('nmod') and path_deps[1].startswith('nmod'):
            key.append(path[1])
    elif len(path_deps) == 3:
        if path_deps[0] == 'nmod:of' and path_deps[1].startswith('nmod') \
                and path_deps[2].startswith('nmod'):
            mod1 = path[1]
            key.append(path[2])
        elif path_deps[0].startswith('nmod') and path_deps[1].startswith('nmod') \
                and path_deps[2] == 'nmod:of':
            key.append(path[1])
            mod2 = path[2]
    elif len(path_deps) == 4:
        if path_deps[0] == 'nmod:of' and path_deps[1].startswith('nmod') \
                and path_deps[2].startswith('nmod') and path_deps[3] == 'nmod:of':
            mod1 = path[1]
            key.append(path[2])
            mod2 = path[3]
    if len(key) == 1:
        tags = []
        for keys, values in dep_fs.items():
            for value in values:
                if value == key[0]:
                    tags.append((keys, value))
                elif keys == key[0]:
                    tags.append((value, keys))
                else:
                    continue
        dep_list = ['nmod:following', 'nmod:during', 'nmod:by', 'nmod:in', 'nmod:after', 'nmod:with']
        for tag in tags:
            if deps.has_key((tag[0], tag[1])) and (deps[(tag[0], tag[1])] in dep_list):
                key = []
                key.append(0)
                break
            else:
                continue
    return mod1, key, mod2

'''A-acl-Key-nmod:x-B
'''
def key_word_pattern6(path, path_deps, dep_fs, deps):
    key = []
    flag_path = 0
    mod1 = None
    mod2 = None
    if len(path_deps) == 2:
        if path_deps[0].startswith('acl') and path_deps[1].startswith('nmod:'):
            key.append(path[1])
            flag_path = 1
    elif len(path_deps) == 3:
        if path_deps[0] == 'nmod:of' and \
                path_deps[1].startswith('acl') and path_deps[2].startswith('nmod:'):
            mod1 = path[1]
            key.append(path[2])
            flag_path = 2
        elif path_deps[0].startswith('acl') and path_deps[1].startswith('nmod:') \
                and path_deps[2] == 'nmod:of':
            key.append(path[1])
            flag_path = 1
            mod2 = path[2]
    elif len(path_deps) == 4:
        if path_deps[0] == 'nmod:of' and \
                path_deps[1].startswith('acl') and path_deps[2].startswith('nmod:') \
                and path_deps[3] == 'nmod:of':
            mod1 = path[1]
            key.append(path[2])
            flag_path = 2
            mod2 = path[3]
    if len(key) == 1:
        tags = []
        for keys, values in dep_fs.items():
            for value in values:
                if value == key[0]:
                    tags.append((keys, value))
                elif keys == key[0]:
                    tags.append((keys, value))
                else:
                    continue
        for tag in tags:
            if deps.has_key((tag[0], tag[1])) and (deps[(tag[0], tag[1])] == 'compound' or \
                deps[(tag[0], tag[1])] == 'amod' or deps[(tag[0], tag[1])] == 'advmod'):
                if abs(int(tag[0]) - int(tag[1])) == 1:
                    if flag_path == 1:
                        if tag[0] == path[1]:
                            key = [tag[0], tag[1]]
                        else:
                            key = [tag[1], tag[0]]
                    elif flag_path == 2:
                        if tag[0] == path[2]:
                            key = [tag[0], tag[1]]
                        else:
                            key = [tag[1], tag[0]]
            elif deps.has_key((tag[1], tag[0])) and (deps[(tag[1], tag[0])] == 'compound' or \
                deps[(tag[1], tag[0])] == 'amod' or deps[(tag[1], tag[0])] == 'advmod'):
                if abs(int(tag[0]) - int(tag[1])) == 1:
                    if flag_path == 1:
                        if tag[0] == path[1]:
                            key = [tag[0], tag[1]]
                        else:
                            key = [tag[1], tag[0]]
                    elif flag_path == 2:
                        if tag[0] == path[2]:
                            key = [tag[0], tag[1]]
                        else:
                            key = [tag[1], tag[0]]

    return mod1, key, mod2

def has_ext_edge(graph, deps_dir, start_token, edge_type):
    for end_token in graph[start_token]:
        if deps_dir.has_key((start_token, end_token)) \
                and deps_dir[(start_token, end_token)] == edge_type:
            return end_token
        elif deps_dir.has_key((end_token, start_token)) \
                and deps_dir[(end_token, start_token)] == edge_type:
            return end_token
    return -1

''' A-nsubj-Key-nmod:x{1,n}-B

    including following exception
    A-nsubj-X-nmod:x-B
             -dobj-Key
'''
def key_word_pattern7(path, path_deps, graph, deps_dir, dep_fs, deps):
    key = []
    mod1 = None
    mod2 = None
    if len(path_deps) == 2:
        if (path_deps[0] == 'nsubj' or path_deps[0] == 'nsubjpass') \
                and path_deps[1].startswith('nmod'):
            ext_token = has_ext_edge(graph, deps_dir, path[1], 'dobj')
            if ext_token != -1:
                if (int(ext_token) > int(path[0])) and (int(ext_token) < int(path[-1])):
                    key.append(ext_token)
                else:
                    key.append(path[1])
            else:
                key.append(path[1])
    elif len(path_deps) == 3:
        if path_deps[0] == 'nmod:of' and \
                (path_deps[1] == 'nsubj' or path_deps[1] == 'nsubjpass') \
                and path_deps[2].startswith('nmod'):
            mod1 = path[1]
            ext_token = has_ext_edge(graph, deps_dir, path[2], 'dobj')
            if ext_token != -1:
                if (int(ext_token) > int(path[0])) and (int(ext_token) < int(path[-1])):
                    key.append(ext_token)
                else:
                    key.append(path[2])
            else:
                key.append(path[2])
        elif (path_deps[0] == 'nsubj' or path_deps[0] == 'nsubjpass') \
                and path_deps[1].startswith('nmod') \
                and path_deps[2] == 'nmod:of':
            ext_token = has_ext_edge(graph, deps_dir, path[1], 'dobj')
            if ext_token != -1:
                if (int(ext_token) > int(path[0])) and (int(ext_token) < int(path[-1])):
                    key.append(ext_token)
                else:
                    key.append(path[1])
            else:
                key.append(path[1])
            mod2 = path[2]
    elif len(path_deps) == 4:
        if path_deps[0] == 'nmod:of' and \
                (path_deps[1] == 'nsubj' or path_deps[1] == 'nsubjpass') \
                and path_deps[2].startswith('nmod') \
                and path_deps[3] == 'nmod:of':
            mod1 = path[1]
            ext_token = has_ext_edge(graph, deps_dir, path[2], 'dobj')
            if ext_token != -1:
                if (int(ext_token) > int(path[0])) and (int(ext_token) < int(path[-1])):
                    key.append(ext_token)
                else:
                    key.append(path[2])
            else:
                key.append(path[2])
            mod2 = path[3]
    elif len(path_deps) > 4:
        begin = 0
        end = len(path_deps) - 1
        if path_deps[0] == 'nmod:of':
            mod1 = path[1]
            begin += 1
        if path_deps[-1] == 'nmod:of':
            mod2 = path[-2]
            end -= 1

        if (path_deps[begin] == 'nsubj') or (path_deps[begin] == 'nsubjpass'):
            begin += 1
            while (path_deps[begin].startswith('nmod:') and begin < end):
                begin += 1
            if begin == end:
                key.append(path[2])
    return mod1, key, mod2

'''
    Match the dependency patterns on the shortest path
'''
# pattern, mod1, key, mod2, e1_mods, e2_mods = pattern_key_word(deps_dir, path_deps, path, graph)
def pattern_key_word(deps_dir, path_deps, path, graph, dep_fs, deps):
    e1_mods = []
    e2_mods = []
    key = []

    begin = 0
    end = len(path_deps) - 1
    left_margin = 0
    right_margin = len(path_deps) - 1

    # find the word that has deps such as 'and','or' with entity on the path
    while begin <= right_margin and path_deps[begin] in transferable_set:
        e1_mods.append(path[begin + 1])
        begin += 1
    while end >= left_margin and path_deps[end] in transferable_set:
        e2_mods.append(path[end])
        end -= 1

    if begin > end:
        # the two entities are in the
        # same modification cluster
        return 'missed', None, key, None, e1_mods, e2_mods

    path_deps = path_deps[begin:end + 1]
    path = path[begin:end + 2]

    # pattern 1
    mod1, key, mod2 = key_word_pattern1(path, path_deps, dep_fs, deps)
    if len(key) != 0:
        return 'pattern1', mod1, key, mod2, e1_mods, e2_mods

    begin = 0
    end = len(path_deps) - 1
    left_margin = 0
    right_margin = len(path_deps) - 1

    while begin <= right_margin and path_deps[begin] == 'appos':
        e1_mods.append(path[begin + 1])
        begin += 1
    while end >= left_margin and path_deps[end] == 'appos':
        e2_mods.append(path[end])
        end -= 1

    path_deps = path_deps[begin:end + 1]
    path = path[begin:end + 2]

    mod1, key, mod2 = key_word_pattern2(path, path_deps, graph, dep_fs, deps, deps_dir)
    if len(key) != 0:
        return 'pattern2', mod1, key, mod2, e1_mods, e2_mods

    mod1, key, mod2 = key_word_pattern3(path, path_deps, dep_fs, deps)
    if len(key) != 0:
        return 'pattern3', mod1, key, mod2, e1_mods, e2_mods

    mod1, key, mod2 = key_word_pattern4(path, path_deps, dep_fs, deps)
    if len(key) != 0:
        return 'pattern4', mod1, key, mod2, e1_mods, e2_mods
    mod1, key, mod2 = key_word_pattern5(path, path_deps, dep_fs, deps)
    if len(key) != 0:
        return 'pattern5', mod1, key, mod2, e1_mods, e2_mods

    mod1, key, mod2 = key_word_pattern6(path, path_deps, dep_fs, deps)
    if len(key) != 0:
        return 'pattern6', mod1, key, mod2, e1_mods, e2_mods

    mod1, key, mod2 = key_word_pattern7(path, path_deps, graph, deps_dir, dep_fs, deps)
    if len(key) != 0:
        return 'pattern7', mod1, key, mod2, e1_mods, e2_mods

    return 'missed', None, key, None, e1_mods, e2_mods

def select_most_possible_key(potential_key, e1, e2):
    if len(potential_key) == 2 and potential_key[0] == potential_key[1]:
        return potential_key[0]

    # we find the words between two entities are
    # more possiblely be the key words
    between = []
    for key in potential_key:
        if key > e1 and key < e2:
            between.append(key)

    if len(between) == 0:
        # when all the potential key words are not between
        # we choose the nearest one to both entities
        nearest = potential_key[0]
        for key in potential_key[1:]:
            if abs(key - e1) + abs(key - e2) < abs(nearest - e1) + abs(nearest - e2):
                nearest = key
        return nearest
    elif len(between) == 1:
        return between[0]
    else:
        # we choose the key nearest to entity 2
        nearest_e2 = 0
        for key in between:
            if abs(key - e2) < abs(nearest_e2 - e2):
                nearest_e2 = key
        return nearest_e2

def dic_key_word(e1, e2, path, sent, GAD_keywords, common_words):
    potential_GAD_key = []
    for index in path:
        if sent[index].lower() in GAD_keywords:
            potential_GAD_key.append(index)

    if len(potential_GAD_key) == 1:
        return potential_GAD_key[0]
    elif len(potential_GAD_key) > 1:
        return select_most_possible_key(potential_GAD_key, e1, e2)

    potential_key = []
    for index in path:
        if sent[index].lower() in common_words:
            potential_key.append(index)

    if len(potential_key) == 1:
        return potential_key[0]
    elif len(potential_key) > 1:
        return select_most_possible_key(potential_key, e1, e2)

    return None

def processing_ADE(pattern, mod1, key, mod2, e1_mods, e2_mods, htm_present, e1, e2, e1_ext, e2_ext, rest_ext, path, graph, \
    inst, sent, deps, deps_dir, dep_fs, mod_dep, count):
    if len(key) != 0:
        mod1s, mod2s, sub_key = htm.supplement(sent, e1, e2, graph, deps_dir, mod1, key[0], mod2)
        htm_present.append(htm.htm_represent(sent, e1, e2, mod1s, mod2s, key, sub_key))
        return key
    else:
        '''not match any pattern
        '''
        # read the dictionary
        dir = home_dir + 'files/'
        ADE_keywords = set()
        for line in open(dir + 'ADE.words'):
            ADE_keywords.add(line.strip())
        common_words = set()
        for line in open(dir + 'common.words'):
            common_words.add(line.strip())
        dic_key = dic_key_word(e1, e2, path, sent, ADE_keywords, common_words)

        if dic_key is not None:
            mod1s, mod2s, sub_key = htm.supplement(sent, e1, e2, graph, deps_dir, None, dic_key, None)
            htm_present.append(htm.htm_represent(sent, e1, e2, mod1s, mod2s, dic_key, sub_key))
            key = []
            key.append(dic_key)
            return key
        else:
            dic_key = dic_key_word(e1, e2, e1_mods + e2_mods, sent, ADE_keywords, common_words)
            if dic_key is not None:
                mod1s, mod2s, sub_key = htm.supplement(sent, e1, e2, graph, deps_dir, None, dic_key, None)
                htm_present.append(htm.htm_represent(sent, e1, e2, mod1s, mod2s, dic_key, sub_key))
                key = []
                key.append(dic_key)
                return key
            else:
                dic_key = dic_key_word(e1, e2, e1_ext + e2_ext + rest_ext, sent, ADE_keywords, common_words)
                
                if dic_key is not None:
                    mod1s, mod2s, sub_key = htm.supplement(sent, e1, e2, graph, deps_dir, None, dic_key, None)
                    htm_present.append(htm.htm_represent(sent, e1, e2, mod1s, mod2s, dic_key, sub_key))
                    key = []
                    key.append(dic_key)
                    return key
                else:
                    key = []
                    return key

def processing_ADE_2(pattern, mod1, key, mod2, e1_mods, e2_mods, htm_present, e1, e2, e1_ext, e2_ext, rest_ext, path, graph, \
    inst, sent, deps, deps_dir, dep_fs, mod_dep, count):
    if len(key) != 0:
        mod1s, mod2s, sub_key = htm.supplement(sent, e1, e2, graph, deps_dir, mod1, key[0], mod2)
        htm_present.append(htm.htm_represent(sent, e1, e2, mod1s, mod2s, key, sub_key))
        return key
    else:
        '''not match any pattern
        '''
        # read the dictionary
        dir = home_dir + 'files/'
        ADE_keywords = set()
        for line in open(dir + 'ADE.words'):
            ADE_keywords.add(line.strip())
        common_words = set()
        for line in open(dir + 'common.words'):
            common_words.add(line.strip())
        dic_key = dic_key_word(e1, e2, path, sent, ADE_keywords, common_words)

        if dic_key is not None:
            mod1s, mod2s, sub_key = htm.supplement(sent, e1, e2, graph, deps_dir, None, dic_key, None)
            htm_present.append(htm.htm_represent(sent, e1, e2, mod1s, mod2s, dic_key, sub_key))
            key = []
            key.append(dic_key)
            return key