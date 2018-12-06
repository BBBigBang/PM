# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 10:15:11 2018

@author: SYW
"""
import sys,getopt
import codecs
import StringIO

################################################################
#tmVar输出（tmVar output）格式2目的输出（final output）格式
##################################################################

CID2RCVdict={}#本体文件中CID2RCV（1-n）
RCV2CIDdict={}#本体文件中RCV2CID（1-1）
RSID2RCVdict={}#映射文件RSID2RCV（1-n）
RCV2RSIDdict={}#映射文件RCV2RSID（1-1）


def load_RCV2CID(path):
    CID2RCVdict1={}#本体文件中CID2RCV（1-n）
    RCV2CIDdict1={}#本体文件中RCV2CID（1-1）
    with open(path,'r') as file2read:
        content=file2read.read()
    content=content.split('\n\n')[:-1]
    for article in content:
        article=article.split('\n')[1]
        article=article.split('|')
        cid=article[0]
        rcv=article[5].split('ClinVar:')[1]
        if '*' in rcv:
            rcv=rcv.split('*')[0]
        rcv=rcv.split(';')
        if cid not in CID2RCVdict:
            CID2RCVdict[cid]=rcv
        for item in rcv:
            if item not in RCV2CIDdict:
                RCV2CIDdict[item]=cid
    file2read.close()
    return RCV2CIDdict1,CID2RCVdict1
	
def load_RSID2RCV(path):
    RSID2RCVdict1={}#映射文件RSID2RCV（1-n）
    RCV2RSIDdict1={}#映射文件RCV2RSID（1-1）
    with open(path,'r') as file2read:
        content=file2read.read()
    content=content.split('\n')[1:-1]
    for article in content:
        article=article.split('\t')
        rsid=article[9]
        rcv=article[11].split(';')
        if rsid not in RSID2RCVdict:
            RSID2RCVdict[rsid]=rcv
        for item in rcv:
            if item not in RCV2RSIDdict:
                RCV2RSIDdict[item]=rsid
    file2read.close()
    return RSID2RCVdict1,RCV2RSIDdict1

def load_tmvarmap(tmvarFNames):
    RCV2CIDdict1,CID2RCVdict1 = load_RCV2CID(tmvarFNames['cidrcvF'])
    RSID2RCVdict1,RCV2RSIDdict1 = load_RSID2RCV(tmvarFNames['rsidrcvF'])
    tmvar_dicts={"RCV2CIDdict":RCV2CIDdict1,
                 "CID2RCVdict":CID2RCVdict1,
                 "RSID2RCVdict":RSID2RCVdict1,
                 "RCV2RSIDdict":RCV2RSIDdict1}
    return tmvar_dicts

def tmVaro2fo_fn(infile,tmvar_dicts):
#    nomalizedfile='../data/data/mut_normalized_test.tmVaroutput.pubtator'
#    outputfile='../data/data/mut_normalized.finaloutput.tsv'
#    RSID2RCVfile='/home/BIO/fengjingkun/precision_medicine/py/dlut/ner_v2/MR_tmVarSoftware/mapping/variant_mapping_rsid2rcv.txt'
#    RCV2CIDfile='/home/BIO/fengjingkun/precision_medicine/py/dlut/ner_v2/MR_tmVarSoftware/mapping/mutation_withCID'

    RCV2CIDdict = tmvar_dicts['RCV2CIDdict']
    CID2RCVdict = tmvar_dicts['CID2RCVdict']
    RSID2RCVdict = tmvar_dicts['RSID2RCVdict']
    RCV2RSIDdict = tmvar_dicts['RCV2RSIDdict']

    fin=codecs.open(infile,'r','utf-8')
    #fout=codecs.open(outfile,'w','utf-8')   
    fout = StringIO.StringIO()
    content=fin.read()
    content=content.split('\n\n')[:-1]
    fin.close()
    #将源文件格式转化为pubtator格式
    for article in content:
        article=article.split('\n')
        title=article[0].split('|t|')[1]
        abstract=article[1].split('|a|')[1]
        fout.write(title + ' ' + abstract + '\n')
        if len(article) > 2 :
            for i in range(2,len(article)) :
                item = article[i].split('\t')
                start = item[1]
                end = item[2]
                mut = item[3]
                rsid='none'
                mcid='none'
                if item[4] == 'SNP':#mutation 类型是SNP，只有RSID号
                    rsid = item[5].split('rs')
                    if len(rsid)>1:
                        rsid=rsid[1]
                    else:
                        rsid='none'
                elif 'RS#:' in item[5]:
                    cont = item[5].split(';RS#:')[1]
                    if 'MC' in cont:
                        mcid=rsid
                    else:
                        rsid=cont
                    ### 获取RSID，寻找MCID
                if rsid!='none' and mcid=='none':
                    cidlist=[]
                    if rsid in RSID2RCVdict:
                        rcv=RSID2RCVdict[rsid]
                        for each in rcv:
                            if each in RCV2CIDdict:
                                cid=RCV2CIDdict[each]
                                if cid not in cidlist:
                                    cidlist.append(cid)
                    else:
                        cidlist.append('none')
                    fout.write(start + '\t' + end + '\t' + mut + '\t' + 'mutation' + '\t')
                    if len(cidlist)>1:
                        for j in range(len(cidlist)-1):
                            fout.write('M'+cidlist[j] + ';')
                        fout.write('M'+cidlist[len(cidlist)-1] + '/RS' + rsid +'\n')
                    elif len(cidlist) == 1 and cidlist[0]!='none':
                        fout.write('M'+cidlist[0] + '/RS' + rsid +'\n')
                    elif len(cidlist) == 1 and cidlist[0]=='none':
                        fout.write(cidlist[0] + '/RS' + rsid +'\n')
                    else:
                        fout.write('none' + '/RS' + rsid +'\n')
                elif rsid=='none' and mcid!='none':
                    fout.write(start + '\t' + end + '\t' + mut + '\t' + 'mutation' + '\tM'+mcid+'/'+rsid+'\n')
                else:
                    fout.write(start + '\t' + end + '\t' + mut + '\t' + 'mutation' + '\t'+mcid+'/'+rsid+'\n')
        fout.write('\n')
    return fout.getvalue()
def GenerateRCV2CID(path):
    with open(path,'r') as file2read:
        content=file2read.read()
    content=content.split('\n\n')[:-1]
    for article in content:
        article=article.split('\n')[1]
        article=article.split('|')
        cid=article[0]
        rcv=article[5].split('ClinVar:')[1]
        if '*' in rcv:
            rcv=rcv.split('*')[0]
        rcv=rcv.split(';')
        if cid not in CID2RCVdict:
            CID2RCVdict[cid]=rcv
        for item in rcv:
            if item not in RCV2CIDdict:
                RCV2CIDdict[item]=cid
def GenerateRSID2RCV(path):
    with open(path,'r') as file2read:
        content=file2read.read()
    content=content.split('\n')[1:-1]
    for article in content:
        article=article.split('\t')
        rsid=article[9]
        rcv=article[11].split(';')
        if rsid not in RSID2RCVdict:
            RSID2RCVdict[rsid]=rcv
        for item in rcv:
            if item not in RCV2RSIDdict:
                RCV2RSIDdict[item]=rsid
                

def tmVaro2fo(infile,outfile):
#    nomalizedfile='../data/data/mut_normalized_test.tmVaroutput.pubtator'
#    outputfile='../data/data/mut_normalized.finaloutput.tsv'
    RSID2RCVfile='/home/BIO/fengjingkun/precision_medicine/py/dlut/ner_v2/MR_tmVarSoftware/mapping/variant_mapping_rsid2rcv.txt'
    RCV2CIDfile='/home/BIO/fengjingkun/precision_medicine/py/dlut/ner_v2/MR_tmVarSoftware/mapping/mutation_withCID'

    GenerateRCV2CID(RCV2CIDfile)
    GenerateRSID2RCV(RSID2RCVfile)
    
    fin=codecs.open(infile,'r','utf-8')
    fout=codecs.open(outfile,'w','utf-8')   
    content=fin.read()
    content=content.split('\n\n')[:-1]
    
    #将源文件格式转化为pubtator格式
    for article in content:
        article=article.split('\n')
        title=article[0].split('|t|')[1]
        abstract=article[1].split('|a|')[1]
        fout.write(title + ' ' + abstract + '\n')
        if len(article) > 2 :
            for i in range(2,len(article)) :
                item = article[i].split('\t')
                start = item[1]
                end = item[2]
                mut = item[3]
                rsid='none'
                mcid='none'
                if item[4] == 'SNP':#mutation 类型是SNP，只有RSID号
                    rsid = item[5].split('rs')
                    if len(rsid)>1:
                        rsid=rsid[1]
                    else:
                        rsid='none'
                elif 'RS#:' in item[5]:
                    cont = item[5].split(';RS#:')[1]
                    if 'MC' in cont:
                        mcid=rsid
                    else:
                        rsid=cont
                    ### 获取RSID，寻找MCID
                if rsid!='none' and mcid=='none':
                    cidlist=[]
                    if rsid in RSID2RCVdict:
                        rcv=RSID2RCVdict[rsid]
                        for each in rcv:
                            if each in RCV2CIDdict:
                                cid=RCV2CIDdict[each]
                                if cid not in cidlist:
                                    cidlist.append(cid)
                    else:
                        cidlist.append('none')
                    fout.write(start + '\t' + end + '\t' + mut + '\t' + 'mutation' + '\t')
                    if len(cidlist)>1:
                        for j in range(len(cidlist)-1):
                            fout.write('M'+cidlist[j] + ';')
                        fout.write('M'+cidlist[len(cidlist)-1] + '/RS' + rsid +'\n')
                    elif len(cidlist) == 1 and cidlist[0]!='none':
                        fout.write('M'+cidlist[0] + '/RS' + rsid +'\n')
                    elif len(cidlist) == 1 and cidlist[0]=='none':
                        fout.write(cidlist[0] + '/RS' + rsid +'\n')
                    else:
                        fout.write('none' + '/RS' + rsid +'\n')
                elif rsid=='none' and mcid!='none':
                    fout.write(start + '\t' + end + '\t' + mut + '\t' + 'mutation' + '\tM'+mcid+'/'+rsid+'\n')
                else:
                    fout.write(start + '\t' + end + '\t' + mut + '\t' + 'mutation' + '\t'+mcid+'/'+rsid+'\n')
        fout.write('\n')
                
def usage():
    print(sys.argv[0]+'-i inputfile -o outputfile')
if __name__=="__main__":
    opts,args=getopt.getopt(sys.argv[1:],"hi:o:")
    inputfile=''
    outputfile=''
    
    if len(sys.argv)<2:
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
    tmVaro2fo(inputfile,outputfile)
