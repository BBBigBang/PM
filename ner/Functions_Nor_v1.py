# -*- coding: utf-8 -*-
"""
Created on Fri Nov 03 16:45:12 2017

@author: cmy
"""
import re
import numpy as np
def SingleOrPlural(word):#单复数变形
    words = []
    #每个单词增加s
    words.append(word.lower())
    trans = word.split(' ')
    for i in range(len(trans)):
        trans[i] = trans[i] + u's'
        newword = ' '.join(trans)
        words.append(newword.lower())
        trans[i] = trans[i][0:-1]
    #去除某单词的s
    trans = word.split(' ')
    for i in range(len(trans)):
        temp = trans[i]
        if trans[i][-1:] == u's':
            trans[i] = trans[i][0:-1]
            newword = ' '.join(trans)
            words.append(newword.lower())
            trans[i] = temp
    return words
#def AaBaCc(word):#对word进行一些大小写替换，并且返回列表
#    words = []
#    words.append(word)
#    words.append(word.upper())#全大写
#    words.append(word.lower())#全小写
#    words.append(word.capitalize())#首字母大写
#    words.append(word.title())#每个单词的首字母大写
#    trans = word.split(' ')
#    for i in range(0,len(trans)):#某个分词保持不变 其余分词首字母大写
#        for j in range(0,len(trans)):
#            if i!=j:
#                trans[j] = trans[j].capitalize()
#        trans = ' '.join(trans)
#        words.append(trans)
#        trans = word.split(' ')
#    for i in range(0,len(trans)):#某个分词保持不变 其余分词小写
#        for j in range(0,len(trans)):
#            if i!=j:
#                trans[j] = trans[j].lower()
#        trans = ' '.join(trans)
#        words.append(trans)
#        trans = word.split(' ')
#    for i in range(0,len(trans)):#某个分词保持不变 其余分词大写
#        for j in range(0,len(trans)):
#            if i!=j:
#                trans[j] = trans[j].upper()
#        trans = ' '.join(trans)
#        words.append(trans)
#        trans = word.split(' ')
#    return words
def trans1(word):#将-替换为空格 或分成两个实体
    words = []
    trans = word.split(' ')
    tag = 0
    for i in range(len(trans)):
        if trans[i] == u'-':
            tag = 1
            break
    if tag == 1:
        if i==1:
            childword = trans[1:]
            childword = ' '.join(childword)
            words.append(childword)
        elif i == (len(trans) -1):
            childword = trans[:-1]
            childword = ' '.join(childword)
            words.append(childword)
        else:            
            transleft = ' '.join(trans[0:i])
            transright = ' '.join(trans[i+1:])
            newword = trans[0:i] + trans[i+1:]
            newword = ' '.join(newword)
            words.append(newword)
            words.append(transleft)    
            words.append(transright)
    return words
def trans2(word):#将and型拆分
    words = []
    trans = word.split(' ')
    tag = 0
    for i in range(len(trans)):
        if trans[i] == u'and':
            tag = 1
            break
    if tag == 1:
        if i == 0:
            childword = trans[1:]
            childword = ' '.join(childword)
            words.append(childword)
        elif i == (len(trans) -1):
            childword = trans[:-1]
            childword = ' '.join(childword)
            words.append(childword)
        else:
            childword1 = trans[0:i] + trans[i+2:]
            childword2 = trans[0:i-1] + trans[i+1:]
            childword1 = ' '.join(childword1)
            childword2 = ' '.join(childword2)
            words.append(childword1)
            words.append(childword2)
    return words

def trans3(word):#去除括号内容
    words = []
    trans = word.split(' ')
    tag = 0
    for i in range(len(trans)):
        try:
            if trans[i][0] == u'(' and trans[i][-1] == u')':
                tag = 1
                break
        except:
            continue
    if tag == 1:
        if i == 0:
            newword = trans[1:]
        elif i == (len(trans)-1): 
            newword = trans[0:-1]
        else:
            newword = trans[0:i] + trans[i+1:]
        newword = ' '.join(newword)
        words.append(newword)
    return words

def trans4(word):#替换特殊字符
    words = []
    if u'α' in word:
        newword = re.sub(u'α',u'alpha',word)
        words.append(newword)
    if u'β' in word:
        newword = re.sub(u'β',u'beta',word)
        words.append(newword)
    return words

def trans5(word):#部分匹配
    words = []
    trans = word.split(' ')
    if len(trans) > 2 and len(trans) < 8:
        for i in range(len(trans)):
            newword = ' '.join(trans[0:i]+trans[i+1:])
            words.append(newword)               
    return words


def OrderExist(word,standard,no):#判断word中的字符是否顺序存在于字符串standard  no为第几个字符
    if no >= len(word):
        return 1
    if word[no] in standard:
        direct = standard.index(word[no])#找到当前字符的索引
        return OrderExist(word,standard[direct+1:],no+1)
    elif word[no].lower() in standard:
        direct = standard.index(word[no].lower())
        return OrderExist(word,standard[direct+1:],no+1)
    else:
        return 0
def FindStandard(word,abstract):#为缩写在摘要中寻找原型
    words = abstract.split(' ')
    abbr_exist = 0
    for i in range(len(words)):
        if word == words[i][1:-1]:#找到缩写所在的索引
            abbr_exist = 1
            direct = i
            break
    if abbr_exist == 0:
        return u'null'
    for begin in range(direct-1,direct-len(word)-2,-1):
        standard = ' '.join(words[begin:direct])#从后向前产生备选原型
        temp = OrderExist(word,standard,0)
        if temp == 1:#如果缩写中的字符顺序存在于该字符串
            return standard
    return u'null'

def ExactMatch(word,dic,num,abstract):
#     if num == 22328:#此实体会导致系统崩溃？？？！！！
#         return u'none',u'???'
    #print '精确匹配第%d个'%num
    words = []
    nowlen = 0
    beforelen = 0
    #缩写-原型
    if word.upper() == word and len(word)<6:
        standard = FindStandard(word,abstract)
        if standard != u'null':
            #fp4.write(word+'\t'+standard+'\n')
            words.append(standard)
            trans = []
            beforelen = nowlen
            nowlen = len(words)
            for each in words[beforelen:nowlen]:
                trans.extend(SingleOrPlural(each))
            for each in trans:
                if each in dic:
                    return dic[each],u'缩写处理'
    #完全匹配及其单复数大小写
    words.append(word)
    if word.lower() in dic:
        return dic[word.lower()],u'完全匹配'
    trans = []#存放当前words里实体的单复数变型及大小写变型
    beforelen = nowlen
    nowlen = len(words)
    for each in words[beforelen:nowlen]:
        trans.extend(SingleOrPlural(each))
    for each in trans:
        if each in dic:
            return dic[each],u'单复数或大小写'
        
    #-
    tempwords = []
    for each in words:
        tempwords.append(each)
    for each in tempwords:
        words.extend(trans1(each))
    trans = []
    beforelen = nowlen
    nowlen = len(words)
    for each in words[beforelen:nowlen]:
        trans.extend(SingleOrPlural(each))
    for each in trans:
        if each in dic:
            return dic[each],u'横线处理'
    #and
    tempwords = []
    for each in words:
        tempwords.append(each)
    for each in tempwords:
        words.extend(trans2(each))
    trans = []
    beforelen = nowlen
    nowlen = len(words)
    for each in words[beforelen:nowlen]:
        trans.extend(SingleOrPlural(each))
    for each in trans:
        if each in dic:
            return dic[each],u'and处理'
    #()
    tempwords = []
    for each in words:
        tempwords.append(each)
    for each in tempwords:
        words.extend(trans3(each))
    trans = []
    beforelen = nowlen
    nowlen = len(words)
    for each in words[beforelen:nowlen]:
        trans.extend(SingleOrPlural(each))
    for each in trans:
        if each in dic:
            return dic[each],u'（）处理'
    #特殊字符及数字
    tempwords = []
    for each in words:
        tempwords.append(each)
    for each in tempwords:
        words.extend(trans4(each))
    trans = []
    beforelen = nowlen
    nowlen = len(words)
    for each in words[beforelen:nowlen]:
        trans.extend(SingleOrPlural(each))
    for each in trans:
        if each in dic:
            return dic[each],u'特殊字符替换'     
    return u'none',u'???'
def sample_token4(oristr):#对待匹配的实体进行字符串预处理

    punctuation1=[u'.u',u'!',u'?',u'"']
    punctuation2=[u'•',u'●',u'-',u'—',u':',u';',u'%',u'+',u'=',u'~',u'#',u'$',u'&',u'*',u'/',u'@',\
                  u'"',u'?',u'!',u'[',u']',u'{',u'}',u'(',u')',u'<',u'>',\
                  u'→',u'↓',u'←',u'↔',u'↑',u'≃',u'⁺',u'···',u'®',u'≧',u'≈',u'⋅⋅⋅',u'·',u'…',u'...',u'‰',u'€',u'≥',u'∼',\
                  u'Δ',u'≤',u'δ',u'™',u'•',u'∗',u'⩾',u'Σ',u'Φ',u'∑',u'ƒ',u'≡',u'═',u'φ',u'Ψ',u'˙',u'Π',u'≫']
    punctuation3=[u',']#周围有空格才切
    punctuation4=[u"'"]#'s的情况，s'的情况，还有周围不是空格的情况

    line=oristr
    line=line.strip()
    for pun in punctuation2:
        line=line.replace(pun,u" "+pun+u" ")
#         print(line)
    if line!='':    
        if line[-1] in punctuation1:
            line=line[:-1]+u" "+line[-1]+u" "
    
    new_line=u""
    i=0
    
    while(len(line)!=0):
        if(i==len(line)-1): 
            new_line=new_line+line[0:i+1]
            break
        elif line[i] in punctuation3:
            if line[i-1]==u' ' or line[i+1]==u' ':
                new_line=new_line+line[:i]+u" "+line[i]+u" "
                line=line[i+1:]
                i=0
            else:
                i=i+1
        else:
            i=i+1
            
    line=new_line+u" "
    new_line=u""
    i=0
    while(len(line)!=0): 
        if(i==len(line)-1): 
            new_line=new_line+line[0:i+1]
            break
        elif line[i] in punctuation4:
            if line[i-1]==u' ' or line[i+1]==u' ':
                new_line=new_line+line[:i]+u" "+line[i]+u" "
                line=line[i+1:]
                i=0
            elif line[i+1]==u's' and line[i+2]==u' ':
                new_line=new_line+line[:i]+u" "+line[i]+u"s "
                line=line[i+2:]
                i=0
            else:
                i=i+1
        else:
            i=i+1
            
    words=new_line.split()
    new_line=u""
    for word in words:
        new_line+=word+u" "
            
    return new_line


def str2vec(str1,model):#实体（含空格的字符串） to 实体向量（numpy型）
    str1 = sample_token4(str1)
    str1 = str1.lower()
    words = str1.split(' ')
    num = 0.0
    sumvec = np.zeros(50)
    for each in words:
        each = each.lower()
        try:
            wordvec = np.array(model[each])
            sumvec = sumvec + wordvec
            num = num + 1
        except:
            pass
    if num == 0:#避免分母为0
        num = 1.0
    sumvec = sumvec/num
    return sumvec


def FindSimilar(entityvec,entitys_vec,entitys_num):#找到欧式距离最小的向量，并返回序号
    minID = 0
    maxsim = 0
#    def cos_sim(vec,nowvec):#vec为词典中实体的向量，nowvec为当前匹配词的向量
#        num = np.vdot(vec,nowvec)  
#        denom = np.linalg.norm(nowvec) * np.linalg.norm(vec)  
#        cos = num / denom #余弦值  
#        sim = 0.5 + 0.5 * cos #归一化
#        sim = np.array([sim])#！！！把数值型变为array型，不然就只是0维度的数
#        return sim
#    def ou_sim(vec,nowvec):
#        dist = np.linalg.norm(nowvec - vec)  
#        sim = 1.0 / (1.0 + dist) #归一化
#        sim = np.array([sim])
#        return sim
#    SimMethod1 = np.vectorize(cos_sim,signature = '(n),(m)->(k)')#n为参数1维度，m为参数2维度，k为新的维度
#    #SimMethod2 = np.vectorize(ou_sim,signature = '(n),(m)->(k)')
#    similarity = SimMethod1(entitys_vec,entityvec)
#    minID = np.argmax(similarity)
    import normalizeCpython;
    return normalizeCpython.findSimilar(entityvec,entitys_vec);
    import time; 
    startTime=time.time(); 
    for i in range(entitys_num):
        dist = np.linalg.norm(entityvec - entitys_vec[i])  
        print(type(dist));
        print(dist.ndim)
        sim = 1.0 / (1.0 + dist) #归一化
        num = np.vdot(entityvec,entitys_vec[i])  
        print(type(num));
        print(num.ndim);
        denom = np.linalg.norm(entityvec) * np.linalg.norm(entitys_vec[i])  
        print(type(denom))
        print(denom.ndim)
        cos = num / denom #余弦值  
        sim = 0.5 + 0.5 * cos #归一化
        if sim > maxsim:
            minID = i
            maxsim = sim
    #print(time.time()-startTime);
    return minID,maxsim
