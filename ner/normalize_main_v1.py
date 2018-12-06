# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 21:45:51 2017

@author: cmy
"""
import sys,getopt
import os
import codecs as cs
import numpy as np
import StringIO
from utils_Nor_v1 import CID2Abstract,GetStr2CID_Dic,GetModel
from utils_Nor_v1 import GetEntityVec,GetLowerDic,GetNoSimDic,GetSimDic
from utils_Nor_v1 import SaveNoSimDic,SaveSimDic
from Functions_Nor_v1 import ExactMatch,FindSimilar,str2vec,FindStandard

def loadDicts(dictFNames):
    print 'loading embedding model...',
    model = GetModel(dictFNames['nor_w2v'],50)
    print 'done'

    print 'loading entity_vec dict...',
    genes,genes_vec = GetEntityVec(dictFNames['nor_ec_gene'])
    diseases,diseases_vec = GetEntityVec(dictFNames['nor_ec_disease'])
    chemicals,chemicals_vec = GetEntityVec(dictFNames['nor_ec_drug'])
    genes_num = len(genes_vec)
    diseases_num = len(diseases_vec)
    chemicals_num = len(chemicals_vec)
    genes_vec = np.array(genes_vec)
    diseases_vec = np.array(diseases_vec)
    chemicals_vec = np.array(chemicals_vec)
    print 'done'

    print 'loading memory entity...',
    Entity2Sim_dic = GetSimDic(dictFNames['nor_sim'])
    NoSimdic = GetNoSimDic(dictFNames['nor_nosim'])
    print 'done'

    print 'loading PM_ontology...',
    str2CID_dic = GetStr2CID_Dic(dictFNames['nor_cid_all'])#得到word与CID映射的字典
    drugs_dic = GetStr2CID_Dic(dictFNames['nor_cid_drug'])
    phenotypes_dic = GetStr2CID_Dic(dictFNames['nor_cid_phenotype'])
    diseases_dic = GetStr2CID_Dic(dictFNames['nor_cid_disease'])
    cells_dic = GetStr2CID_Dic(dictFNames['nor_cid_cell'])
    genes_dic = GetStr2CID_Dic(dictFNames['nor_cid_gene'])
    moleculars_dic = GetStr2CID_Dic(dictFNames['nor_cid_mole'])
    label2dic = {'dna':genes_dic,'rna':genes_dic,'drug':drugs_dic,'disease':diseases_dic,'phenotype':phenotypes_dic,'cell':cells_dic,'protein':drugs_dic}
    print 'done'

    print 'loading lower dic...',
    LowerDic = GetLowerDic(dictFNames['nor_cid_all'])
    print 'done'

    print 'loading ID-abstract dict...',
    CID2Abstract_dic = CID2Abstract(dictFNames['nor_cid_all'])
    print 'done'                                                
    nor_dicts={"model":model,
               "genes":genes,"genes_vec":genes_vec,"genes_num":genes_num,
               "diseases":diseases,"diseases_vec":diseases_vec,"diseases_num":diseases_num,
               "chemicals":chemicals,"chemicals_vec":chemicals_vec,"chemicals_num":chemicals_num,
               "Entity2Sim_dic":Entity2Sim_dic,"NoSimdic":NoSimdic,
               "str2CID_dic":str2CID_dic,"label2dic":label2dic,
               "LowerDic":LowerDic,"CID2Abstract_dic":CID2Abstract_dic}
    return nor_dicts

def normalize_v1_fn(nor_dicts,infile):
    
    model = nor_dicts['model']
    
    genes=nor_dicts['genes']
    genes_vec = nor_dicts['genes_vec']
    diseases=nor_dicts['diseases']
    diseases_vec = nor_dicts['diseases_vec']
    chemicals=nor_dicts['chemicals']
    chemicals_vec = nor_dicts['chemicals_vec']
    genes_num = nor_dicts['genes_num']
    diseases_num = nor_dicts['diseases_num']
    chemicals_num = nor_dicts['chemicals_num']

    
    Entity2Sim_dic = nor_dicts['Entity2Sim_dic']
    NoSimdic = nor_dicts['NoSimdic']
    
    str2CID_dic = nor_dicts['str2CID_dic']#得到word与CID映射的字典
    label2dic = nor_dicts['label2dic']
    
    LowerDic = nor_dicts['LowerDic']
    CID2Abstract_dic = nor_dicts['CID2Abstract_dic']
    
    qiyiword = 0#存在歧义的数量
    exactmatch = 0#精确匹配数量
    match = 0#成功匹配的数量
    nomatch = 0#匹配失败的数量
    num = 0#总处理数量
    xiaoqinum = 0#歧义数量
    p = 0.92#相似度阈值

    #input
    fp2 = StringIO.StringIO(infile)
    articles = fp2.read()#读取待匹配的文章
    fp2.close()
    #output
    fp3 = StringIO.StringIO()
    
    #精确匹配
    articles = articles.split('\n\n')[0:-1]#切分成列表 每项都是一个文章
    for x in range(len(articles)):
        if (x+1)%50==0:
            print x+1,'......',
        #print x+1,'...',
        text = articles[x].split('\n')
        for i in range(1,len(text)):#每一个文章中的实体
            num = num + 1
            entity = text[i].split('\t')
            word = entity[2]
            label = entity[3]#该实体的类别
            abstract = text[0]
            simword,matchlabel = ExactMatch(word,LowerDic,num,text[0]) #返回匹配的词和使用的规则
    
            #精确匹配失败，使用模糊匹配
            if simword == u'none':
                if word in NoSimdic:
                    nomatch +=1
    
                elif word in Entity2Sim_dic:
                    if Entity2Sim_dic[word][0] == label:
                        try:#用已经词向量匹配后的词典进行匹配
                            similarEntity = Entity2Sim_dic[word][1]
                            try:
                                CID = label2dic[label][similarEntity]
                            except:
                                CID = str2CID_dic[similarEntity]
                            if len(CID)>1:
                                qiyiword += 1
                                entity.append('|'.join(CID))
                            else:
                                entity.append(CID[0])
                            entity.append(similarEntity)
                            entity.append(u'词向量匹配')
                            match += 1
    #                         text[i] = '\t'.join(entity)
                        except:
                            nomatch += 1
                    else:
    #                     print '在已匹配词典中，类别不同'
                        before = word
                        if word.upper() == word and len(word)<6:
                            standard = FindStandard(word,abstract)
                            if standard != u'null':
                                word = standard
                        entityvec = str2vec(word,model)#计算当前实体的词向量
                        if np.sum(entityvec) == 0:#词向量全0 则跳过
                            nomatch += 1
    #                         print u'匹配失败第%d个'%nomatch
                        else:
                            if label =='drug'or label =='protein':
                                similarNo,maxsim = FindSimilar(entityvec,chemicals_vec,chemicals_num)
                                similarEntity = chemicals[similarNo]
                            elif label =='dna' or label =='rna':
                                similarNo,maxsim = FindSimilar(entityvec,genes_vec,genes_num)
                                similarEntity = genes[similarNo]
                            else:
                                similarNo,maxsim = FindSimilar(entityvec,diseases_vec,diseases_num)
                                similarEntity = diseases[similarNo]
                            if maxsim>p:#如果相似度大于阈值，匹配成功
                                try:
                                    try:
                                        CID = label2dic[label][similarEntity]
                                    except:
                                        CID = str2CID_dic[similarEntity]
                                    if len(CID)>1:
                                        qiyiword += 1
                                        entity.append(u'|'.join(CID))
                                    else:
                                        entity.append(CID[0])
                                    entity.append(similarEntity)
                                    entity.append(u'词向量匹配')
                                    match += 1
    #                                 print u'匹配成功第%d个'%match
    #                                 text[i] = '\t'.join(entity)
                                    sim = [label,similarEntity]
                                    Entity2Sim_dic[before] = sim
                                except:
                                    nomatch += 1
    #                                 print u'匹配失败第%d个'%nomatch
                            else:#词向量小于阈值 匹配失败
                                nomatch+=1
    #                             print u'匹配失败第%d个'%nomatch
                else:
    #                 print '不在已匹配词典中'
                    before = word
                    if word.upper() == word and len(word)<6:
                        standard = FindStandard(word,abstract)
                        if standard != u'null':
                            word = standard
                    entityvec = str2vec(word,model)#计算当前实体的词向量
                    if np.sum(entityvec) == 0:#词向量全0 则跳过
                        nomatch += 1
    #                     print u'匹配失败第%d个'%nomatch
                    else:
                        if label =='drug'or label =='protein':
                            similarNo,maxsim = FindSimilar(entityvec,chemicals_vec,chemicals_num)
                            similarEntity = chemicals[similarNo]
                        elif label =='dna' or label =='rna':
                            similarNo,maxsim = FindSimilar(entityvec,genes_vec,genes_num)
                            similarEntity = genes[similarNo]
                        else:
                            similarNo,maxsim = FindSimilar(entityvec,diseases_vec,diseases_num)
                            similarEntity = diseases[similarNo]
                        #print maxsim
                        if maxsim>p:#如果相似度大于阈值，匹配成功
                            try:
                                try:
                                    CID = label2dic[label][similarEntity]
                                except:
                                    CID = str2CID_dic[similarEntity]
                                if len(CID)>1:
                                    qiyiword += 1
                                    entity.append(u'|'.join(CID))
                                else:
                                    entity.append(CID[0])
                                entity.append(similarEntity)
                                entity.append(u'词向量匹配')
                                match += 1
    #                             print u'匹配成功第%d个'%match
    #                             text[i] = '\t'.join(entity)
                                sim = [label,similarEntity]
                                Entity2Sim_dic[before] = sim
                            except:
                                nomatch += 1
    #                             print u'匹配失败第%d个'%nomatch
    #                             pass
                        else:#词向量小于阈值 匹配失败
                            NoSimdic[before] = label
                            nomatch += 1
    #                         print u'匹配失败第%d个'%nomatch
                   
            else:
                exactmatch += 1
                match += 1
    #             print '精确匹配成功第%d个'%exactmatch
                try:
                    CID = label2dic[label][simword]
                except:
                    CID = str2CID_dic[simword]
                if len(CID)>1:
                    qiyiword += 1
                    entity.append(u'|'.join(CID))
                else:
                    entity.append(CID[0])
                entity.append(simword)
                entity.append(matchlabel)
            text[i] = '\t'.join(entity)
        articles[x] = '\n'.join(text)
    
    
    #消歧   
    for x in range(len(articles)):#选择摘要的序号
        text = articles[x].split('\n')
        if len(text)==1:#如果没有实体 则跳过该摘要
            continue
        for i in range(1,len(text)):#对于每一行/实体
            entity = text[i].split('\t')
            if len(entity) == 4:#如果没有匹配
                continue
            else:
                CIDs = entity[4].split(u'|')
                if len(CIDs) == 1:#如果不存在歧义
                    continue
                else:#如果存在歧义
                    #两个CID如果摘要相同，保留一个
                    unique_abstract = CID2Abstract_dic[CIDs[0]]
                    if_unique = 1
                    for j in range(1,len(CIDs)):
                        if CID2Abstract_dic[CIDs[j]] != unique_abstract:
                            if_unique = 0
                    if if_unique == 1:#如果CID的摘要相同
                        xiaoqinum +=1
                        entity[4] = CIDs[0]
                        text[i] = '\t'.join(entity)
                    else:#如果摘要不同
                        abstracts_vec = []
                        for CID in CIDs:
                            abstract  = CID2Abstract_dic[CID]
                            abstracts_vec.append(str2vec(abstract,model).tolist())
                        abstracts_vec = np.array(abstracts_vec)
                        article_vec = str2vec(text[0],model)
                        similarNo,maxsim = FindSimilar(article_vec,abstracts_vec,len(CIDs))
                        xiaoqinum +=1
                        entity[4] = CIDs[similarNo]
                        text[i] = '\t'.join(entity)                    
        articles[x] = '\n'.join(text)
    
    for x in range(len(articles)):#选择摘要的序号
        text = articles[x].split('\n')
        i=0
        for each in text:
            if i!=0:
                segs=each.split('\t')
                if len(segs)<5: 
                    each=each+'\t'+'undetermined'
                else:
                    each=segs[0]+'\t'+segs[1]+'\t'+segs[2]+'\t'+segs[3]+'\t'+segs[4]
            fp3.write(each+'\n')
            i+=1
        fp3.write('\n')
    print 'nor done!'
#    SaveSimDic(u'./input/nor_data/memory_sim_dic.txt',Entity2Sim_dic)
#    SaveNoSimDic(u'./input/nor_data/memory_nosim_dic.txt',NoSimdic)
#    print '相似实体词典保存完成'
    return fp3.getvalue()
def usage():
    print sys.argv[0]+' -i infile -o outfile'
if __name__=='__main__':
    opts, args=getopt.getopt(sys.argv[1:],"hi:o:")
    infile=''
    outfile=''
    if len(sys.argv)<3:
        usage()
        sys.exit()
    for op, value in opts:
        if op=="-i":
            infile = value
        elif op=="-o":
            outfile=value
        elif op=='-h':
            usage()
            sys.exit()
    normalize_v1(infile,outfile)
