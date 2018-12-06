#encoding=utf-8
'''
Created on 2017.4.17

@author: Ling Luo
Combine the results of machine learning method and dictionary method
'''
import sys, getopt
import os
import codecs 
import StringIO;
def combine_ml_dict_fn(ml_file,dic_file): 
#{{{
    """
    merge the output of machine learning approach and dic approach 
    @param:
        ml_file:    python string, the output of machine learning
        dic_file:   python string, the output of dict approach 
    @return:
        result:     python string
    """
#{{{
    fin_dic=StringIO.StringIO(dic_file);
    fin_ml=StringIO.StringIO(ml_file);
    fout=StringIO.StringIO();
#    fin_dic=open(dic_file,'r',encoding='utf-8')
#    fin_ml=open(ml_file,'r',encoding='utf-8')
#    fout=open(outfile,'w',encoding='utf-8')
    
    entity_dic=[]
    entity_ml=[]
    text=''
    num=0
    for line in fin_dic:
        num+=1
        if num%100==0:
            print num,'......',
        line=line.strip()
        text=line
        while(line!=''):
            line=next(fin_dic).strip()
            if line!='':
                entity_dic.append(line)
        line=next(fin_ml).strip()
        while(line!=''):
            line=next(fin_ml).strip()
            if line!='':
                entity_ml.append(line)
#         print(entity_dic)
#         print(entity_ml)
        len_dic=len(entity_dic)
        len_ml=len(entity_ml)
        i_dic=0
        i_ml=0
        entity_combine=[]
        while(i_dic<len_dic and i_ml<len_ml):
            segs_dic=entity_dic[i_dic].split('\t')
            segs_ml=entity_ml[i_ml].split('\t')
            if int(segs_ml[1])<int(segs_dic[0]):
                entity_combine.append(entity_ml[i_ml])
                i_ml+=1
            elif int(segs_ml[1])>=int(segs_dic[0]) and int(segs_ml[0])<int(segs_dic[0]) and int(segs_ml[1])<int(segs_dic[1]):
                entity_combine.append(entity_ml[i_ml])
                i_ml+=1
                i_dic+=1
            elif int(segs_ml[1])>=int(segs_dic[1]) and int(segs_ml[0])<=int(segs_dic[0]):
                while int(segs_dic[0])<=int(segs_ml[1]):
                    i_dic+=1
                    if i_dic>=len_dic:
                        break
                    segs_dic=entity_dic[i_dic].split('\t')
                entity_combine.append(entity_ml[i_ml])
                i_ml+=1
            elif int(segs_ml[0])>=int(segs_dic[0]) and int(segs_ml[1])<=int(segs_dic[1]):
                while int(segs_ml[0])<=int(segs_dic[1]):
                    i_ml+=1
                    if i_ml>=len_ml:
                        break
                    segs_ml=entity_ml[i_ml].split('\t')
                entity_combine.append(entity_dic[i_dic])
                i_dic+=1
            elif int(segs_ml[0])<=int(segs_dic[1]) and int(segs_ml[0])>int(segs_dic[0]) and int(segs_ml[1])>int(segs_dic[1]):
                i_dic+=1
            elif int(segs_ml[0])>int(segs_dic[1]):
                entity_combine.append(entity_dic[i_dic])
                i_dic+=1
        while(i_dic<len_dic):
            entity_combine.append(entity_dic[i_dic])
            i_dic+=1
        while(i_ml<len_ml):
            entity_combine.append(entity_ml[i_ml])
            i_ml+=1
        fout.write(text+'\n')
        for ele in entity_combine:
            fout.write(ele+'\n')
        fout.write('\n')
        entity_dic=[]
        entity_ml=[]
        entity_combine=[]
    fin_dic.close()
    fin_ml.close()
    return fout.getvalue();
#}}}
#}}}

def combine_ml_dict(ml_file,dic_file,outfile):
#{{{
    fin_dic=codecs.open(dic_file,'r','utf-8')
    fin_ml=codecs.open(ml_file,'r','utf-8')
    fout=codecs.open(outfile,'w','utf-8')
#    fin_dic=open(dic_file,'r',encoding='utf-8')
#    fin_ml=open(ml_file,'r',encoding='utf-8')
#    fout=open(outfile,'w',encoding='utf-8')
    
    entity_dic=[]
    entity_ml=[]
    text=''
    num=0
    for line in fin_dic:
        num+=1
        if num%100==0:
            print num,'......',
        line=line.strip()
        text=line
        while(line!=''):
            line=next(fin_dic).strip()
            if line!='':
                entity_dic.append(line)
        line=next(fin_ml).strip()
        while(line!=''):
            line=next(fin_ml).strip()
            if line!='':
                entity_ml.append(line)
#         print(entity_dic)
#         print(entity_ml)
        len_dic=len(entity_dic)
        len_ml=len(entity_ml)
        i_dic=0
        i_ml=0
        entity_combine=[]
        while(i_dic<len_dic and i_ml<len_ml):
            segs_dic=entity_dic[i_dic].split('\t')
            segs_ml=entity_ml[i_ml].split('\t')
            if int(segs_ml[1])<int(segs_dic[0]):
                entity_combine.append(entity_ml[i_ml])
                i_ml+=1
            elif int(segs_ml[1])>=int(segs_dic[0]) and int(segs_ml[0])<int(segs_dic[0]) and int(segs_ml[1])<int(segs_dic[1]):
                entity_combine.append(entity_ml[i_ml])
                i_ml+=1
                i_dic+=1
            elif int(segs_ml[1])>=int(segs_dic[1]) and int(segs_ml[0])<=int(segs_dic[0]):
                while int(segs_dic[0])<=int(segs_ml[1]):
                    i_dic+=1
                    if i_dic>=len_dic:
                        break
                    segs_dic=entity_dic[i_dic].split('\t')
                entity_combine.append(entity_ml[i_ml])
                i_ml+=1
            elif int(segs_ml[0])>=int(segs_dic[0]) and int(segs_ml[1])<=int(segs_dic[1]):
                while int(segs_ml[0])<=int(segs_dic[1]):
                    i_ml+=1
                    if i_ml>=len_ml:
                        break
                    segs_ml=entity_ml[i_ml].split('\t')
                entity_combine.append(entity_dic[i_dic])
                i_dic+=1
            elif int(segs_ml[0])<=int(segs_dic[1]) and int(segs_ml[0])>int(segs_dic[0]) and int(segs_ml[1])>int(segs_dic[1]):
                i_dic+=1
            elif int(segs_ml[0])>int(segs_dic[1]):
                entity_combine.append(entity_dic[i_dic])
                i_dic+=1
        while(i_dic<len_dic):
            entity_combine.append(entity_dic[i_dic])
            i_dic+=1
        while(i_ml<len_ml):
            entity_combine.append(entity_ml[i_ml])
            i_ml+=1
        fout.write(text+'\n')
        for ele in entity_combine:
            fout.write(ele+'\n')
        fout.write('\n')
        entity_dic=[]
        entity_ml=[]
        entity_combine=[]
    fin_dic.close()
    fin_ml.close()
    fout.close()
#}}}
def usage():
    print sys.argv[0]+' -m ml_file -d dic_file -o outfile'

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "hm:d:o:")
    ml_file=''
    outfile=''
    dic_file=''

    if len(sys.argv)<3:
        usage()
        sys.exit()
    for op, value in opts:
        if op == "-m":
            ml_file = value
        elif op == "-o":
            outfile = value
        elif op=="-d":
            dic_file = value
        elif op == "-h":
            usage()
            sys.exit()
    combine_ml_dict(ml_file,dic_file,outfile)
