# -*- coding: utf-8 -*-


def read_entity_file(filename):
	entity = []
	count = 0
	for line in open(filename):
		count += 1
		#elem = line.split('|')[2].rpartition('(')[0]
		elem = line.split('|', 3)[2].replace(' ', '-')
		#print elem
		if elem is not None:
			#print '111111111'
			entity.append(str(elem))
		else:
			pass
	return entity

# def read_entity_file(filename):
# 	entity = []
# 	count = 0
# 	for line in open(filename):
# 		count += 1
# 		elem = line.split(' ', 5)[5].replace(' ', '-').strip()
# 		print elem
# 		if elem is not None:
# 			entity.append(str(elem))
# 		else:
# 			pass
# 	return entity

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


def getTypes(filename):
	entity = []
	entity = read_entity_file(filename)
	return entity

if __name__ == '__main__':
	dir = '../files/'
	entity = []
	entity = read_entity_file(dir + 'tempt.indexs')
	print entity
	set_entity = list(set(entity))
	print set_entity

	tag_list = []
	en_list = []
	inst_list = ['false 2 4 docosahexaenoic_acid methylmercury drug drug','false 2 8 docosahexaenoic_acid brain drug phenotype','false 4 8 methylmercury brain drug phenotype','false 6 12 docosahexaenoic_acids methylmercury drug drug']
	for line in inst_list:
		tag_list.append((int(line.split(' ')[1]), int(line.split(' ')[2]), line.split(' ')[3], line.strip().split(' ')[4]))
		en_list.append(str(line.split(' ', 5)[5].replace(' ', '-').strip()))
	print tag_list
	print tag_list[0][1]
	print en_list
