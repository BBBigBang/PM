#encoding=utf-8
'''
Created on 2017.4.17

@author: Ling Luo
dict-based NER
Output:BIO-dict
'''
import sys,getopt
import os
import codecs 
import StringIO;

#data structure trie
class Trie(object):
#{{{
    class Node(object):
        def __init__(self):
            self.term = None
            self.next = {}
    
    def __init__(self, terms=[]):
        self.root = Trie.Node()
        for term in terms:
            self.add(term)
    
    def add(self, term):
        node = self.root
        for char in term:
            if not char in node.next:
                node.next[char] = Trie.Node()
            node = node.next[char]
        node.term = term
    
    def match(self, query):
        results = []
        for i in range(len(query)):
            node = self.root
            for j in range(i, len(query)):
                node = node.next.get(query[j])
                if not node:
                    break
                if node.term:
                    results.append((i, len(node.term)))
        return results
    
    def __repr__(self):
        output = []
        def _debug(output, char, node, depth=0):
            output.append('%s[%s][%s]' % (' '*depth, char, node.term))
            for (key, n) in node.next.items():
                _debug(output, key, n, depth+1)
        _debug(output, '', self.root)
        return '\n'.join(output)
#}}}

#dict-based NER function version 
#load dict 
def loadDic(dictFName):
#{{{
    """
    from file load dict, and use Class Trie  to build match structure.
    @param:
        dictFName:      python string. the file name of dict 
    @return:
        result:         an instance of Class Trie
    """
#{{{
    dicin=codecs.open(dictFName,'r','utf-8')
    win_size=500 #the length of string over win_zise will be filtered
    Dic=[]
    print 'loading dict....'
    for line in dicin:
        line=line.strip()
        if len(line.split())<=win_size:
            words=line.split()
            for i in range(len(words)):
                if len(words[i])>3 and (not words[i].isupper()):
                    words[i]=words[i].lower()
            line=' '.join(words[0:])
            Dic.append(line.strip())
    print "Dic_len:",len(Dic)
    dicin.close()
    ac = Trie(Dic)
    print "load dic complete";
    return ac;
#}}}
#}}}
def dict_based_BIO_fn(source,ac,entityname):
#{{{
    """
    use dict based approach to do NER 
    @param:
        source:     python 2D string list, utf-8, should have be tokened 
                    such as [['w','w',...],['w','w',...],...]
        ac:         an instance of class Trie, use for dict matching
    @return:
        result:     python 3D string list, utf-8
                    such as [[['w','l'],['w','l'],...],[['w','l'],...]]
    """
#{{{
    #lower cast for dict matching 
    import copy;
    souceTmp=copy.deepcopy(source);
    for i in range(len(souceTmp)):
        souceTmp[i][0]=souceTmp[i][0].lower();
        for j in range(len(souceTmp[i])):
            if len(souceTmp[i][j])>3 and (not souceTmp[i][j].isupper()):
                souceTmp[i][j]=souceTmp[i][j].lower();
    
    #start dic matching 
    #{{{
    ftemp=[];
    ftempSent=[];
    for k in range(len(source)):
        sent = souceTmp[k]
        sentence=' '.join(sent[0:])+" "
#         print(sentence)
        result=ac.match(sentence)
#         print(result)
#         for word in result:
#             print("old:",sentence[word[0]:word[0]+word[1]])
        new_result=[]
        old=(0,0)
        flag=-1
    #     print(old[1])
        for i in result:
            if i[0]!=old[0] and old[0]>flag and old!=(0,0):
                if old[0]==0 and sentence[old[1]]==" ":
                    new_result.append(old)
                    flag=old[0]+old[1]
                    old=i
                elif old[0]>0 and sentence[old[0]-1]==' ' and sentence[old[0]+old[1]]==' ':
                    new_result.append(old)
                    flag=old[0]+old[1]
                    old=i
                else:
                    old=i      
            else:
                old=i
        if old[0]>flag and old!=(0,0):
            if old[0]==0 and sentence[old[1]]==" ":
                new_result.append(old)
            elif old[0]>0 and sentence[old[0]-1]==' ' and sentence[old[0]+old[1]]==' ':
                new_result.append(old)
             
        if len(new_result)==0:
            for token in sent:
                ftempSent.append([token,'O'])
            ftemp.append(ftempSent);
            ftempSent=[];
             
        else:  
            j=0
            old_i=0
            i=0 
            while i<len(sentence):
#                 print(j)
                if j<len(new_result):
                    if i==new_result[j][0]:

                            segs=sentence[new_result[j][0]:new_result[j][0]+new_result[j][1]].split()
#                             print("pre:",segs)
                            for t in range(len(segs)):
#                                 print(segs)
                                if t==0:
                                    ftempSent.append([segs[t],'B-'+entityname])
                                else:
                                    ftempSent.append([segs[t],'I-'+entityname])
                            i=i+new_result[j][1]+1
                            old_i=i
                            j+=1

                    else:
                        if sentence[i]==" ":
                            ftempSent.append([sentence[old_i:i],'O'])
                            old_i=i+1
                            i+=1
                        else:
                            i+=1
                else:
                    if sentence[i]==" ":
                        ftempSent.append([sentence[old_i:i],'O'])
                        old_i=i+1
                        i+=1
                    else:
                        i+=1
            ftemp.append(ftempSent);
            ftempSent=[]
                      
        if k%1000==0:
            print k,'.......',
   #}}}
    
    #recover capital
    #maybe we can change in dict matching to omit this recover
    for i in range(len(source)):
        for j in range(len(source[i])):
            ftemp[i][j][0]=source[i][j]
    return ftemp;
#}}}
#}}}
def loadDics(dictFNames):
#{{{
    """
    load multi dict. 
    @param:
        dictFNames:     python dict. the key is the name of the dict, the value is the file name.
    @return:
        dicts:          python dict. the key is the name of the dict, the value is an instance of Trie. 
    """
    dicts={};
    for key,value in dictFNames.items():
        ac_dict=loadDic(value);
        if dicts.has_key(key):
            raise RuntimeError("%s key appear more than once in dict names"%(key));
        else:
            dicts[key]=ac_dict;
    return dicts;
#}}}

#dict-based NER
def dict_based_BIO(inifle,dictfile,outfile):
#{{{
    tempfile='dict.temp'
    fin=codecs.open(infile,'r','utf-8')
    dicin=codecs.open(dictfile,'r','utf-8')
    fout=codecs.open(tempfile,'w','utf-8')
#    fin=open(infile,'r',encoding='utf-8')
#    dicin=open(dictfile,'r',encoding='utf-8')
#    fout=open(tempfile,'w',encoding='utf-8')
    win_size=500 #the length of string over win_zise will be filtered
    Dic=[]
    print 'loading dict....'
    for line in dicin:
        line=line.strip()
        if len(line.split())<=win_size:
            words=line.split()
            for i in range(len(words)):
                if len(words[i])>3 and (not words[i].isupper()):
                    words[i]=words[i].lower()
            line=' '.join(words[0:])
            Dic.append(line.strip())
    print "Dic_len:",len(Dic)
    dicin.close()
  
    sent_list=[]
    sent = []

    i=0
    for line in fin:
        line=line.strip()
        if line=="":
            sent_list.append(sent)
            sent=[]
            i=0
        else:
            words=line.split('\t')
            if i==0:
                words[0]=words[0].lower()
            else:
                if len(words[0])>3 and (not words[0].isupper()):
                    words[0]=words[0].lower()
            sent.append(words[0])
            i+=1
           
    sent=[]
    fin.close()
     
    ac = Trie(Dic)
#     print(ac.match('acids'))
    print 'complete successfully...' 
    for k in range(len(sent_list)):
        sent = sent_list[k]
        sentence=' '.join(sent[0:])+" "
#         print(sentence)
        result=ac.match(sentence)
#         print(result)
#         for word in result:
#             print("old:",sentence[word[0]:word[0]+word[1]])
        new_result=[]
        old=(0,0)
        flag=-1
    #     print(old[1])
        for i in result:
            if i[0]!=old[0] and old[0]>flag and old!=(0,0):
                if old[0]==0 and sentence[old[1]]==" ":
                    new_result.append(old)
                    flag=old[0]+old[1]
                    old=i
                elif old[0]>0 and sentence[old[0]-1]==' ' and sentence[old[0]+old[1]]==' ':
                    new_result.append(old)
                    flag=old[0]+old[1]
                    old=i
                else:
                    old=i      
            else:
                old=i
        if old[0]>flag and old!=(0,0):
            if old[0]==0 and sentence[old[1]]==" ":
                new_result.append(old)
            elif old[0]>0 and sentence[old[0]-1]==' ' and sentence[old[0]+old[1]]==' ':
                new_result.append(old)
             
        if len(new_result)==0:
            for token in sent:
                fout.write(token+'\t'+'O'+'\n')
            fout.write('\n')
             
        else:  
            j=0
            old_i=0
            i=0 
            while i<len(sentence):
#                 print(j)
                if j<len(new_result):
                    if i==new_result[j][0]:

                            segs=sentence[new_result[j][0]:new_result[j][0]+new_result[j][1]].split()
#                             print("pre:",segs)
                            for t in range(len(segs)):
#                                 print(segs)
                                if t==0:
                                    fout.write(segs[t]+'\t'+'B-dict'+'\n')
                                else:
                                    fout.write(segs[t]+'\t'+'I-dict'+'\n')
                            i=i+new_result[j][1]+1
                            old_i=i
                            j+=1

                    else:
                        if sentence[i]==" ":
                            fout.write(sentence[old_i:i]+'\t'+'O'+'\n')
                            old_i=i+1
                            i+=1
                        else:
                            i+=1
                else:
                    if sentence[i]==" ":
                        fout.write(sentence[old_i:i]+'\t'+'O'+'\n')
                        old_i=i+1
                        i+=1
                    else:
                        i+=1
            fout.write('\n')
                      
        if k%1000==0:
            print k,'.......',
    fout.close()
    
    fin=codecs.open(infile,'r','utf-8')
    fout=codecs.open(tempfile,'r','utf-8')
    fout_real=codecs.open(outfile,'w','utf-8')
#    fin=open(infile,'r',encoding='utf-8')
#    fout=open(tempfile,'r',encoding='utf-8')
#    fout_real=open(outfile,'w',encoding='utf-8')
    
    for line in fin:
        line=line.strip()
        dic_line=next(fout).strip()
        if line!='':
            seg_line=line.split('\t')
            seg_dic=dic_line.split('\t')
            fout_real.write(seg_line[0]+'\t'+seg_dic[1]+'\n')
        else:
            fout_real.write('\n')
    fin.close()
    fout.close()
    fout_real.close()
    if os.path.exists('dict.temp'):
        os.remove('dict.temp')    
#}}}
def usage():
    print sys.argv[0]+' -i inputfile -d dictfile -o outputfile'

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "hi:d:o:")
    infile=''
    outfile=''
    dictfile=''

    if len(sys.argv)<3:
        usage()
        sys.exit()
    for op, value in opts:
        if op == "-i":
            infile = value
        elif op == "-o":
            outfile = value
        elif op=="-d":
            dictfile = value
        elif op == "-h":
            usage()
            sys.exit()
    dict_based_BIO(infile, dictfile, outfile)
