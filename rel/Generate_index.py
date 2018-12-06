# -*- coding: utf-8 -*-

import codecs as cs

def read_index_file(filename):
	index = []
	count = 0
	for line in open(filename):
		count += 1
		elem = line.split(' ')[0].rpartition('(')[0]
		if elem == 'true':
			index.append(str(count))
		else:
			pass
	return index

def write_index_file(filename, content):
	fp = cs.open(filename, 'w')
	count = 0
	for elem in content:
		count += 1
		if count != len(content):
			fp.writelines(elem)
			fp.writelines('\n')
		else:
			fp.writelines(elem)
	fp.close()

def generate_indexFile():
	dir = '../files/'
	index = []
	index = read_index_file(dir + 'ADE.indexs')
	write_index_file(dir + 'train0.t', index)
	print 'Index file has been created...'

if __name__ == '__main__':

	dir = '../files/'

	index = []
	index = read_index_file(dir + 'DDI.indexs')

	write_index_file(dir + 'train0.t', index)