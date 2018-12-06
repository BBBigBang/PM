
import Corpus_PM
#import LSTM_RE_Predict
import LSTM_RE_Predict_v2
import FileUtil
import subprocess
import os, sys
import Keyword_Extraction
from Constants import home_dir, threshold 
import logging;
import time;

model_file = home_dir + 'data/liver.in.train.h5'

def run(abstract, entity_list, eval, rep):
#{{{
    """
    an function to extraction relation. 
    @param:
        abstract:
        entity_list:
        eval:
        rep:
    @return:
        
    """

    logger=logging.getLogger("relation_run:");
    #print 'Generate instances from previous NER results'
    startTime=time.time();
    insts_embed_list, insts_offset_list = Corpus_PM.gen_insts_from_one_abstract(abstract, entity_list)
    logger.debug('Generate instance done, espliced:{}s'.format(time.time()-startTime));
    if len(insts_embed_list) == 0:
        return [],[]  
    
    insts_embed_list, insts_offset_list = Corpus_PM.filter_possible_negatives(insts_embed_list, insts_offset_list)
    logger.debug('Filter possible negative instances done, espliced:{}s'.format(time.time()-startTime));
    if len(insts_embed_list) == 0:
        return [],[]  

    #print 'Predict relations between the various biomedical entities'
    startTime=time.time();
    #answer_array_test, filtered_index = LSTM_RE_Predict.binary_relation_extraction(insts_embed_list, eval, rep)
    answer_array_test, filtered_index = LSTM_RE_Predict_v2.binary_relation_extraction(insts_embed_list, eval, rep)
    logger.debug('Predict relation done, espliced:{}s'.format(time.time()-startTime));

    #print answer_array_test
    if len(answer_array_test)==0:
        return [],[]

    #print 'Extract the relation entity pairs'
    startTime=time.time();
    #true_insts_offset = LSTM_RE_Predict.get_true_insts(insts_offset_list, answer_array_test, filtered_index, threshold)
    true_insts_offset = LSTM_RE_Predict_v2.get_true_insts(insts_offset_list, answer_array_test, filtered_index, threshold)
    logger.debug('Extract relation done, espliced:{}s'.format(time.time()-startTime));
    if len(true_insts_offset)==0:
        return [],[]
    
    #print 'Parsing corresonding sentences for interaction word extraction'
    startTime=time.time();
    inst_index_list, sent_list = Corpus_PM.process_insts_4_parser(true_insts_offset)


    print('###########################################################################')
    print(' length of sent_list ')
    print(len(sent_list))
    print(' max length of element in sent_list ')
    e_length = [len(k) for k in sent_list]
    print(max(e_length))
    e_all = [len(k.split(' '))  for k in sent_list]
    print(' max word quantity of element in sent_list ')
    print(max(e_all))
    print('###########################################################################')


    FileUtil.writeStrLines(home_dir + 'tempt.sent', sent_list)
    logger.debug('Parsing interaction done, espliced:{}s'.format(time.time()-startTime));
    
    startTime=time.time();
    retval = subprocess.call('java -mx3g -cp "' + home_dir + 'stanford-parser/*"' + ' edu.stanford.nlp.parser.lexparser.LexicalizedParser ' ' -nthreads 15 ' \
                                    '-outputFormat "wordsAndTags,typedDependencies" -sentences newline' + \
                                    ' edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz ' +  \
                                  home_dir + 'tempt.sent > ' + home_dir + 'tempt.sent.par',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
    logger.debug('Stanford parse done, espliced:{}s'.format(time.time()-startTime));
    assert retval == 0
    
    #print 'Keyword Extraction'
    
    startTime=time.time();
    nodes_list, edges_list, triple_list = Keyword_Extraction.extraction_mid_version(inst_index_list, home_dir + 'tempt.sent.par', home_dir + 'outHtml/out.html')
    logger.debug('Keyword extraction done, espliced:{}s'.format(time.time()-startTime));

    #print '#############################################'  
    #print 'Keyword Extraction'
    #print '#############################################'
    print 'Find', len(triple_list), 'triples successfully.'

    print 'triple_list..................'
    print triple_list

    return nodes_list, edges_list, triple_list
    #}}}

def toJson(nodes,edges):
    """
    convert relation to Json for cytoscape.js
    @param:
        nodes:      list, NOTE: should be changed! 
        edges:      list, NOTE: should be changed!
    @return:
        result:     string, json format
    """
    import output_json;
    #NOTE: here the method generate_JSONfile return python dict, 
        # NOT string, this not meet our request. 
        # we should change dumps it to string
        # so we use json dumps method 
    import json;
    return json.dumps(output_json.generate_JSONfile(nodes,edges));




