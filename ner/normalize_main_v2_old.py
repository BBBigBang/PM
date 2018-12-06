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
from utils_nor_v2 import CID2Abstract,GetStr2CID_Dic,GetModel
from utils_nor_v2 import GetEntityVec,GetLowerDic,GetNoSimDic,GetSimDic,GetToken2EntityDic
from utils_nor_v2 import SaveNoSimDic,SaveSimDic
from Functions_nor_v2 import ExactMatch,FindSimilar,str2vec,FindStandard,GetPartMatchSet
import time
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
    
    Entity2Vec_genes = {}
    Entity2Vec_diseases = {}
    Entity2Vec_chemicals = {}#将实体向量词典保存为词典型，便于生成部分匹配集
    for i in range(genes_num):
        Entity2Vec_genes[genes[i]] = genes_vec[i]
    for i in range(diseases_num):
        Entity2Vec_diseases[diseases[i]] = diseases_vec[i]
    for i in range(chemicals_num):
        Entity2Vec_chemicals[chemicals[i]] = chemicals_vec[i]
    print 'done'

    #print 'loading memory entity...',
    #Entity2Sim_dic = GetSimDic(dictFNames['nor_sim'])
    #NoSimdic = GetNoSimDic(dictFNames['nor_nosim'])
    #print 'done'

    print 'loading token_entity dict...',
    Token2Entity_dic = GetToken2EntityDic(dictFNames['nor_token_entity'])
    print 'done'

    print 'loading PM_ontology...',
    str2CID_dic = GetStr2CID_Dic(dictFNames['nor_cid_all'])#得到word与CID映射的字典
    drugs_dic = GetStr2CID_Dic(dictFNames['nor_cid_drug'])
    phenotypes_dic = GetStr2CID_Dic(dictFNames['nor_cid_phenotype'])
    diseases_dic = GetStr2CID_Dic(dictFNames['nor_cid_disease'])
    cells_dic = GetStr2CID_Dic(dictFNames['nor_cid_cell'])
    genes_dic = GetStr2CID_Dic(dictFNames['nor_cid_gene'])
    #moleculars_dic = GetStr2CID_Dic(dictFNames['nor_cid_mole'])
    mutation_dic = GetStr2CID_Dic(dictFNames['nor_cid_mutation'])
    label2dic = {'dna':genes_dic,'rna':genes_dic,'drug':drugs_dic,'disease':diseases_dic,'phenotype':phenotypes_dic,'cell':cells_dic,'protein':genes_dic,'mutation':mutation_dic}
    print 'done'

    print 'loading lower dic...',
    LowerDic = GetLowerDic(dictFNames['nor_cid_all'])
    print 'done'

    print 'loading ID-abstract dict...',
    CID2Abstract_dic = CID2Abstract(dictFNames['nor_cid_all'])
    print 'done'                                                
    nor_dicts={"model":model,
               "Entity2Vec_genes":Entity2Vec_genes,
               "Entity2Vec_diseases":Entity2Vec_diseases,
               "Entity2Vec_chemicals":Entity2Vec_chemicals,
               "Token2Entity_dic":Token2Entity_dic,
               "str2CID_dic":str2CID_dic,"label2dic":label2dic,
               "LowerDic":LowerDic,"CID2Abstract_dic":CID2Abstract_dic}
    return nor_dicts

def normalize_v2_fn(nor_dicts,infile):
    
    model = nor_dicts['model']
    
    Entity2Vec_genes = nor_dicts['Entity2Vec_genes']
    Entity2Vec_diseases = nor_dicts['Entity2Vec_diseases']
    Entity2Vec_chemicals = nor_dicts['Entity2Vec_chemicals']
    
    Token2Entity_dic = nor_dicts['Token2Entity_dic']
    
    str2CID_dic = nor_dicts['str2CID_dic']
    label2dic = nor_dicts['label2dic']
    
    LowerDic = nor_dicts['LowerDic']    
    CID2Abstract_dic = nor_dicts['CID2Abstract_dic']
    
    qiyiword = 0#存在歧义的数量
    exactmatch = 0#精确匹配数量
    match = 0#成功匹配的数量
    nomatch = 0#匹配失败的数量
    num = 0#总处理数量
    xiaoqinum = 0#歧义数量
    p = 0.9#相似度阈值

    #input
    fp2 = StringIO.StringIO(infile)
    articles = fp2.read()#读取待匹配的文章
    fp2.close()
    #output
    fp3 = StringIO.StringIO()

    
    articles = articles.split('\n\n')[0:-1]#切分成列表 每项都是一个文章
    article_num=0
    for x in range(len(articles)):
        article_num+=1
        if article_num%500==0:
            print article_num,'......',
        #start =time.clock()
        text = articles[x].split('\n')
        #精确匹配
        text[0]=text[0].replace('ssss ','',1)
        for i in range(1,len(text)):#每一个文章中的实体
            num = num + 1
            entity = text[i].split('\t')
            word = entity[2]
            label = entity[3]#该实体的类别
            simword,matchlabel = ExactMatch(word,LowerDic,num,text[0])
            if simword == u'none':
                nomatch += 1
                #print '精确匹配失败第%d个'%nomatch
            else:
                exactmatch += 1
                match += 1
                #print '精确匹配成功第%d个'%exactmatch
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
        #模糊匹配
        abstract = text[0]
        for i in range(1,len(text)):#对于每一行实体
            entity = text[i].split('\t')
            if len(entity) == 4:#没有精确匹配结果
                word = entity[2]
                label = entity[3]
    #                print '不在已匹配词典中'
                before = word#保留原型
                if word.upper() == word and len(word)<6:#还原缩写
                    standard = FindStandard(word,abstract)
                    if standard != u'null':
                        word = standard
                entityvec = str2vec(word,model)#计算当前实体的词向量
                if np.sum(entityvec) == 0:#词向量全0 则跳过
                    nomatch += 1
                    #print u'匹配失败第%d个 无词向量'%nomatch
                else:
                    if label ==u'drug':
                        #得到当前实体的部分匹配集
                        #start =time.clock()
                        partmatchs_vec,partmatchs_set = GetPartMatchSet(word,Entity2Vec_chemicals,Token2Entity_dic)
                        #end = time.clock()
                        #print('部分匹配集时间: %s Seconds'%(end-start))
                        if len(partmatchs_set) == 0:
                            nomatch +=1
                            #print u'匹配失败第%d个 在无匹配词典中'%nomatch
                            continue                        
                        partmatchs_vec = np.array(partmatchs_vec)
                        #start =time.clock()
                        similarNo,maxsim = FindSimilar(entityvec,partmatchs_vec,len(partmatchs_set))
                        #end = time.clock()
                        #print('计算相似度时间: %s Seconds'%(end-start))
                        similarEntity = partmatchs_set[similarNo]
                    if label ==u'dna' or label ==u'rna' or label ==u'protein':
                        partmatchs_vec,partmatchs_set = GetPartMatchSet(word,Entity2Vec_genes,Token2Entity_dic)
                        if len(partmatchs_set) == 0:
                            nomatch +=1
                            #print u'匹配失败第%d个 在无匹配词典中'%nomatch
                            continue
                        partmatchs_vec = np.array(partmatchs_vec)
                        similarNo,maxsim = FindSimilar(entityvec,partmatchs_vec,len(partmatchs_set))
                        similarEntity = partmatchs_set[similarNo]
                    if label ==u'disease':
                        partmatchs_vec,partmatchs_set = GetPartMatchSet(word,Entity2Vec_diseases,Token2Entity_dic)
                        if len(partmatchs_set) == 0:
                            nomatch +=1
                            #print u'匹配失败第%d个 在无匹配词典中'%nomatch
                            continue
                        partmatchs_vec = np.array(partmatchs_vec)
                        similarNo,maxsim = FindSimilar(entityvec,partmatchs_vec,len(partmatchs_set))
                        similarEntity = partmatchs_set[similarNo]
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
                            #print u'匹配成功第%d个'%match
                            text[i] = '\t'.join(entity)
                            sim = [label,similarEntity]
                            #Entity2Sim_dic[before] = sim
                        except:
                            nomatch += 1
                            #print u'匹配失败第%d个 未知错误'%nomatch
                            pass
                    else:#词向量小于阈值 匹配失败
                        #NoSimdic[before] = label
                        nomatch += 1
                        #print u'匹配失败第%d个 相似度过低'%nomatch
        
        #消歧   
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
                    #print CIDs[0]
                    #print CID2Abstract_dic[CIDs[0]]
                    if  CIDs[0] in CID2Abstract_dic:
                        unique_abstract = CID2Abstract_dic[CIDs[0]]
                    else:
                        print "00000"
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
    #写入文件
        i=0
        for each in text:
            if i!=0:
                segs=each.split('\t')
                if len(segs)<5: 
                    each=str(int(segs[0])-5)+'\t'+str(int(segs[1])-5)+'\t'+segs[2]+'\t'+segs[3]+'\t'+'undetermined'
                else:
                    each=str(int(segs[0])-5)+'\t'+str(int(segs[1])-5)+'\t'+segs[2]+'\t'+segs[3]+'\t'+segs[4]
            fp3.write(each+'\n')
            i+=1
        fp3.write('\n')
        #end = time.clock()
        #print('nor时间: %s Seconds'%(end-start))
    #print 'nor_v2 done'
    #SaveSimDic(u'../data/相似实体词典.txt',Entity2Sim_dic)
    #SaveNoSimDic(u'../data/无相似实体词典.txt',NoSimdic)
    #print '相似实体词典保存完成'
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
    normalize_v2(infile,outfile)

