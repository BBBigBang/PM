# -*- coding: utf-8 -*-
import types

mod_set = set(['amod', 'advmod', 'compound', 'compound:prt', 'nummod', 'mwe'])

clause_set = set(['advcl', 'acl', 'csubj', 'ccomp', 'csubjpass', 'acl:relcl', 'parataxis'])

transferable_set = mod_set.union(set(['conj:and', 'conj:or']))

supplement_set = set(['amod', 'compound', 'compound:prt', 'nmod:of', 'nmod:with'])
'''
    Find out the modification part
'''
def supplement(sent, e1, e2, graph, deps_dir, mod1, key, mod2):
    mod1s = []
    mod2s = []
    if key == 0:
        return mod1s, mod2s, None

    if mod1 is not None:
        mod1s.append(mod1)
    for elem in graph[e1]:
        if elem != key and elem != mod1 and \
                ((deps_dir.has_key((e1, elem)) and deps_dir[(e1, elem)] in supplement_set and abs(e1 - elem) < 5) or \
                         (deps_dir.has_key((elem, e1)) and deps_dir[(elem, e1)] in supplement_set and abs(
                                 e1 - elem) < 5)):
            if abs(e1 - elem) == 2 and (
                        sent[(e1 + elem) / 2] == ',' or sent[(e1 + elem) / 2] == ')' or sent[(e1 + elem) / 2] == '('):
                continue
            mod1s.append(elem)

    if mod2 is not None:
        mod2s.append(mod2)
    for elem in graph[e2]:
        if elem != key and elem != mod2 and \
                ((deps_dir.has_key((e2, elem)) and deps_dir[(e2, elem)] in supplement_set and abs(e2 - elem) < 5) or \
                         (deps_dir.has_key((elem, e2)) and deps_dir[(elem, e2)] in supplement_set and abs(
                                 e2 - elem) < 5)):
            if abs(e2 - elem) == 2 and (
                        sent[(e2 + elem) / 2] == ',' or sent[(e2 + elem) / 2] == ')' or sent[(e2 + elem) / 2] == '('):
                continue
            mod2s.append(elem)

    sub_key = None
    if len(mod1s) != 0:
        for mod in mod1s:
            if int(mod) == int(e1) or int(mod) == int(e2):
                mod1s.remove(mod)
    if len(mod2s) != 0:
        for mod in mod2s:
            if int(mod) == int(e1) or int(mod) == int(e2):
                mod2s.remove(mod)
    # for elem in graph[key]:
    #     if (deps_dir.has_key((key, elem)) and (
    #             deps_dir[(key, elem)] == 'neg' or deps_dir[(key, elem)] == 'conj:negcc')) or \
    #             (deps_dir.has_key((elem, key)) and (
    #                     deps_dir[(elem, key)] == 'neg' or deps_dir[(elem, key)] == 'conj:negcc')):
    #         sub_key = elem

    return mod1s, mod2s, sub_key

def htm_represent(sent, e1, e2, mod1s, mod2s, key, sub_key):
    key_color = 'red'
    entity_color = 'green'
    mod_color = 'blue'

    if type(key) is types.ListType:
        key.sort()
    sent[e1] = '<font color="' + entity_color + '"><strong>' + \
               sent[e1] + '</strong></font>'
    sent.append('\t|\t<')
    sent.append('<font color="' + entity_color + '"><strong>' + \
                sent[e1] + '</strong></font>')
    sent.append(',')

    if len(mod1s) > 0:
        for mod1 in mod1s:
            sent[mod1] = '<font color="' + mod_color + '"><strong>' + \
                         sent[mod1] + '</strong></font>'
            sent.append('<font color="' + mod_color + '"><strong>' + \
                        sent[mod1] + '</strong></font>')
    else:
        sent.append('_')
    sent.append(',')

    if sub_key is not None:
        sent[sub_key] = '<font color="' + key_color + '"><strong>' + \
                        sent[sub_key] + '</strong></font>'
        sent.append('<font color="' + key_color + '"><strong>' + \
                    sent[sub_key] + '</strong></font>')

    if type(key) is types.ListType:
        if key[0] == 0:
            sent.append('<font color="' + key_color + '"><strong>side effect</strong></font>')
            sent.append(',')
        else:
            for elem_key in key:
                sent[elem_key] = '<font color="' + key_color + '"><strong>' + \
                            sent[elem_key] + '</strong></font>'
                sent.append('<font color="' + key_color + '"><strong>' + \
                            sent[elem_key] + '</strong></font>')
                sent.append(',')
    else:
        sent[key] = '<font color="' + key_color + '"><strong>' + \
                        sent[key] + '</strong></font>'
        sent.append('<font color="' + key_color + '"><strong>' + \
                        sent[key] + '</strong></font>')
        sent.append(',')

    if len(mod2s) > 0:
        for mod2 in mod2s:
            sent[mod2] = '<font color="' + mod_color + '"><strong>' + \
                         sent[mod2] + '</strong></font>'
            sent.append('<font color="' + mod_color + '"><strong>' + \
                        sent[mod2] + '</strong></font>')
    else:
        sent.append('_')

    sent.append(',')
    sent[e2] = '<font color="' + entity_color + '"><strong>' + \
               sent[e2] + '</strong></font>'
    sent.append('<font color="' + entity_color + '"><strong>' + \
                sent[e2] + '</strong></font>')
    sent.append('>')
    sent.append('<BR><BR>')

    return ' '.join(sent)