# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 20:48:32 2017

@author: cmy
"""
import codecs as cs
#import numpy as np
def GetStr2CID_Dic(filepath):#字符串 to CID的映射，字典
    fp = cs.open(filepath,'r','utf-8')
    content = fp.read()
    fp.close()
    dic = {}
    content = content.split('\n\n')[0:-1]#去除最后的空白
    for i in range(len(content)):
        words = content[i].split('\n')
        for j in range(1,len(words)):
            try:
                name = words[j].split('|')[2]
                CID = words[j].split('|')[0]
                if dic.has_key(name):
                    if CID not in dic[name]:
                        dic[name].append(CID)
                else:
                    dic[name] = []
                    dic[name].append(CID)
            except:
                print words
                break
    return dic

def GetModel(filepath,emb_dim):#单词 to 向量的映射，dic形式,emb_dim是词向量维度
    model = {}
    fp = cs.open(filepath,'r','utf-8')
    content = fp.readlines()[1:]
    fp.close()
    for each in content:
        each = each.split(' ')
        model[each[0]] = []
        for i in range(1,emb_dim+1):
            model[each[0]].append(float(each[i]))
    return model

def CID2Abstract(path):#CID to 摘要,词典
    fp = cs.open(path,'r','utf-8')
    context = fp.read()
    fp.close()
    dic = {}
    context = context.split('\n\n')[0:-1]
    for j in range(len(context)):
        text = context[j].split('\n')
        abstract = text[0]
        CID = text[1].split(u'|')[0]
        dic[CID] = abstract
    return dic


def GetEntityVec(filepath):#实体列表 and 实体的向量（列表型）
    fp = cs.open(filepath,'r','utf-8')
    content = fp.readlines()[0:-1]
    fp.close()
#     no = 0
    entitys = []#可以计算向量的实体
    entitys_vec = []#对应的向量
    for each in content:
#         no += 1
#         print no
        entity = each.split(u'|')[0]
        entitys.append(entity)
        entityvec = each.split(u'|')[1].split(' ')
        floatvec = []
        for x in entityvec:
            floatvec.append(float(x))
        entitys_vec.append(floatvec)
    return entitys,entitys_vec
def GetLowerDic(filepath):#字符串 to CID的映射，字典
    fp = cs.open(filepath,'r','utf-8')
    content = fp.read()
    fp.close()
    dic = {}
    content = content.split('\n\n')[0:-1]#去除最后的空白
    for i in range(len(content)):
        words = content[i].split('\n')
        for j in range(1,len(words)):
            try:
                name = words[j].split('|')[2]
                lowername = name.lower()
                dic[lowername] = name
            except:
                print words
                break
    return dic
def GetSimDic(filepath):
    fp = cs.open(filepath,'r','utf-8')
    content = fp.read()
    fp.close()
    dic = {}
    content = content.split('\n')[:-1]
    for each in content:
        word = each.split('\t')[0]
        label = each.split('\t')[1]
        sim = each.split('\t')[2]
        dic[word] = [label,sim]
    return dic
def GetNoSimDic(filepath):
    fp = cs.open(filepath,'r','utf-8')
    content = fp.read()
    fp.close()
    dic = {}
    content = content.split('\n')[:-1]
    for each in content:
        word = each.split('\t')[0]
        label = each.split('\t')[1]
        dic[word] = label
    return dic
def SaveSimDic(filepath,dic):
    fp = cs.open(filepath,'w','utf-8')
    for each in dic:
        fp.write(each+u'\t'+dic[each][0]+u'\t'+dic[each][1]+u'\n')
    fp.close()
def SaveNoSimDic(filepath,dic):
    fp = cs.open(filepath,'w','utf-8')
    for each in dic:
        fp.write(each+u'\t'+dic[each]+u'\n')
    fp.close()