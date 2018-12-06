# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 16:18:09 2018

@author: SYW
"""
import sys,getopt
import os

def cus_rmdir(path):
    if len(os.listdir(path)):
        for sub_name in os.listdir(path):
            print(sub_name)
            sub_path=os.path.join(path,sub_name)
            if os.path.isfile(sub_path):
                os.remove(sub_path)
            else:
                cus_rmdir(sub_path)

def usage():
    print(sys.argv[0]+' -i inputfile -o outputfile')


if __name__=="__main__":
    opts,args=getopt.getopt(sys.argv[1:],"hi:o:")
    infile=''
    outfile=''
    if not os.path.exists('temp'):
        os.makedirs('temp')
    if len(sys.argv)<2:
        usage()
        sys.exit()
    for op,value in opts:
        if op=="-i":
            infile=value
        elif op=="-o":
            outfile=value
        elif op=="-h":
            usage()
            sys.exit()
    
#need 3 dir named 'Gin_data', 'Gout_data', 'TMout_data' respectively,and they have to be cleaned before running all follow steps.
#1:clean
    print('#############################')
    print('step 1: now clean all files in three dirs')
    print('#############################')
    cus_rmdir('./MR_tmVarSoftware/Gin_data')
    cus_rmdir('./MR_tmVarSoftware/Gout_data')
    cus_rmdir('./MR_tmVarSoftware/TMout_data')
    #os.remove(outfile)
    print('step 1:now clean..........\n')
    print('clean done\n\n')  
#2:preprocess
    print('#############################')
    print('step 2: now preprocess the tobe-processed input data into pubtator format')
    print('#############################')
    print(infile)
    command='python s2Gi.py -i '+ infile +' -o ./MR_tmVarSoftware/Gin_data/temp.txt'
    print('step 2:now preprocess:\n'+command+'..........')
    os.system(command)
    print('preprocess done\n\n')
    
#3:GnormPlus to get gene
    print('##################################')
    print('step 3: now GnormPlus to get gene')
    print('###################################')
    command='cd ./MR_tmVarSoftware/GNormPlusJava && java -Xmx10G -Xms10G -jar GNormPlus.jar ../Gin_data ../Gout_data setup.txt'
    print('step 3:now GNormPlus\n'+command+'..............')
    os.system(command)
    print('GNormPlus done')
    
#4:tmVar to normalize
    print('##################################')
    print('step 4: now tmVar to normalize')
    print('###################################')
    command='cd ./MR_tmVarSoftware/tmVarJava && java -Xmx5G -Xms5G -jar tmVar.jar ../Gout_data ../TMout_data'
#    command='java -Xmx5G -Xms5G -jar tmVarJava/tmVar.jar Gin_data TMout_data'#不执行第三步，直接执行第四步，输入为Gin_data中的文件，结果为不标准化
    print('step 4:now tmVar\n'+command+'..............')
    os.system(command)
    print('tmVar done')
#5:post-process
    print('##################################')
    print('step 5: now post-process the tmVar output into final output')
    print('###################################')
    command='python tmVaro2fo.py -i ./MR_tmVarSoftware/TMout_data/temp.txt.PubTator -o '+ outfile
    print('step 5:now post-precess'+command+'..............')
    os.system(command)
    print('post-precess done')
    
