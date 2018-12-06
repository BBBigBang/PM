# -*- coding: utf-8 -*-

import json
import re
import random
import types

# re_obj = re.compile(r'.*?<strong>(.*?)</strong>.*?')

entityObj = re.compile(r'.*?<.*?color="green"><strong>(.*?)</strong></font>.*?')
modObj = re.compile(r'.*?<.*?color="blue"><strong>(.*?)</strong></font>.*?')
relationObj = re.compile(r'.*?<.*?color="red"><strong>(.*?)</strong></font>.*?')

key_obj = re.compile(r'.*?<.*?color="red"><strong>(.*?)</strong></font>.*?')
position = ['top-left', 'top-center', 'top-right', 'center-left', \
			'center-right', 'bottom-left', 'bottom-center', 'bottom-right']


def get_keywords(key, sent):
    key.sort()
    # str_key = key_obj.match(sent[key[0]])
    str_key = sent[key[0]].replace('<font color="red"><strong>','').\
    		replace('</strong></font>','')

    # if str_key:
    #     str_str = key_obj.match(sent[key[0]]).groups(0)
    #     str_key = str_str[0].strip('<font color="red"><strong>').strip('</strong></font>')
    # else:
    #     str_key = sent[key[0]].strip('<font color="red"><strong>').strip('</strong></font>')
    
    if len(key) > 1:
        for k in range(1, len(key)):
            # cur_str = key_obj.match(sent[key[k]])
            str_key = str_key + '_' + \
            	str(sent[key[k]].replace('<font color="red"><strong>','').replace('</strong></font>',''))
            # if cur_str:
            #     cur_cur = key_obj.match(sent[key[k]]).groups(0)
            #     cur_key = cur_cur[0].strip('<font color="green"><strong>').strip('</strong></font>')
            #     str_key = str_key + '_' + cur_key
            # else:
            #     str_key = str_key + '_' + str(sent[key[k]]).strip('<font color="green"><strong>').strip('</strong></font>')
                
    return str_key

def jsonEntity(inst, entity_type, i, nodes_list, re_id, entity_list, entity_id_list, concept_id):
	
	if inst[2 + i] in entity_list:
		for num in range(len(nodes_list)):
			if inst[2 + i] == nodes_list[num]['data']['name']:
				re_id[i] = int(nodes_list[num]['data']['id'])

	elif concept_id in entity_id_list:
		if concept_id == 'undetermined':
			entity = {}
			entity["id"] = len(nodes_list) + 1
			entity["name"] = inst[2 + i]
			entity_list.append(inst[2 + i])
			entity["type"] = entity_type.split('-')[0 + i]
			entity["score"] = 1
			entity["NMID"] = concept_id
			entity_id_list.append(concept_id)

			Bigentity = {}
			Bigentity["data"] = entity

			pos = random.randint(0, (len(position)-1))
			Bigentity["classes"] = position[pos]
			nodes_list.append(Bigentity)
		else:
			for num in range(len(nodes_list)):
				if concept_id == nodes_list[num]['data']['NMID']:
					re_id[i] = int(nodes_list[num]['data']['id'])

	else:
		entity = {}
		entity["id"] = len(nodes_list) + 1
		entity["name"] = inst[2 + i]
		entity_list.append(inst[2 + i])
		entity["type"] = entity_type.split('-')[0 + i]
		entity["score"] = 1
		entity["NMID"] = concept_id
		entity_id_list.append(concept_id)

		Bigentity = {}
		Bigentity["data"] = entity

		pos = random.randint(0, (len(position)-1))
		Bigentity["classes"] = position[pos]
		nodes_list.append(Bigentity)

def jsonRelation(key, sent, nodes_list, edge_list, re_id, sentence_score, relation_list):
	relation = {}
	if re_id[0] != 0 and re_id[1] == 0:
		relation["source"] = re_id[0]
		relation["target"] = len(nodes_list)
		re_id = [0, 0]

	elif re_id[1] != 0 and re_id[0] == 0:
		relation["source"] = len(nodes_list)
		relation["target"] = re_id[1]
		re_id = [0, 0]

	elif re_id[0] != 0 and re_id[1] != 0:
		if (re_id[0], re_id[1]) in relation_list or (re_id[1], re_id[0]) in relation_list:
			re_id = [0, 0]
			return 
		else:
			relation["source"] = re_id[0]
			relation["target"] = re_id[1]
			re_id = [0, 0]
			relation_list.append((re_id[0], re_id[1]))
			relation_list.append((re_id[1], re_id[0]))
			return

	else:
		relation["source"] = len(nodes_list) - 1
		relation["target"] = len(nodes_list)
		re_id = [0, 0]

	key.sort()
	str_key = key_obj.match(sent[key[0]])
	if str_key:
		str_str = key_obj.match(sent[key[0]]).groups(0)
		str_key = str_str[0].replace('<font color="green"><strong>','').replace('</strong></font>','').replace('<font color="red"><strong>', '')
	else:
		str_key = sent[key[0]].replace('<font color="green"><strong>','').replace('</strong></font>','').replace('<font color="red"><strong>', '')
	
	if len(key) > 1:
		for k in range(1, len(key)):
			cur_str = key_obj.match(sent[key[k]])
			if cur_str:
				cur_cur = key_obj.match(sent[key[k]]).groups(0)
				cur_key = cur_cur[0].replace('<font color="green"><strong>','').replace('</strong></font>','').replace('<font color="red"><strong>', '')
				str_key = str_key + '_' + cur_key
			else:
				str_key = str_key + '_' + str(sent[key[k]])
	str_key = str_key.replace('<font color="green"><strong>','').replace('</strong></font>','').replace('<font color="red"><strong>', '')
	relation["type"] = str_key
	
	sentence_str = ''

	sent2 = sent[1:]
	for elem in sent2:
		tag1 = entityObj.match(elem)
		tag2 = modObj.match(elem)
		tag3 = relationObj.match(elem)
		if tag1:
			cur_elem = elem.replace('color="green"', 'color="red"').replace('<', '<').replace('>', '>').strip()
			sentence_str = sentence_str + ' ' + cur_elem
		elif tag2:
			cur = modObj.match(elem).groups(0)
			cur_elem = cur[0].strip()
			sentence_str = sentence_str + ' ' + cur_elem
		elif tag3:
			cur_elem = elem.replace('color="red"', 'color="green"').replace('<', '<').replace('>', '>').strip()
			sentence_str = sentence_str + ' ' + cur_elem
		else:
			sentence_str = sentence_str + ' ' + elem.strip()
	sentence_str = sentence_str.split('|')[0].strip('\t').strip('\n').strip()
	sentence_str += ' <BR>'
	sentence_str.replace('\\', '&#92;').replace('_', ' ').\
				replace('( ', '(').replace(' )', ')').\
				replace(' ,', ',').replace(' .', '.').\
				replace(' ?', '?').replace(' :', ':').strip('\t')
	relation["sentence"] = []
	relation["sentence"].append(sentence_str)

	# str_key2 = re_obj.match(sent[1])
	# if str_key2:
	# 	str_str2 = re_obj.match(sent[1]).groups(0)
	# 	str_sent = str_str2[0]
	# else:
	# 	str_sent = sent[1]

	# for s in range(2, len(sent)):
	# 	cur_str = re_obj.match(sent[s])
	# 	if cur_str:
	# 		cur_cur = re_obj.match(sent[s]).groups(0)
	# 		cur_key = cur_cur[0]
	# 		str_sent = str_sent + '_' + cur_key
	# 	else:
	# 		str_sent = str_sent + ' ' + sent[s]
	# str_sent2 = str_sent.split('|')[0].replace('_', ' ').replace('( ', '(').\
	# 	replace(' )', ')').replace(' ,', ',').replace(' .', '.').\
	# 	replace(' ?', '?').replace(' :', ':').strip('\t')

	# str_sent3 = tag_entity(str_sent2, nodes_list, int(relation["source"]), int(relation["target"]))
	# str_sent3 = str_sent3 + ' <BR>'
	# str_sent3.strip()
	# relation["sentence"] = []
	# relation["sentence"].append(str_sent3)

	# real_key = ''
	# str_key = str_sent.split('|')[0].split(' ')
	# print str_key
	# for elem in str_key:
	# 	cur_key2 = key_obj.match(elem)
	# 	if cur_key2:
	# 		temp = key_obj.match(elem).groups(0)
	# 		temp_key = temp[0]
	# 		real_key = real_key + '_' + str(temp_key)
	# 	else:
	# 		continue
	# real_key.strip('_')
	# relation["type"] = real_key
	
	relation["score"] = sentence_score

	flag = 0

	for index in range(len(edge_list)):
		if (int(relation["source"]) == int(edge_list[index]["data"]["source"])) and \
			(int(relation["target"]) == int(edge_list[index]["data"]["target"])):
			flag = 1
			if relation["score"] > edge_list[index]["data"]["score"]:
				# replace
				edge_list[index]["data"]["score"] = relation["score"]
				edge_list[index]["data"]["type"] = relation["type"]
				edge_list[index]["data"]["sentence"].append(relation["sentence"][0])
				# edge_list[index]["data"]["sentence"] = relation["sentence"]
			else:
				edge_list[index]["data"]["sentence"].append(relation["sentence"][0])

		elif (int(relation["source"]) == int(edge_list[index]["data"]["target"])) and \
			(int(relation["target"]) == int(edge_list[index]["data"]["source"])):
			flag = 1
			if relation["score"] > edge_list[index]["data"]["score"]:
				# replace
				edge_list[index]["data"]["score"] = relation["score"]
				edge_list[index]["data"]["type"] = relation["type"]
				edge_list[index]["data"]["sentence"].append(relation["sentence"][0])
				# edge_list[index]["data"]["sentence"] = relation["sentence"]
			else:
				edge_list[index]["data"]["sentence"].append(relation["sentence"][0])
		else:
			continue

	if flag == 0:
		Bigrelation = {}
		Bigrelation["data"] = relation
		edge_list.append(Bigrelation)
	else:
		pass

# def tag_entity(sentence, nodes_list, e1_id, e2_id):
	
# 	e1_name = []
# 	e2_name = []
# 	e1_name = nodes_list[e1_id-1]["data"]["name"].strip().replace('_', ' ').split(' ')
# 	e2_name = nodes_list[e2_id-1]["data"]["name"].strip().replace('_', ' ').split(' ')
# 	# processing...
# 	sentence_list = sentence.split(' ')
# 	for i in range(len(sentence_list)):
# 		if len(e1_name) == 1:
# 			if sentence_list[i].replace('(','').replace(')','').replace(',','').replace('.','').strip() == e1_name[0]:
# 				sentence_list[i] = "<font color='red'>" + str(sentence_list[i]) + "<&#47;font>"
# 				#sentence_list[i] = "<font color='red'>" + str(sentence_list[i]) + "</font>"
# 			else:
# 				pass
# 		elif len(e1_name) > 1:
# 			if sentence_list[i].replace('(','').replace(')','').replace(',','').replace('.','').strip() == e1_name[0] \
# 				and sentence_list[i+1].replace('(','').replace(')','').replace(',','').replace('.','').strip() == e1_name[1]:
# 				for j in range(len(e1_name)):
# 					sentence_list[i + j] = "<font color='red'>" + str(sentence_list[i+j]) + "<&#47;font>"
# 					#sentence_list[i + j] = "<font color='red'>" + str(sentence_list[i+j]) + "</font>"
# 			else:
# 				pass
# 		else:
# 			continue
# 	for i in range(len(sentence_list)):
# 		if len(e2_name) == 1:
# 			if sentence_list[i].replace('(','').replace(')','').replace(',','').replace('.','').strip() == e2_name[0]:
# 				sentence_list[i] = "<font color='red'>" + str(sentence_list[i]) + "<&#47;font>"
# 				#sentence_list[i] = "<font color='red'>" + str(sentence_list[i]) + "</font>"
# 			else:
# 				pass
# 		elif len(e2_name) > 1:
# 			if sentence_list[i].replace('(','').replace(')','').replace(',','').replace('.','').strip() == e2_name[0] \
# 				and sentence_list[i+1].replace('(','').replace(')','').replace(',','').replace('.','').strip() == e2_name[1]:
# 				for j in range(len(e2_name)):
# 					sentence_list[i + j] = "<font color='red'>" + str(sentence_list[i+j]) + "<&#47;font>"
# 					#sentence_list[i + j] = "<font color='red'>" + str(sentence_list[i+j]) + "</font>"
# 			else:
# 				pass
# 		else:
# 			continue
# 	sentence2 = ""
# 	for i in range(len(sentence_list)):
# 		sentence2 = sentence2 + ' ' + sentence_list[i]
# 	return sentence2


def gen_jsonData(inst, entity_type, sent, key, nodes_list, edge_list, sentence_score, entity_list, entity_id_list, concept_ids, relation_list):
	re_id = [0, 0]

	Nmid = concept_ids.split(' ')
	concept_id = [Nmid[0], Nmid[1]]

	for i in range(2):
		jsonEntity(inst, entity_type, i, nodes_list, re_id, entity_list, entity_id_list, concept_id[i])

	jsonRelation(key, sent, nodes_list, edge_list, re_id, sentence_score, relation_list)


def generate_JSONfile(nodes_list, edge_list):
	json_data = {}
	json_data['nodes'] = nodes_list
	json_data['edges'] = edge_list
	return json_data

def writeJson(fileName, json_data):
	json_str = json.dumps(json_data, sort_keys=False, indent=2)
	writeObj = open(fileName, 'w')
	writeObj.write(json_str)
	writeObj.close()

def loadJson(fileName):
	f = open(fileName, encoding = 'utf-8')
	data = json.load(f)
	nodes_data = data['nodes']

	return nodes_data

if __name__ == '__main__':

	nodes_data = loadJson('C:/Users/Administrator/Desktop/liver_data.json')
	print(nodes_data)

	for nodes_elem in nodes_data:
		pos = random.randint(0, (len(position)-1))
		nodes_elem['data'].setdefault('class', position[pos])
		print nodes_elem
