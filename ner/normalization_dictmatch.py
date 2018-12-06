#encoding=utf-8
'''
Created on 2017.4.19

@author: Administrator
normalizaiton-dictionary exact match method
'''
import sys,getopt
import os
import codecs 
import StringIO;
#load concept table
def loadConceptTable(dName):
    #{{{
    """
    load concept table for downstream process 
    @param:
        dName:      python string, the directory  name of concept table 
    @return:
        result:     python dict,  (word)->(id)
    """
    #{{{
    conceptTable={}
    for s in os.listdir(dName):
    	fin_dic=codecs.open(dName+s,'r','utf-8')
#        fin_dic=open(dicfile_path+s,'r',encoding='utf-8')
        line=next(fin_dic)
        for line in fin_dic:
            line=line.strip()
            segs=line.split("|")
            key=segs[2].lower()
            if key not in conceptTable:
                conceptTable[key]=segs[0]
            else:
                if conceptTable[key].find(segs[0])<0:
                    conceptTable[key]=conceptTable[key]+'|'+segs[0]
        fin_dic.close()
    return conceptTable;
#}}}
#}}}
def dict_normalization_fn(conceptTable,infile):
#{{{
    """
    do normalization process 
    @param:
        conceptTable:   python dict, concept table,  (word)->(id)
        infile:         python string, the text need to normalizaiton
    @return:
        result:         python string
    """
    #{{{
    fin_ner=StringIO.StringIO(infile);
    fout=StringIO.StringIO();
#    fin_ner=open(combine_infile,'r',encoding='utf-8')
#    fout=open(outfile,'w',encoding='utf-8')
    for line in fin_ner:
        text=line
        fout.write(text)
        while line!='':
            line=next(fin_ner).strip()
            if line!='':
                segs=line.split('\t')
                key=segs[2].lower()
                if key in conceptTable:
                    fout.write(line+'\t'+conceptTable[key]+'\n')
                else:
                    fout.write(line+'\t'+'undetermined'+'\n')
        fout.write('\n')
    fin_ner.close()
    return fout.getvalue();
#}}}
#}}}
def dict_normalization(dicfile_path,combine_infile,outfile):
    #{{{
    fin_ner=codecs.open(combine_infile,'r','utf-8')
    fout=codecs.open(outfile,'w','utf-8')
#    fin_ner=open(combine_infile,'r',encoding='utf-8')
#    fout=open(outfile,'w',encoding='utf-8')
    dict={}
    for s in os.listdir(dicfile_path):
    	fin_dic=codecs.open(dicfile_path+s,'r','utf-8')
#        fin_dic=open(dicfile_path+s,'r',encoding='utf-8')
        line=next(fin_dic)
        for line in fin_dic:
            line=line.strip()
            segs=line.split("|")
            key=segs[2].lower()
            if key not in dict:
                dict[key]=segs[0]
            else:
                if dict[key].find(segs[0])<0:
                    dict[key]=dict[key]+'|'+segs[0]
        fin_dic.close()
    for line in fin_ner:
        text=line
        fout.write(text)
        while line!='':
            line=next(fin_ner).strip()
            if line!='':
                segs=line.split('\t')
                key=segs[2].lower()
                if key in dict:
                    fout.write(line+'\t'+dict[key]+'\n')
                else:
                    fout.write(line+'\t'+'undetermined'+'\n')
        fout.write('\n')
    fin_ner.close()
    fout.close()
#}}}

def usage():
    print sys.argv[0]+' -c dicfile_path -n combine__infile -o outfile'

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "hc:n:o:")
    dicfile_path=''
    outfile=''
    combine_infile=''

    if len(sys.argv)<3:
        usage()
        sys.exit()
    for op, value in opts:
        if op == "-c":
            dicfile_path = value
        elif op == "-o":
            outfile = value
        elif op=="-n":
            combine_infile = value
        elif op == "-h":
            usage()
            sys.exit()
    dict_normalization(dicfile_path,combine_infile,outfile)

