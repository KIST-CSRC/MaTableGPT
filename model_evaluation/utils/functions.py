from collections import defaultdict
import re
import json

def get_keys(d, parent_key='', sep='//'):
    keys = []
    key_list2 = []
    for k, v in d.items():
        new_key = parent_key+sep+k if parent_key else k
        
        if isinstance(v, list):
            if k == 'ref' : 
                new_key = new_key + '****' + str(v)
                keys.append(new_key)
            
            else : 
                keys.append(new_key)
                for i in v : 
                    if type(i) != str and type(i) != float and type(i) != int: 
                        keys.extend(get_keys(i, new_key, sep=sep))
                    else : 
                        new_key = new_key
        if isinstance(v, dict):
            keys.append(new_key)
            keys.extend(get_keys(v, new_key, sep=sep))
        
        if type(v) == str or type(v) == float or type(v) == int: 
            new_key = new_key + '****' + str(v)
            keys.append(new_key)  
    for j in keys : 
        if j.split("//")[0] == "catalysts" or j.split("//")[0] == "catalyst" : 
            j = j.split('//')
            j = "//".join(j[1:])
            key_list2.append(j)
        else : 
            key_list2.append(j)
            
    return key_list2 

def add_indices_to_duplicates(input_list):
    index_dict = defaultdict(list)

    for index, item in enumerate(input_list):
        index_dict[item].append(index)

    output_list = []

    for item, indices in index_dict.items():
        if len(indices) > 1:
            for i, index in enumerate(indices, 1):
                    modified_item = item.replace('//', f'//(index{i})')
                else:
                    modified_item = item
                output_list.append(modified_item)
        else:
            output_list.append(item)

    return output_list

def contains_list(data):
    if isinstance(data, list):
        return True
    if isinstance(data, dict):
        for key, value in data.items():
            if contains_list(value):
                return True
    return False

def get_keys_for_value_accuracy(d, parent_key='', sep='//'):
    keys = []
    key_list2 = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k

        if isinstance(v, list):
            keys.append(new_key)
            for i in v:
                if contains_list(i) == False : 
                    new_list = []
                    value_list = []
                    for performance_property, performance_value in i.items():
                        if performance_property != 'condition' : 
                            if isinstance(performance_value, str):

                                value_list.append(performance_value)

                            elif isinstance(performance_value, dict):
                                for p_p, p_v in performance_value.items():
                                    if isinstance(p_v, str):

                                        value_list.append(p_v)
                                    

                    total_value = '(('+'++'.join(value_list) + '))'
                    
                    new_dict = {}
                    for kkk, vvv in i.items():
                        if isinstance(vvv, str):    
                            new_dict[kkk+total_value] = vvv
                        elif isinstance(vvv, dict):
                            kkk +=total_value
                            new_dict[kkk] = {}

                            for kk, vv in vvv.items():
                                new_dict[kkk][kk+total_value] = vv
                    new_list.append(new_dict)
                    changed_dict = new_dict

                    keys.extend(get_keys_for_value_accuracy(changed_dict, new_key, sep=sep))
                
                if contains_list(i) ==True : #
                    keys.extend(get_keys_for_value_accuracy(i, new_key, sep=sep))


        if isinstance(v, dict):
            keys.append(new_key)
            keys.extend(get_keys_for_value_accuracy(v, new_key, sep=sep))

        if type(v) == str:
            new_key = new_key + '****' + v
            keys.append(new_key)

    for j in keys:
        if j.split("//")[0] == "catalysts" or j.split("//")[0] == "catalyst":
            j = j.split('//')
            j = "//".join(j[1:])
            key_list2.append(j)
        else:
            key_list2.append(j)
    
    return key_list2 

def seperate_key_value(input_list):
    pattern = re.compile(r'\(\((.*?)\)\)')  
    new_list = []
    for item in input_list:
        match = pattern.search(item)
        if match:
            content = match.group(1)
            result = re.sub(pattern, '', item)
            new_list.append([result, content])
        else:
            new_list.append([item])

    return new_list

def remove_whitespace_from_keys(data):
    if isinstance(data, dict):
        return {key.replace(" ", ""): remove_whitespace_from_keys(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [remove_whitespace_from_keys(item) for item in data]
    else:
        return data

def str_val_valset_split(list) : 
    new_list = []
    for item in list:
        a = []
        for i in item :
            substrings = i.split('****')
            a.append(substrings[0])

            if len(substrings) > 1:
                a.extend(substrings[1].split('++'))

        new_list.append(a)
    
    return new_list

def group_by_first_element(list1):
    result = {}
    for sublist in list1:
        key = sublist[0]
        if key in result:
            result[key].append(sublist)
        else:
            result[key] = [sublist]
    return list(result.values())


def finding_pair(list1, list2) : 
    intersection = len(set(list1) & set(list2))
    return intersection


def all_element_int( lst):

    for element in lst:
        if isinstance(element, list):
            if not all_element_int(element):
                return False
        elif not isinstance(element, int):
            return False
    return True

def catalyst_performance(gt_list):
    gt_v = [j for j in gt_list if '****' in j]
    result_list_ = [k for k in gt_v if 'ref' not in k]
    result_list__ = [k for k in result_list_ if 'loading' not in k]
    result_list_ref = [k for k in gt_v if 'ref' in k]
    result_list_loading = [k for k in gt_v if 'loading' in k]
    result_list = []
    for item in result_list__ : 
        a = item.split('//')[:-1]
        b = '//'.join(a)
        result_list.append(b)
    no_dupl = list(set(result_list))
    return no_dupl, result_list_ref, result_list_loading

def count_number(catalyst_list, first, second ) : 
    count_ = []
    for index, cata in enumerate(catalyst_list):
        if first in cata and second in cata[first] and cata[first][second]:
            count_.append(index)
    return count_

def making_new_dict(catalyst_list, first, second, count_lst): 
    new_dict = {}
    new_value = []

    if len(count_lst) > 1 : 
        for value_index in count_lst  : 
            new_value.append(catalyst_list[value_index][first][second])
            
        if any(isinstance(sublist, list) for sublist in new_value) : 
            new_value = [item for sublist in new_value for item in (sublist if isinstance(sublist, list) else [sublist])]
        new_dict.setdefault(first, {})[second] = new_value

    else :
        new_dict = catalyst_list[count_lst[0]]
    return new_dict

def dupl_catalyst(lst) : 
    catalyst = []
    for i in lst : 
        if '//' not in i : 
            catalyst.append(i)
    
    if len(catalyst) != len(list(set(catalyst))) : 
        return True
    
    else : 
        return False     

def merging_result(catalyst_list, lst):
    no_dupl, result_list_ref, result_list_loading = catalyst_performance(lst)
    new_result = []
    for cata_perfo in no_dupl : 
        f_s_lst = cata_perfo.split('//')
        
        if len(f_s_lst)  >1 : 
            first = f_s_lst[0] 
            second = f_s_lst[1] 
            count = count_number(catalyst_list, first, second)
            new_dict = making_new_dict(catalyst_list, first,second, count)
            new_result.append(new_dict)
            
    ref_dict = {}
    loading_dict = {}
    
    for ref in result_list_ref : 

        if '//' in ref : 
            ref_catalyst = ref.split('//')[0]
            reference = str(ref.split('****')[-1])
            ref_dict.setdefault(ref_catalyst, {})['ref'] = reference
            if ref_dict not in new_result : 
                new_result.append(ref_dict)

        else : 
            reference = str(ref.split('****')[-1])
            ref_dict["ref"] = reference
            new_result.append(ref_dict)
            
    for lo in result_list_loading : 
        if '//' in lo : 
            lo_catalyst = lo.split('//')[0]
            loading = str(lo.split('****')[-1])
            loading_dict.setdefault(lo_catalyst, {})["loading"] = loading
            new_result.append(loading_dict)
        else : 
            loading = str(lo.split('****')[-1])
            loading_dict["loading"] = loading
            new_result.append(new_dloading_dictict)
    result_dict = {}
    for item in new_result:
        key = next(iter(item))  
        if key in result_dict:
            result_dict[key].update(item[key])
        else:
            result_dict[key] = item[key]
    result_list = [{key: value} for key, value in result_dict.items()]
    return(result_list)

def flatten_list(nested_list):
    flat_list = []
    for element in nested_list:
        if isinstance(element, list):
            flat_list.extend(flatten_list(element))
        else:
            flat_list.append(element)
    return flat_list
