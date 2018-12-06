# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 09:45:15 2018

@author: SYW
"""
import os
import sys
import getopt
import codecs
import StringIO
###################################################
#源文本（source input）格式到GNormPlus输入（GNormPlus input）格式
##################################################

def s2Gi_fn(content,outputfile):
    #fin=codecs.open(inputfile,'r','utf-8')
    fout=codecs.open(outputfile,'w','utf-8')
    #content=fin.read()
    #fout=StringIO.StringIO()
    #print 's2gi\n\n'
    #print content
    content=content.split('\n')[:-1]
    
    #将源文件格式转化为pubtator格式
    pmid=1#按递增顺序从1开始生成pmid号
    for article in content:
        article=article.split('. ')
        title=article[0]+'.'#分割获取title
        abstract=''
        for i in range(1,len(article)-1):
            abstract=abstract+article[i]+'. '
        abstract=abstract+article[len(article)-1]+'.'#分割获取abstract
        fout.write(str(pmid)+'|t|'+title+'\n'+str(pmid)+'|a|'+abstract+'\n\n')
        pmid+=1
    fout.close()
	
def s2Gi(inputfile,outputfile):
    fin=codecs.open(inputfile,'r','utf-8')
    fout=codecs.open(outputfile,'w','utf-8')
    content=fin.read()
    print 's2gi\n\n'
    print content
    content=content.split('\n')[:-1]
    
    #将源文件格式转化为pubtator格式
    pmid=1#按递增顺序从1开始生成pmid号
    for article in content:
        article=article.split('. ')
        title=article[0]+'.'#分割获取title
        abstract=''
        for i in range(1,len(article)-1):
            abstract=abstract+article[i]+'. '
        abstract=abstract+article[len(article)-1]+'.'#分割获取abstract
        fout.write(str(pmid)+'|t|'+title+'\n'+str(pmid)+'|a|'+abstract+'\n\n')
        pmid+=1
def usage():
    print(sys.argv[0]+' -i inputfile -o outputfile')

if __name__=="__main__":
    opts,args= getopt.getopt(sys.argv[1:],"hi:o:")
    inputfile=''
    outputfile=''
    if (sys.argv)<2:
        usage()
        sys.exit()
    for op,value in opts:
        if op=="-i":
            inputfile=value
        elif op=="-o":
            outputfile=value
        elif op=="-h":
            usage()
            sys.exit()
    s2Gi(inputfile,outputfile)
