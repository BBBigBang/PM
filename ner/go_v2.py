#encoding=utf-8
'''
Created on 2017.4.25

@author: Ling Luo
run script
dutir
'''

import sys,getopt
import os
import threading
import StringIO;
import logging;
import codecs
import subprocess
from combine_dict_ml import combine_ml_dict_fn;
from restore_index import restore_index_type_fn;
from dict_based_tagger import dict_based_BIO_fn;
from html_visualization import html_visu_nor_fn;
#from normalize_main_v1 import normalize_v1_fn;
from postprocessing import postprocessing_fn;
from normalize_main_v2 import normalize_v2_fn;
from ssplit_token import ssplit_token_fn;
from s2Gi import s2Gi_fn
from tmVaro2fo import tmVaro2fo_fn
import  mlTagger;

def loadExternalDicts(dictFNames):
#{{{
    """
    load external dicts and concept table.
    @param:
        dictFNames:     python dict. the key is the name of the dict, the value is the file name.
    @return:
        dicts:          python dict. the key is the name of the dict, the value is an instance of Trie, or an conceptTable. 
    """
    from dict_based_tagger import loadDics;
    if dictFNames.has_key('concept'):
        conceptPath=dictFNames['concept'];
        del dictFNames['concept'];
    else:
        conceptPath="";
    ac_dicts=loadDics(dictFNames);
    if conceptPath:
        from normalization_dictmatch import loadConceptTable;
        conceptTable=loadConceptTable(conceptPath);
        ac_dicts['concept']=conceptTable;
    else:
        ac_dicts['concept']=None;
    return ac_dicts;
#}}}
def parseAbstractEntityList(data):
#{{{
    """
    from plain text to parse abstract and entity list.
    the plain text must be the format : abstract followed by entity list,
        each abstract is segregated by an newline.
    @param:
        data:   string.
    @return:
        result:     list. such as [{'abstract':abstract,'entity_list':[entity1,entity2,...]},{},...]
                        entity is [startPos,endPos,entityName,entityType,user-define]
    """
    fin=StringIO.StringIO(data);
    result=[];
    doc={};
    newDoc=True;
    for line in fin:
        line=line.rstrip();
        if  line :
            #read abstract and entity list
            if newDoc:
                doc['abstract']=line;
                doc['entity_list']=[];
                newDoc=False;
            else:
                #read entity list;
                line=line.split('\t');
                if len(line) < 5:
                    print(line);
                    raise RuntimeError("entity_list is %d, less than 5"%(len(line)));
                line[0]=int(line[0]);
                line[1]=int(line[1]);
                doc['entity_list'].append(line);
        else:
            #new doc 
            result.append(doc);
            doc={};
            newDoc=True;
    if len(doc) !=0:
        result.append(doc);

    return result;
#}}}

def cus_rmdir(path):
    if len(os.listdir(path)):
        for sub_name in os.listdir(path):
            #print(sub_name)
            sub_path=os.path.join(path,sub_name)
            if os.path.isfile(sub_path):
                os.remove(sub_path)
            else:
                cus_rmdir(sub_path)

def go_fn(source,
          externalDicts, #some parameters about dict approach
          norDicts, #normalization dict
          tmvar_dicts, #tmvar dict
          mlEval,parameters, #some parameters about ml approach
          ssplitSent=False,omitHeader=True,isText=True):
    """
    do all process of NER 
    @param:
        source:         python string, utf-8, needed to process 
        externalDicts:  python dict, the key is the name of dict, the value is the dict.
        mlEval:         python function object,
                            the eval function of machine learning
        parameters:     python dict,  some config about machine learning model 
        ssplitSent:     bool, whether to ssplit sentence.
        omitHeader:     bool, whether omit the header of html 
        isText:         bool, whether the source is text or file
    @return:
        result:         python string
    """
    print "This is NER_v2!"
    logger = logging.getLogger('Go_fn:')
    #load external dicts 
    ac_cell=externalDicts['ac_cell'];
    #ac_disease=externalDicts['ac_disease'];
    #ac_drug=externalDicts['ac_drug'];
    #ac_mutation=externalDicts['ac_mutation'];
    ac_phenotype=externalDicts['ac_phenotype'];
    conceptTable=externalDicts['concept'];



    # 1: tokenization
    #utf-8 convert 
    if not isinstance(source,unicode):
        logger.debug("!WARNING!, input string not utf-8, we will convert it to utf-8");
        source=source.decode('utf-8');
    import time;
    source=source.decode('utf-8')
    
    startTime=time.time();
   
    vartool_path='/home/BIO/fengjingkun/precision_medicine/py/dlut/ner_v2/MR_tmVarSoftware/'
    #f = codecs.open(vartool_path+'tmvar.temp_input','w','utf-8') 
    #f.write(source+'\n');
    #f.close()
    content = source +'\n'
    
    
    source='ssss '+source.strip()
    #source=source.replace('\n',' ')
    source=source.replace('\n','\nssss ')
    #print 'ner_input:',source

    ssplitSource=ssplit_token_fn(source,ssplitSent);
    logger.debug('source len='+str(len(ssplitSource)));
    logger.debug('token done,espliced:{}s'.format(time.time()-startTime));

    #2: NER:dict-based method and machine learning-based method 
    #transform string to 2D list, maybe we can do this in ssplit_token_fn 
    fin=StringIO.StringIO(ssplitSource);
    sent_list=[];
    for line in fin:
        line=line.strip()
        words=line.split(' ')
        #one line of a list is an document, so expand not append
        sent_list.append(words)
    fin.close(); 
    logger.debug('convert 2D list over');
    #use two thread to do 
    #from threading import Thread;
    #receive thread's return 
    #dictOutpout=[];
    mlOutpout=[];
    #threads=[];

    #dict-based method 
    ##t=Thread(target=lambda args,l:l.append(dict_based_BIO_fn(*args)),
    ##                    args=((sent_list,ac),dictOutpout));
    ##threads.append(t);
    startTime=time.time();
    mlOutpout=mlTagger.ml_fn(sent_list,mlEval,parameters); 
    logger.debug('ml over,espliced:{}s'.format(time.time()-startTime));
    startTime=time.time();
    dictOutpout_cell=dict_based_BIO_fn(sent_list,ac_cell,'cell');
    #dictOutpout_disease=dict_based_BIO_fn(sent_list,ac_disease,'disease');
    #dictOutpout_drug=dict_based_BIO_fn(sent_list,ac_drug,'drug');
    #dictOutpout_mutation=dict_based_BIO_fn(sent_list,ac_mutation,'mutation');
    dictOutpout_phenotype=dict_based_BIO_fn(sent_list,ac_phenotype,'phenotype');
    logger.debug('dict over,espliced:{}s'.format(time.time()-startTime));
    dictOutpoutStr_cell=StringIO.StringIO();
    for elem in dictOutpout_cell:
        #each sentence 
        for e in elem:
            #each word 
            dictOutpoutStr_cell.write(e[0]+'\t'+e[1]+'\n');
        dictOutpoutStr_cell.write('\n');
    """
    dictOutpoutStr_disease=StringIO.StringIO();
    for elem in dictOutpout_disease:
        #each sentence
        for e in elem:
            #each word
            dictOutpoutStr_disease.write(e[0]+'\t'+e[1]+'\n');
        dictOutpoutStr_disease.write('\n');
    
    dictOutpoutStr_drug=StringIO.StringIO();
    for elem in dictOutpout_drug:
        #each sentence
        for e in elem:
            #each word
            dictOutpoutStr_drug.write(e[0]+'\t'+e[1]+'\n');
        dictOutpoutStr_drug.write('\n');
    
    dictOutpoutStr_mutation=StringIO.StringIO();
    for elem in dictOutpout_mutation:
        #each sentence
        for e in elem:
            #each word
            dictOutpoutStr_mutation.write(e[0]+'\t'+e[1]+'\n');
        dictOutpoutStr_mutation.write('\n');
    """
    dictOutpoutStr_phenotype=StringIO.StringIO();
    for elem in dictOutpout_phenotype:
        #each sentence
        for e in elem:
            #each word
            dictOutpoutStr_phenotype.write(e[0]+'\t'+e[1]+'\n');
        dictOutpoutStr_phenotype.write('\n');
    ##mlOutpout=mlOutpout[0];
    logger.debug('ml,dict over');

    #3: restore index to produce tsv format 
    startTime=time.time();
    dictOutpout_cell=restore_index_type_fn(source,dictOutpoutStr_cell.getvalue());
    dictOutpoutStr_cell.close();
    #dictOutpout_disease=restore_index_type_fn(source,dictOutpoutStr_disease.getvalue());
    #dictOutpoutStr_disease.close();
    #dictOutpout_drug=restore_index_type_fn(source,dictOutpoutStr_drug.getvalue());
    #dictOutpoutStr_drug.close();
    #dictOutpout_mutation=restore_index_type_fn(source,dictOutpoutStr_mutation.getvalue());
    #dictOutpoutStr_mutation.close();
    dictOutpout_phenotype=restore_index_type_fn(source,dictOutpoutStr_phenotype.getvalue());
    dictOutpoutStr_phenotype.close();
    mlOutpout=restore_index_type_fn(source,mlOutpout);
    logger.debug('restore over,espliced:{}s'.format(time.time()-startTime))    ;
    #4: combine the results of dict-based and ml-based 
    startTime=time.time();
    combineOutput1=combine_ml_dict_fn(mlOutpout,dictOutpout_cell);
    #combineOutput2=combine_ml_dict_fn(combineOutput1,dictOutpout_disease);
    #combineOutput3=combine_ml_dict_fn(combineOutput2,dictOutpout_drug);
    #combineOutput3=combine_ml_dict_fn(combineOutput1,dictOutpout_mutation);
    combineOutput2=combine_ml_dict_fn(combineOutput1,dictOutpout_phenotype);
    logger.debug('combine_ml_dict_fn over,espliced:{}s'.format(time.time()-startTime));
   
    #postprocess
    startTime=time.time()
    postprocess=postprocessing_fn(combineOutput2)
    logger.debug('postprocessing_fn over,espliced:{}s'.format(time.time()-startTime));
 
    #5: normalization  
    startTime=time.time();
    #normalizationOutput=normalize_v1_fn(norDicts,combineOutput4);
    normalizationOutput=normalize_v2_fn(norDicts,postprocess);
    logger.debug('normalization over,espliced:{}s'.format(time.time()-startTime));
    #print 'Test:',isText
    '''
    if not isText:
    	logger.debug('this is not a text');
    	print normalizationOutput
    	logger.debug('------------------end---------------------')
        return normalizationOutput;
    '''
    
    #6: tmvar to tag mutation
    startTime=time.time()
    #vartool_path='/home/BIO/fengjingkun/precision_medicine/py/dlut/ner_v2/MR_tmVarSoftware/'
    #1:clean
    cus_rmdir(vartool_path+'Gin_data')
    cus_rmdir(vartool_path+'Gout_data')
    cus_rmdir(vartool_path+'TMout_data')
    #print('step 1:now clean..........\n')
    print('clean done')  
    
    #2:preprocess
    #print('#############################')
    #print('step 2: now preprocess the tobe-processed input data into pubtator format')
    #print('#############################')
    #print(infile)
    s2Gi_fn(content,vartool_path+'Gin_data/temp.txt')
    #command='python '+vartool_path+'s2Gi.py -i '+ vartool_path+'tmvar.temp_input' +' -o '+vartool_path+'Gin_data/temp.txt'
    #print('step 2:now preprocess:\n'+command+'..........')
    #os.system(command)
    print('preprocess done')
    
    #3:GnormPlus to get gene
    #print('##################################')
    #print('step 3: now GnormPlus to get gene')
    #print('###################################')
    retval = subprocess.call('cd '+vartool_path+'GNormPlusJava && java -Xmx10G -Xms10G -jar GNormPlus.jar '+vartool_path+'Gin_data '+vartool_path+'Gout_data setup.txt',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
    assert retval == 0
    
    #command='cd '+vartool_path+'GNormPlusJava && java -Xmx10G -Xms10G -jar GNormPlus.jar '+vartool_path+'Gin_data '+vartool_path+'Gout_data setup.txt'
    #print('step 3:now GNormPlus\n'+command+'..............')
    #os.system(command)
    print('GNormPlus done')
    
    #4:tmVar to normalize
    #print('##################################')
    #print('step 4: now tmVar to normalize')
    #print('###################################')
    retval1 = subprocess.call('cd '+vartool_path+'tmVarJava && java -Xmx5G -Xms5G -jar tmVar.jar '+vartool_path+'Gout_data '+vartool_path+'TMout_data',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
    assert retval1 == 0
    #command='cd '+vartool_path+'tmVarJava && java -Xmx5G -Xms5G -jar tmVar.jar '+vartool_path+'Gout_data '+vartool_path+'TMout_data'
#    command='java -Xmx5G -Xms5G -jar tmVarJava/tmVar.jar Gin_data TMout_data'#不执行第三步，直接执行第四步，输入为Gin_data中的文件，结果为不标准化
    #print('step 4:now tmVar\n'+command+'..............')
    #os.system(command)
    print('tmVar done')

    #5:post-process
    #print('##################################')
    #print('step 5: now post-process the tmVar output into final output')
    #print('###################################')
    
    tmvar_output = tmVaro2fo_fn(vartool_path+'TMout_data/temp.txt.PubTator',tmvar_dicts)
    #command='python '+vartool_path+'tmVaro2fo.py -i '+vartool_path+'TMout_data/temp.txt.PubTator -o '+ vartool_path+'tmvar.temp_out'
    #print('step 5:now post-precess'+command+'..............')
    #os.system(command)
    print('post-precess done')
    
    #f = codecs.open(vartool_path+'tmvar.temp_out','r','utf-8')
    #tmvar_output = f.read()
    #f.close()
    logger.debug('tmvar_fn over,espliced:{}s'.format(time.time()-startTime));

    finalcombineOutput=combine_ml_dict_fn(tmvar_output,normalizationOutput);
    
    if not isText:
        logger.debug('NER done');
        #print normalizationOutput
        #print finalcombineOutput
        logger.debug('------------------end---------------------')
        return finalcombineOutput;
    
    #6: output html format 
    startTime=time.time();
    result=html_visu_nor_fn(finalcombineOutput,omitHeader);

    print('go.py---the result of html_visu_nor_fn---as following : ')
    print(result)
    print('------------------------END-----------------------------')
    #print result
    #result=result.replace('####','')
    logger.debug('html_visualization over,espliced:{}s'.format(time.time()-startTime));
    return result;

def ml_based(ml_py):
    command=ml_py+' -i temp/input.token -o temp/input.token.ml_BIO -m /home/BIO/yangpei/precision_medicine/models/'
    print 'now ML NER:\n',command,'\n..........'
    os.system(command)
    print 'ML NER done........'
def dic_based(dictfile):
    command='python dict_based_tagger.py -i temp/input.token -o temp/input.token.dic_BIO -d '+dictfile
    print 'now DIC NER:\n',command,'\n..........'
    os.system(command)
    print 'DIC NER done........'
def usage():
    print sys.argv[0]+' -i inputfile -o outputfile'

if __name__=="__main__":
    dictfile='input/precision_medicine.dic_remove_sort_len'
    ml_py="THEANO_FLAGS='lib.cnmem=0.1,cuda.root=/usr/local/cuda-7.5,device=gpu0,floatX=float32' python /home/BIO/yangpei/precision_medicine/py/tagger.py"
    concept_path='concept/'
    opts, args=getopt.getopt(sys.argv[1:],"hi:o:")
    infile=''
    outfile=''
    if not os.path.exists('temp'):
        os.makedirs('temp')
    if not os.path.exists('output'):
        os.makedirs('output')

    if len(sys.argv)<2:
        usage()
        sys.exit()
    for op, value in opts:
        if op == "-i":
            infile = value
        elif op == "-o":
            outfile = value
        elif op == "-h":
            usage()
            sys.exit()

# 1: tokenization
    command='python ssplit_token.py -i '+infile+' -o temp/input.token'
    print '1: now token:\n',command,'\n..........'
    os.system(command)
    print 'token done........'
    
#2: NER:dict-based method and machine learning-based method
    threads=[]
    t=threading.Thread(target=ml_based,args=(ml_py,))
    threads.append(t)
    t=threading.Thread(target=dic_based,args=(dictfile,))
    threads.append(t)
    print '2: mul threads NER!\n'
    
    for i in range(len(threads)):
        threads[i].start()
    for i in range(len(threads)):
        threads[i].join()
    print 'all NER DONE\n'

#3: restore index to produce tsv format
    command='python restore_index.py -t '+infile+' -i temp/input.token.dic_BIO -o temp/input.token.dic_tsv'
    print '3: now restore_dic_index:\n',command,'\n.........'
    os.system(command)
    print 'restore_dic_index done.......'

    command='python restore_index.py -t '+infile+' -i temp/input.token.ml_BIO -o temp/input.token.ml_tsv'
    print '3: now restore_ml_index:\n',command,'\n.........'
    os.system(command)
    print 'restore_ml_index done.......'

#4: combine the results of dict-based and ml-based
    command='python combine_dict_ml.py -m temp/input.token.ml_tsv -d temp/input.token.dic_tsv -o temp/input.token.combine_tsv'
    print '4: now combine_index:\n',command,'\n.........'
    os.system(command)
    print 'combine_index done.......' 

#5: normalization
    command='python normalization_dictmatch.py -c '+concept_path+' -n temp/input.token.combine_tsv -o temp/input.token.ner_nor'
    print '5: now normalization:\n',command,'\n.........'
    os.system(command)
    print 'normalization done.......'

#6: output html format
    command='python html_visualization.py -i temp/input.token.ner_nor -o '+outfile
    print '6: now output:\n',command,'\n.........'
    os.system(command)
    print 'output done.......'
