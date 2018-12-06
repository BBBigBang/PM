import numpy


def get_true_insts(insts_offset_list, answer_array_test, filtered_index, threshold=0.5):
    
    '''
        filtered_index contains the indexs of instances whose lengths are longer
        than the max_sent_len and be removed before
    '''
    assert len(insts_offset_list) == len(answer_array_test) + len(filtered_index)
    rest_insts_offset = []
    for i in range(len(insts_offset_list)):
        if i not in filtered_index:
            rest_insts_offset.append(insts_offset_list[i])
    
    
    assert len(rest_insts_offset) == len(answer_array_test)
    true_inst_list = []
    index = 0
    for elem in answer_array_test[:,0]:
        if elem > threshold:
            true_inst_list.append(rest_insts_offset[index] + '|' + str(elem))
        index += 1 
    
    return true_inst_list   