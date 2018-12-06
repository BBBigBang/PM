#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
# *************************************************
# > File Name: test.py
# > Author: yang 
# > Mail: yangperasd@163.com 
# > Created Time: Sun 19 Nov 2017 06:48:11 PM CST
# *************************************************
import time;
from joblib import Parallel, delayed
import multiprocessing as mp
    
# what are your inputs, and what operation do you want to 
# perform on each input. For example...
startTime=time.time();
inputs = range(999999) 
def processInput(i):
    return i*i;

num_cores = mp.cpu_count()
print(num_cores);
    
#results = Parallel(n_jobs=num_cores)(delayed(processInput)(i) for i in range(1000,40000))
#pool=mp.Pool(processes=4);
#results=pool.map(processInput,inputs)
#result=[];
for i in inputs:
    processInput(i);
    #result.append(i*i)
print("over {}s".format(time.time()-startTime));
