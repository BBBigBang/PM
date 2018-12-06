#encoding=utf-8
'''
Created on 2017.3.6

@author: Ling Luo
Visualize the final result with html format
'''

import sys,getopt
import codecs 
import StringIO;
def html_visu_nor_fn(infile,omitHeader=True,popOver=True):
#{{{
    """
    use html format to reformat the result 
    @param:
        infile:     python string, the text after normalization 
        omitHeader: bool, whether omit the header of html
        popOver:    bool, whether use boostrap popover plugin
    @return:
        result:     python string, the text can sent to client
    """
#{{{
    fin=StringIO.StringIO(infile);
    fout=StringIO.StringIO();
#    fin=open(infile,'r',encoding='utf-8')
#    fout=open(outfile,'w',encoding='utf-8')
    
    #some tag for html color and popover 
    drugColor='#337ab7">'#<durg>
    diseaseColor='#5cb85c">'#<disease>
    proteinColor='#5bc0de">'#<protein>
    dnaColor='#f0ad4e">'#<dna>
    rnaColor='#d9534f">'#<rna>
    cellColor='#777">'
    phenotypeColor='#fdc086">'
    mutationColor='#ff1493">'
    if popOver: 
        popOverPreTag='<span  data-toggle=\"popover\" \
                data-trigger=\"hover\" data-container=\"body\" \
                data-placement=\"right\" \
                data-content=\"<li class=\'list-group-item\'>\
                <span aria-hidden=\'true\' class=\'glyphicon glyphicon-th-large\'>\
                </span>{type}</li><li class=\'list-group-item\'>\
                <span class=\'glyphicon glyphicon-search\' aria-hidden=\'true\'>\
                </span>{normalization}</li>\" class="label label-'#<durg>
        drug_tag=popOverPreTag+'primary">';
        disease_tag=popOverPreTag+'success">';
        protein_tag=popOverPreTag+'info">';
        dna_tag=popOverPreTag+'warning">';
        rna_tag=popOverPreTag+'danger">';
        cell_tag=popOverPreTag+'default">';
        phenotype_tag=popOverPreTag+'default2">'
        mutation_tag=popOverPreTag+'default3">'
        end_tag='</span>'
    else:
        drug_tag='<font style="background-color: '+drugColor#<durg>
        disease_tag='<font style="background-color: '+diseaseColor#<disease>
        protein_tag='<font style="background-color: '+proteinColor#<protein>
        dna_tag='<font style="background-color: '+dnaColor#<dna>
        rna_tag='<font style="background-color: '+rnaColor#<rna>
        cell_tag='<font style="background-color: '+cellColor
        phenotype_tag='<font style="background-color: '+phenotypeColor
        mutation_tag='<font style="background-color: '+mutationColor
        end_tag='</font>'
    line_tag='<br \>'

    #a aux function for two different color format 
    def formatColor(tag,typeName,normalization):
        if popOver:
            return tag.format(type=typeName,normalization=normalization);
        else:
            return tag;
    
    if not omitHeader:
        fout.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">\n')
        fout.write('<html>\n<head>\n<meta charset="UTF-8">\n    <title>uptodate</title>\n</head>\n')
        fout.write('<body style="font-family: times new roman;font-size:20px">\n');
        fout.write(protein_tag+'Protein'+end_tag+'&emsp;'+dna_tag+'DNA'+end_tag+'&emsp;'+rna_tag+'RNA'+end_tag+'&emsp;'+drug_tag+'Chemical'+end_tag+'&emsp;'+disease_tag+'Disease'+end_tag+'&emsp;'+cell_tag+'Cell'+end_tag+'&emsp;'+phenotype_tag+'Phenotype'+end_tag+'&emsp;'+mutation_tag+'Mutation'+end_tag+'&emsp;'+'\n<br /><br />\n')
    
    new_text=''
    index_start=0
    for line in fin:
        text=line.strip()
        #write text 
        while(line!=''):
            line=next(fin).strip()
            if line!='':
                segs=line.split('\t')
                before_text=text[index_start:int(segs[0])]
                before_text=before_text.replace('<','&lt;').replace('>','&gt;')
                entity_text=text[int(segs[0]):int(segs[1])]
                entity_text=entity_text.replace('<','&lt;').replace('>','&gt;')
                if segs[3]=='drug':
                    new_text=new_text+before_text+formatColor(drug_tag,segs[3],segs[4])+entity_text+end_tag
                elif segs[3]=='disease':
                    new_text=new_text+before_text+formatColor(disease_tag,segs[3],segs[4])+entity_text+end_tag
                elif segs[3]=='protein':
                    new_text=new_text+before_text+formatColor(protein_tag,segs[3],segs[4])+entity_text+end_tag
                elif segs[3]=='dna':
                    new_text=new_text+before_text+formatColor(dna_tag,segs[3],segs[4])+entity_text+end_tag
                elif segs[3]=='rna':
                    new_text=new_text+before_text+formatColor(rna_tag,segs[3],segs[4])+entity_text+end_tag
                elif segs[3]=='cell':
                    new_text=new_text+before_text+formatColor(cell_tag,segs[3],segs[4])+entity_text+end_tag
                elif segs[3]=='phenotype':
                    new_text=new_text+before_text+formatColor(phenotype_tag,segs[3],segs[4])+entity_text+end_tag
                elif segs[3]=='mutation':
                    new_text=new_text+before_text+formatColor(mutation_tag,segs[3],segs[4])+entity_text+end_tag
                index_start=int(segs[1])
        new_text=new_text+text[index_start:]
        fout.write('<div class="Document">\n<div class="aritcle">\n')
        fout.write(new_text+line_tag+'\n')
        #write annotation
        fout.write('\n')
        new_text=''
        index_start=0 
        fout.write('</div>\n</div>\n')
    if not omitHeader:
        fout.write('</body>\n')
        fout.write('</html>\n')
    fin.close()
    return fout.getvalue();
#}}}
#}}}
def html_visu_nor(infile,outfile):
#{{{
    fin=codecs.open(infile,'r','utf-8')
    fout=codecs.open(outfile,'w','utf-8')
#    fin=open(infile,'r',encoding='utf-8')
#    fout=open(outfile,'w',encoding='utf-8')
    
    drug_tag='<font style="background-color: rgb(171,221,164)">'#<durg>
    disease_tag='<font style="background-color: rgb(0,208,255)">'#<disease>
    protein_tag='<font style="background-color: rgb(215,25,28)">'#<protein>
    dna_tag='<font style="background-color: rgb(253,174,97)">'#<dna>
    rna_tag='<font style="background-color: rgb(255,255,191)">'#<rna>
    dict_tag='<font style="background-color: rgb(155,155,191)">'
    end_tag='</font>'
    line_tag='<br \>'
    
    fout.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">\n')
    fout.write('<html>\n<head>\n<meta charset="UTF-8">\n    <title>uptodate</title>\n</head>\n<body style="font-family: Times New Roman;font-size:20px">\n')
    fout.write(protein_tag+'Protein'+end_tag+'&emsp;'+dna_tag+'DNA'+end_tag+'&emsp;'+rna_tag+'RNA'+end_tag+'&emsp;'+drug_tag+'Chemical'+end_tag+'&emsp;'+disease_tag+'Disease'+end_tag+'&emsp;'+dict_tag+'DICT'+end_tag+'&emsp;'+'\n<br /><br />\n')
    
    new_text=''
    index_start=0
    for line in fin:
        text=line.strip()
        entity_line=[]
        while(line!=''):
            line=next(fin).strip()
            if line!='':
                entity_line.append(line)
                segs=line.split('\t')
                before_text=text[index_start:int(segs[0])]
                before_text=before_text.replace('<','&lt;').replace('>','&gt;')
                entity_text=text[int(segs[0]):int(segs[1])]
                entity_text=entity_text.replace('<','&lt;').replace('>','&gt;')
                if segs[3]=='drug':
                    new_text=new_text+before_text+drug_tag+entity_text+end_tag
                elif segs[3]=='disease':
                    new_text=new_text+before_text+disease_tag+entity_text+end_tag
                elif segs[3]=='protein':
                    new_text=new_text+before_text+protein_tag+entity_text+end_tag
                elif segs[3]=='dna':
                    new_text=new_text+before_text+dna_tag+entity_text+end_tag
                elif segs[3]=='rna':
                    new_text=new_text+before_text+rna_tag+entity_text+end_tag
                elif segs[3]=='dict':
                    new_text=new_text+before_text+dict_tag+entity_text+end_tag
                index_start=int(segs[1])
        new_text=new_text+text[index_start:]
        fout.write('<text>\n')
        fout.write(new_text+line_tag+'\n')
        fout.write('</text>\n')
        fout.write('<annotation>\n')
        for ele in entity_line:
            ele=ele.replace('\t','&emsp;')
            fout.write(ele+line_tag+'\n')
      #  fout.write(line_tag+'\n')
        fout.write('</annotation>\n')
        fout.write(line_tag+'\n')
        new_text=''
        index_start=0
    fout.write('</body>\n</html>')
    fin.close()
    fout.close()
#}}}
def usage():
    print sys.argv[0]+' -i infile -o outfile'

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "hi:o:")
    infile=''
    outfile=''

    if len(sys.argv)<3:
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
    html_visu_nor(infile,outfile)

