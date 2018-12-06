#encoding=utf-8
'''
Created on 2017.4.17

@author: Ling Luo
Convert BIO format to tsv format
'''
import sys, getopt
import os
import codecs 
import StringIO;
def restore_index_type_fn(original,bio):
#{{{
    """
    restore ner's index according to original file 
    @param:
        original:   python string, the text before tokenize 
        bio:        python string, the text after NER 
    @return:
        outfile:    python string, the text after restore index
    """
    #{{{
    ENTITY_LABEL=''
    oritext_fin=StringIO.StringIO(original);
    dicbio_fin=StringIO.StringIO(bio);
    fout=StringIO.StringIO();
#    oritext_fin=open(ori_file,'r',encoding='utf-8')
#    dicbio_fin=open(infile,'r',encoding='utf-8')
#    fout=open(outfile,'w',encoding='utf-8')
    bio_line=''
    text_line=''
    entity_list=[]
    entity_line=''
    last_label='O'
    for text_line in oritext_fin:
        text_line=text_line.strip()
        len_text=len(text_line)
        currtent_index_st=0
        currtent_index_end=0
        entity_index_st=0
        entity_index_end=0
        entity_type=''
        while(currtent_index_end<len_text):
            bio_line=next(dicbio_fin).strip()
            
            if bio_line!='':
                segs=bio_line.split('\t')
                currtent_index_st=text_line.find(segs[0],currtent_index_end)
                if currtent_index_st==-1:
                    print("-1");
                    print(text_line);
                    print(bio_line);
                    raise RuntimeError("fuck");
                currtent_index_end=currtent_index_st+len(segs[0])
                if segs[1][0]=='B':
                    if last_label=='B' or last_label=='I':
                        
                        entity_line=str(entity_index_st)+'\t'+str(entity_index_end)+'\t'+text_line[entity_index_st:entity_index_end]+'\t'+entity_type
                        entity_list.append(entity_line)
                        entity_line=''
                        entity_index_st=currtent_index_st
                        entity_index_end=currtent_index_end
                        entity_type=segs[1][2:]
                    elif last_label=='O':
                        entity_index_st=currtent_index_st
                        entity_index_end=currtent_index_end
                        entity_type=segs[1][2:]
                elif segs[1][0]=='I':
                    if last_label=='B' or last_label=='I':
                        entity_index_end=currtent_index_end
                    elif last_label=='O' :
                        print('error!!! OI')
                elif segs[1][0]=='O':
                    if last_label=='B' or last_label=='I':
                        #NOTE: 'B I O' is valid, but 'I O' is Invalid
                        #in this case, entity_index_st ==0, 
                        #so we should judge entity_index_st != 0
                        if entity_index_st:
                            entity_line=str(entity_index_st)+'\t'+str(entity_index_end)+'\t'+text_line[entity_index_st:entity_index_end]+'\t'+entity_type
                            entity_list.append(entity_line)
                            entity_line=''
                    
                last_label=segs[1][0]
        fout.write(text_line+'\n')
        for ele in entity_list:
            fout.write(ele+'\t'+ENTITY_LABEL+'\n')
        fout.write('\n')
        entity_list=[]
        entity_line=''
        last_label='O'
    oritext_fin.close()
    dicbio_fin.close()
    return fout.getvalue();
#}}}
#}}}

def restore_index_type(ori_file,infile,outfile):
    #{{{
    ENTITY_LABEL=''
    oritext_fin=codecs.open(ori_file,'r','utf-8')
    dicbio_fin=codecs.open(infile,'r','utf-8')
    fout=codecs.open(outfile,'w','utf-8')
#    oritext_fin=open(ori_file,'r',encoding='utf-8')
#    dicbio_fin=open(infile,'r',encoding='utf-8')
#    fout=open(outfile,'w',encoding='utf-8')
    bio_line=''
    text_line=''
    entity_list=[]
    entity_line=''
    last_label='O'
    for text_line in oritext_fin:
        text_line=text_line.strip()
        len_text=len(text_line)
        currtent_index_st=0
        currtent_index_end=0
        entity_index_st=0
        entity_index_end=0
        entity_type=''
        while(currtent_index_end<len_text):
            bio_line=next(dicbio_fin).strip()
            
            if bio_line!='':
                segs=bio_line.split('\t')
                currtent_index_st=text_line.find(segs[0],currtent_index_end)
                currtent_index_end=currtent_index_st+len(segs[0])
                if segs[1][0]=='B':
                    if last_label=='B' or last_label=='I':
                        
                        entity_line=str(entity_index_st)+'\t'+str(entity_index_end)+'\t'+text_line[entity_index_st:entity_index_end]+'\t'+entity_type
                        entity_list.append(entity_line)
                        entity_line=''
                        entity_index_st=currtent_index_st
                        entity_index_end=currtent_index_end
                        entity_type=segs[1][2:]
                    elif last_label=='O':
                        entity_index_st=currtent_index_st
                        entity_index_end=currtent_index_end
                        entity_type=segs[1][2:]
                elif segs[1][0]=='I':
                    if last_label=='B' or last_label=='I':
                        entity_index_end=currtent_index_end
                    elif last_label=='O' :
                        print('error!!! OI')
                elif segs[1][0]=='O':
                    if last_label=='B' or last_label=='I':
                        entity_line=str(entity_index_st)+'\t'+str(entity_index_end)+'\t'+text_line[entity_index_st:entity_index_end]+'\t'+entity_type
                        entity_list.append(entity_line)
                        entity_line=''
                    
                last_label=segs[1][0]
        fout.write(text_line+'\n')
        for ele in entity_list:
            fout.write(ele+'\t'+ENTITY_LABEL+'\n')
        fout.write('\n')
        entity_list=[]
        entity_line=''
        last_label='O'
    fout.close()
    oritext_fin.close()
    dicbio_fin.close()
#}}}
def usage():
    print sys.argv[0]+' -t ori_file -i infile -o outfile'

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "hi:t:o:")
    infile=''
    outfile=''
    ori_file=''
   
    if len(sys.argv)<3:
        usage()
        sys.exit()
    for op, value in opts:
        if op == "-i":
            infile = value
        elif op == "-o":
            outfile = value
        elif op=="-t":
            ori_file = value
        elif op == "-h":
            usage()
            sys.exit()
    restore_index_type(ori_file, infile, outfile)
