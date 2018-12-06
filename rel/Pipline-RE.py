'''
Created on 2017.10.24

@author: ZZH
'''

import Corpus_PM
import LSTM_RE_Predict
import FileUtil
import subprocess
import os, sys
import Keyword_Extraction




home_dir = '../'
model_file = home_dir + 'data/liver.in.train.h5'
threshold = 0.9

if len(sys.argv) != 2:
    print 'Wrong paramters for work type'
    sys.exit()

abstracts_with_ner = sys.argv[1]

print '#############################################'
print 'Generate instances from previous NER results'
print '#############################################'
print
insts_embed_list, insts_offset_list = Corpus_PM.gen_insts_from_abstracts(abstracts_with_ner)
# if len(insts_embed_list) == 0:
#     return [],[]  


print '#############################################'
print 'Filter possible negative instances'
print '#############################################'
print
insts_embed_list, insts_offset_list = Corpus_PM.filter_possible_negatives(insts_embed_list, insts_offset_list)
# if len(insts_embed_list) == 0:
#     return [],[]  

print '#############################################'
print 'Predict relations between the various biomedical entities'
print '#############################################'
print
answer_array_test, filtered_index = LSTM_RE_Predict.binary_relation_extraction(insts_embed_list, model_file, home_dir)

print answer_array_test

# if len(answer_array_test)==0:
#     return [],[]
print 'Classification done'

true_insts_offset = LSTM_RE_Predict.get_true_insts(insts_offset_list, answer_array_test, filtered_index, threshold)
# if len(true_insts_offset)==0:
#     return [],[]

print 'Extract relational entity pairs done.'

print '#############################################'
print 'Parsing corresonding sentences for interaction word extraction'
print '#############################################'
print
inst_index_list, sent_list = Corpus_PM.process_insts_4_parser(true_insts_offset)
FileUtil.writeStrLines(home_dir + 'tempt.sent', sent_list)
return_code = subprocess.call('java -mx3g -cp "' + home_dir + 'stanford-parser/*"' + ' edu.stanford.nlp.parser.lexparser.LexicalizedParser ' \
                                '-outputFormat "wordsAndTags,typedDependencies" -sentences newline' + \
                                ' edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz ' +  \
                              home_dir + 'tempt.sent > ' + home_dir + 'tempt.sent.par', shell=True)
assert return_code == 0

print '#############################################'  
print 'Keyword Extraction'
print '#############################################'
print
out_htm = home_dir + '../PM_RE.htm'  
nodes_list, edge_list, triple_list = Keyword_Extraction.extraction_mid_version(inst_index_list, home_dir + 'tempt.sent.par', out_htm)
print 'Find', len(triple_list), 'triples successfully.'





    
    