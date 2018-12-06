#encoding=utf-8
'''
Created on 2017.4.7

@author: Ling Luo

Input the original text, the text will be token by the script.
Output: one token per line, the documents are divided by empty lines.

'''
import sys,getopt
import os
import codecs
import StringIO;
def ssplit_token_fn(line,ssplitSent=False):
#{{{
    """
    tokenize sentences or document.
    @param:
        line:           python sring, utf-8, needed to tokened.
        ssplitSent:     whether to ssplit sentence.
    @return:
        result:         python string, utf-8
    """
#{{{
    #utf-8 convert 
    if not isinstance(line,unicode):
        print "!WARNING!, input string not utf-8, we will convert it to utf-8";
        line=line.decode('utf-8');
    if ssplitSent:
        ftemp=StringIO.StringIO();
        #sentence_split
        char_split=['!','?','.','"'] #根据这些标点符合后面接char_end划分句子
        char_end=[' ','\t']
        line=line.strip()
        i=0
        while(len(line)!=0):
            if(i==len(line)-1):
                ftemp.write(line[0:i+1]+"\n")
                line=""
                break
            #elif (line[i] in char_split) and (line[i+1] in char_end) and (line[i+2].isupper() or not line[i+2].isalpha()): #标点后面是空格并且接大写才切句
            elif (line[i] in char_split) and (line[i+1] in char_end): 
		if(line[i]=='"'):
                    if(line[i-1] in char_split ):
                        ftemp.write(line[0:i+1]+"\n")
                        line=line[i+2:]
                        i=0
                    else:
                        i=i+1
                else:
                    ftemp.write(line[0:i+1]+"\n")
                    line=line[i+2:]
                    i=0
            else:
                i=i+1
    else:
        ftemp=StringIO.StringIO(line);
    ftemp.seek(0);
    #print 'ss:',ftemp.read()    
    #tokenize4
    punctuation1=['.','!','?','"']
    punctuation2=[u'•', u'●', u'-', u'—', u':', u';', u'%', u'+', u'=', u'~', u'#',\
                  u'$', u'&', u'*', u'/', u'@', 'u\'\'', u'?', u'!', u'[', u']', u'{', u'}',\
                  u'(', u')', u'<', u'>', u'→', u'↓', u'←', u'↔', u'↑', u'≃', u'⁺', u'···',\
                  u'®', u'≧', u'≈', u'⋅⋅⋅', u'·', u'…', u'...', u'‰', u'€', u'≥', u'∼', u'Δ',\
                  u'≤', u'δ', u'™', u'•', u'∗', u'⩾', u'Σ', u'Φ', u'∑', u'ƒ', u'≡', u'═', u'φ', u'Ψ', u'˙', u'Π', u'≫']
    punctuation3=[',']#周围有空格才切
    punctuation4=["'"]#'s的情况，s'的情况，还有周围不是空格的情况 
    ftemp.seek(0);
    fout=StringIO.StringIO()
    for line in ftemp:
        line=line.strip()
        for pun in punctuation2:
            line=line.replace(pun,u" "+pun+u" ")
        if line!='':    
            if line[-1] in punctuation1:
                line=line[:-1]+" "+line[-1]+" "
        
        new_line=""
        i=0
        
        while(len(line)!=0):
            if(i==len(line)-1): 
                new_line=new_line+line[0:i+1]
                break
            elif line[i] in punctuation3:
                if line[i-1]==' ' or line[i+1]==' ':
                    new_line=new_line+line[:i]+" "+line[i]+" "
                    line=line[i+1:]
                    i=0
                else:
                    i=i+1
            else:
                i=i+1
                
        line=new_line+" "
        new_line=""
        i=0
        while(len(line)!=0): 
            if(i==len(line)-1): 
                new_line=new_line+line[0:i+1]
                break
            elif line[i] in punctuation4:
                if line[i-1]==' ' or line[i+1]==' ':
                    new_line=new_line+line[:i]+" "+line[i]+" "
                    line=line[i+1:]
                    i=0
                elif line[i+1]=='s' and line[i+2]==' ':
                    new_line=new_line+line[:i]+" "+line[i]+"s "
                    line=line[i+2:]
                    i=0
                else:
                    i=i+1
            else:
                i=i+1
                
        words=new_line.split()
        new_line=""
        for word in words:
            new_line+=word+" "
        if new_line=='':
            fout.write('\n')
        else:        
            fout.write(new_line+'\n');
    ftemp.close()

    return fout.getvalue();
#}}}
#}}}

def ssplit_token(infile,outfile):
#{{{
    fin=codecs.open(infile,'r','utf-8')
    ftemp=codecs.open("tempfile",'w','utf-8')
   # fin=open(infile,'r',encoding='utf-8')
   # ftemp=open("tempfile",'w',encoding='utf-8')
    
    #sentence_split
    char_split=['!','?','.','"'] 
    char_end=[' ','\t']
    for line in fin:
        line=line.strip()
        i=0
        while(len(line)!=0):
            if(i==len(line)-1):
                ftemp.write(line[0:i+1]+"\n")
                line=""
                break
            elif (line[i] in char_split) and (line[i+1] in char_end) and (line[i+2].isupper() or not line[i+2].isalpha()): #The punctuation followed by a space and an uppercase will be splilt.
                if(line[i]=='"'):
                    if(line[i-1] in char_split ):
                        ftemp.write(line[0:i+1]+"\n")
                        line=line[i+2:]
                        i=0
                    else:
                        i=i+1
                else:
                    ftemp.write(line[0:i+1]+"\n")
                    line=line[i+2:]
                    i=0
            else:
                i=i+1

        ftemp.write("\n")
    ftemp.close()
    fin.close()
    
    #tokenize4
    infile="tempfile"
    punctuation1=['.','!','?','"']
    punctuation2=[u'•', u'●', u'-', u'—', u':', u';', u'%', u'+', u'=', u'~', u'#',\
                  u'$', u'&', u'*', u'/', u'@', 'u\'\'', u'?', u'!', u'[', u']', u'{', u'}',\
                  u'(', u')', u'<', u'>', u'→', u'↓', u'←', u'↔', u'↑', u'≃', u'⁺', u'···',\
                  u'®', u'≧', u'≈', u'⋅⋅⋅', u'·', u'…', u'...', u'‰', u'€', u'≥', u'∼', u'Δ',\
                  u'≤', u'δ', u'™', u'•', u'∗', u'⩾', u'Σ', u'Φ', u'∑', u'ƒ', u'≡', u'═', u'φ', u'Ψ', u'˙', u'Π', u'≫']
    punctuation3=[',']
    punctuation4=["'"]
    fin=codecs.open(infile,'r','utf-8')
    fout=codecs.open(outfile,'w','utf-8')
   # fin=open(infile,'r',encoding='utf-8')
   # fout=open(outfile,'w',encoding='utf-8')
    number=0
    for line in fin:
    	number+=1
    	if number%500==0:
    	    print number,'.......',
        line=line.strip()
        if line=='':
            fout.write('\n')
        for pun in punctuation2:
            line=line.replace(pun," "+pun+" ")
#         print(line)
        if line!='':    
            if line[-1] in punctuation1:
                line=line[:-1]+" "+line[-1]+" "
        
        new_line=""
        i=0
        
        while(len(line)!=0):
            if(i==len(line)-1): 
                new_line=new_line+line[0:i+1]
                break
            elif line[i] in punctuation3:
                if line[i-1]==' ' or line[i+1]==' ':
                    new_line=new_line+line[:i]+" "+line[i]+" "
                    line=line[i+1:]
                    i=0
                else:
                    i=i+1
            else:
                i=i+1
                
        line=new_line+" "
        new_line=""
        i=0
        while(len(line)!=0): 
            if(i==len(line)-1): 
                new_line=new_line+line[0:i+1]
                break
            elif line[i] in punctuation4:
                if line[i-1]==' ' or line[i+1]==' ':
                    new_line=new_line+line[:i]+" "+line[i]+" "
                    line=line[i+1:]
                    i=0
                elif line[i+1]=='s' and line[i+2]==' ':
                    new_line=new_line+line[:i]+" "+line[i]+"s "
                    line=line[i+2:]
                    i=0
                else:
                    i=i+1
            else:
                i=i+1
                
        words=new_line.split()
       
        for word in words:
            fout.write(word+'\n')
    
    fin.close()
    fout.close()
    
    if os.path.exists('tempfile'):
        os.remove('tempfile')
#}}}

def usage():
    print sys.argv[0]+' -i inputfile -o outputfile'
        
if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "hi:o:")
    inputfile=''
    outputfile=''

    if len(sys.argv)<2:
        usage()
        sys.exit()
    for op, value in opts:
        if op == "-i":
            inputfile = value
        elif op == "-o":
            outputfile = value
        elif op == "-h":
            usage()
            sys.exit()
    ssplit_token(inputfile, outputfile)
