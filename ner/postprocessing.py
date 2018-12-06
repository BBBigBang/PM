#encoding=utf-8
'''
Created on 2017��12��18��

@author: lingluo
'''
import codecs as cs
import StringIO
#后处理，统一识别多于两次的实体，对于类型不统一的实体，统一实体类型。
def postprocessing_fn(infile):
    fin=StringIO.StringIO(infile)
    fout=StringIO.StringIO()

    
    for line in fin:
        text=line.strip()
	#print text
        fout.write(text+'\n')
        line=next(fin).strip()
        dict_entity={} #dict[entiy]=type1|num1|type2|num2
        dict_line={} #dict[line_nums]=line
#         list_line=[] #[line_nums]
        while(line!=''):
	    #print line
            segs=line.split('\t')
            #produce dict_entity
            if segs[2].lower() in dict_entity.keys():
                keyvalue=dict_entity[segs[2].lower()]
                key_seg=keyvalue.split('|')
                flag=0
                for i in range(len(key_seg)):
                    if segs[3]==key_seg[i]:
                        key_seg[i+1]=str(int(key_seg[i+1])+1)
                        flag=1
                        break
                if flag==0:
                    dict_entity[segs[2].lower()]+='|'+segs[3]+'|1'
                else:
                    new_value=''
                    for i in range(len(key_seg)):
                        new_value+=key_seg[i]+'|'
                    dict_entity[segs[2].lower()]=new_value[0:-1]  

            else:
                dict_entity[segs[2].lower()]=segs[3]+'|1'
            
            dict_line[int(segs[0])]=line
#             list_line.append(segs[0])
            line=next(fin).strip()
        #统一实体类型
        for key in dict_entity.keys():
            segs=dict_entity[key].split('|')
            max_type=segs[0]
            max_num=int(segs[1])
            i=2
            while i< len(segs):
                if int(segs[i+1])>max_num:
                    max_type=segs[i]
                    max_num=int(segs[i+1])
                i+=2
            dict_entity[key]=max_type

        for key in dict_line.keys():
            segs=dict_line[key].split('\t')
            if segs[3]!=dict_entity[segs[2].lower()]:
                dict_line[key]=segs[0]+'\t'+segs[1]+'\t'+segs[2]+'\t'+dict_entity[segs[2].lower()]        
        
        #write
        #punctuation2=['-',':',';','%','+','=','~','#','$','&','*','/','@','"','?','!','[',']','{','}','(',')','.',',',' ']
        punctuation2=[',',' ','.','-',':',';','%','+','=','~','#','$','&','*','/','@',\
                  '"','?','!','[',']','{','}','(',')','<','>',\
                  '→','⁺','···','®','≧','≈','⋅⋅⋅','·','…','‰','€','≥',\
                  'Δ','≤','δ','™','•','∗','⩾','Σ','Φ','∑','ƒ','≡','═','φ','Ψ','˙','Π','≫']
	for key in dict_entity.keys():
            index_s=[]
            index=text.lower().find(key,0)
            while index!=-1:
                index_s.append(index)
                index=text.lower().find(key,index+len(key))

            for index in index_s:
                if index not in dict_line.keys():
                    
                    if index-1>=0 and index+len(key)<len(text):
                        if (text[index-1] in punctuation2) and (text[index+len(key)] in punctuation2): 
                            dict_line[index]=str(index)+'\t'+str(index+len(key))+'\t'+text[index:index+len(key)]+'\t'+dict_entity[key]
                    elif index==0 and index+len(key)<len(text):
                        if text[index+len(key)] in punctuation2: 
                            dict_line[index]=str(index)+'\t'+str(index+len(key))+'\t'+text[index:index+len(key)]+'\t'+dict_entity[key]
                    elif index-1>=0 and index+len(key)==len(text):
                        if text[index-1] in punctuation2 : 
                            dict_line[index]=str(index)+'\t'+str(index+len(key))+'\t'+text[index:index+len(key)]+'\t'+dict_entity[key]
                        
        #排序后是一个列表
        dict_line=sorted(dict_line.items(),key=lambda asd:asd[0],reverse=False)
        #print 'post:'
	dict_line_new=[]
        if len(dict_line)>0:
	    #print dict_line[0][1]+'\n'
	    dict_line_new.append(dict_line[0])
            #fout.write(dict_line[0][1]+'\n')
	j=0
        for i in range(1,len(dict_line)-1):
            segs_before=dict_line_new[j][1].split('\t')
            segs=dict_line[i][1].split('\t')
            segs_next=dict_line[i+1][1].split('\t')
            if int(segs[0])>int(segs_before[1]):
                if int(segs[1])>=int(segs_next[1]):
		    #print dict_line[i][1],i
		    dict_line_new.append(dict_line[i])
                    j+=1
                    #fout.write(dict_line[i][1]+'\n')
                elif int(segs[1])<=dict_line[i+1][0]:
		    #print dict_line[i][1],i
		    dict_line_new.append(dict_line[i])
		    j+=1
                    #fout.write(dict_line[i][1]+'\n')
        if len(dict_line)>=2:            
            segs_before=dict_line_new[j][1].split('\t')
            segs=dict_line[len(dict_line)-1][1].split('\t')
            if int(segs[0])>int(segs_before[1]):
		#print dict_line[len(dict_line)-1][1]+'\n'
		dict_line_new.append((dict_line[len(dict_line)-1]))
                #fout.write(dict_line[len(dict_line)-1][1]+'\n')
        for i in range(len(dict_line_new)):
	    #print dict_line_new[i][1]
	    fout.write(dict_line_new[i][1]+'\n')
        fout.write('\n')
    fin.close()
    return fout.getvalue()    
                    
                
                
            
    
if __name__ == '__main__':
    infile='C:/Users/Administrator/Desktop/pm_dict/input.token.combine_tsv'
    outfile='C:/Users/Administrator/Desktop/pm_dict/input.token.post'
    postprocessing(infile,outfile)


