import json
import os
import random
import re
import unicodedata
from utils.functions import *

class evaluation : 
    def __init__(self, prediction_path, groundTruth_path) :
        self.prediction_path = prediction_path
        self.groundTruth_path = groundTruth_path
        
        
    def remove_whitespace_from_keys(self, data):
        '''
        remove whitespace from keys
        '''
        if isinstance(data, dict):
            data = {key.replace("_", ""): self.remove_whitespace_from_keys(value) for key, value in data.items()}
        if isinstance(data, dict):
            return {key.replace(" ", ""): self.remove_whitespace_from_keys(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.remove_whitespace_from_keys(item) for item in data]
        else:
            return data
        
    def remove_unicode(self, text):
        '''
        remove unicode
        '''
    
        return ''.join(char for char in unicodedata.normalize('NFKD', text) if not unicodedata.combining(char))


    def remove_unicode_version(self,data) : 
        processed_data = {}
        for key, value in data.items():
            key = self.remove_unicode(key)
            if isinstance(value, str):
                processed_data[key] = self.remove_unicode(value)
            else:
                processed_data[key] = value

        return processed_data
    
    def unicode_to_str(self, match):
        unicode_str = match.group()
        return bytes(unicode_str, 'utf-8').decode('unicode_escape') 
    
    def load_data(self) :
        '''
        load prediction and ground truth
        '''
        with open(self.prediction_path, 'r', encoding='utf-8-sig') as file:
            prediction = json.load(file) 
        
        with open(self.groundTruth_path, 'r', encoding='utf-8-sig') as file:
            ground_truth = json.load(file)  

        prediction = json.dumps(prediction, ensure_ascii=False)

        cleaned_string = re.sub(r'–', '-', prediction)
        cleaned_string = re.sub(r'−', '-', cleaned_string)
        cleaned_string = re.sub(r'<sup>', '', cleaned_string)
        cleaned_string = re.sub(r'</sup>', '', cleaned_string)
        cleaned_string = re.sub(r'\\u[0-9a-fA-F]{4}', self.unicode_to_str, cleaned_string)
        cleaned_string = re.sub(r'�', '±', cleaned_string)
        cleaned_string = re.sub(r'm2 g−1', 'm2/g', cleaned_string)
        cleaned_string = re.sub(r'μF cm−2', 'μF/cm2', cleaned_string)
        cleaned_string = re.sub(r'mA mg−2', 'mA/mg2', cleaned_string)
        cleaned_string = re.sub(r'mA mg−1', 'mA/mg', cleaned_string)
        cleaned_string = re.sub(r'mA cm−2', 'mA/cm2', cleaned_string)
        cleaned_string = re.sub(r'ohm', 'ω', cleaned_string)
        cleaned_string = re.sub(r'~', '∼', cleaned_string)
        cleaned_string = re.sub(r'</potential>', '', cleaned_string)
        cleaned_string = re.sub(r'²', '2', cleaned_string)
        cleaned_string = re.sub(r'\u2005', ' ', cleaned_string)
        cleaned_string = re.sub(r'\u2006', ' ', cleaned_string)
        cleaned_string = re.sub(r'\u2009', ' ', cleaned_string)
        cleaned_string = re.sub(r'\u200b', ' ', cleaned_string)
        cleaned_string = re.sub(r'\u202f', ' ', cleaned_string)
        cleaned_string = re.sub(r'\u200e', ' ', cleaned_string)
        cleaned_string = re.sub(r'0\s+0', '0,0', cleaned_string)
        cleaned_string = re.sub(r'(\d+)∼(\d+)', r'\1-\2', cleaned_string)
        cleaned_string = re.sub(r' ', '', cleaned_string)
        cleaned_string = re.sub(r'·', '', cleaned_string)
        cleaned_string = re.sub(r'fcm−2', 'f/cm2', cleaned_string)
        cleaned_string = cleaned_string.lower()
        cleaned_string = re.sub(r'jecsa', 'ecsa', cleaned_string)
        cleaned_string = re.sub(r'j-ecsa', 'ecsa', cleaned_string)
        cleaned_string = re.sub(r'ag-1', 'a/g', cleaned_string)
        cleaned_string = re.sub(r'ours', 'thiswork', cleaned_string)
        cleaned_string = re.sub(r'0\.m', '0m', cleaned_string)
        cleaned_string = re.sub(r';', '', cleaned_string)
        cleaned_string = re.sub(r'\.$', '', cleaned_string)
        prediction = json.loads(cleaned_string)
        
        ground_truth = json.dumps(ground_truth, ensure_ascii=False)
        cleaned_string = re.sub(r'–', '-', ground_truth)
        cleaned_string = re.sub(r'−', '-', cleaned_string)
        cleaned_string = re.sub(r'<sup>', '', cleaned_string)
        cleaned_string = re.sub(r'</sup>', '', cleaned_string)
        cleaned_string = re.sub(r'\\u[0-9a-fA-F]{4}', self.unicode_to_str, cleaned_string)
        cleaned_string = re.sub(r'�', '±', cleaned_string)
        cleaned_string = re.sub(r'm2 g−1', 'm2/g', cleaned_string)
        cleaned_string = re.sub(r'μF cm−2', 'μF/cm2', cleaned_string)
        cleaned_string = re.sub(r'mA mg−2', 'mA/mg2', cleaned_string)
        cleaned_string = re.sub(r'mA mg−1', 'mA/mg', cleaned_string)
        cleaned_string = re.sub(r'mA cm−2', 'mA/cm2', cleaned_string)
        cleaned_string = re.sub(r'ohm', 'ω', cleaned_string)
        cleaned_string = re.sub(r'~', '∼', cleaned_string)
        cleaned_string = re.sub(r'²', '2', cleaned_string)
        cleaned_string = re.sub(r'\u2005', ' ', cleaned_string)
        cleaned_string = re.sub(r'\u2006', ' ', cleaned_string)
        cleaned_string = re.sub(r'\u2009', ' ', cleaned_string)
        cleaned_string = re.sub(r'\u200b', ' ', cleaned_string)
        cleaned_string = re.sub(r'\u202f', ' ', cleaned_string)
        cleaned_string = re.sub(r'\u200e', ' ', cleaned_string)
        cleaned_string = re.sub(r'0\s+0', '0,0', cleaned_string)
        cleaned_string = re.sub(r'(\d+)∼(\d+)', r'\1-\2', cleaned_string)
        cleaned_string = re.sub(r' ', '', cleaned_string)
        cleaned_string = re.sub(r'·', '', cleaned_string)
        cleaned_string = re.sub(r'fcm−2', 'f/cm2', cleaned_string)
        cleaned_string = cleaned_string.lower()
        cleaned_string = re.sub(r'jecsa', 'ecsa', cleaned_string)
        cleaned_string = re.sub(r'j-ecsa', 'ecsa', cleaned_string)
        cleaned_string = re.sub(r'ag-1', 'a/g', cleaned_string)
        cleaned_string = re.sub(r'ours', 'thiswork', cleaned_string)
        cleaned_string = re.sub(r'0\.m', '0m', cleaned_string)
        cleaned_string = re.sub(r';', '', cleaned_string)
        cleaned_string = re.sub(r'\.$', '', cleaned_string)

        ground_truth = json.loads(cleaned_string)
        prediction = self.remove_unicode_version(prediction)
        ground_truth = self.remove_unicode_version(ground_truth)
        
        prediction = self.remove_whitespace_from_keys(prediction)
        ground_truth = self.remove_whitespace_from_keys(ground_truth)

        return prediction, ground_truth
    
    def get_key_list_with_value(self) :
        '''
        return list that contain key, value sets
        '''
        prediction, ground_truth = self.load_data()
        pr_list = get_keys(prediction, parent_key = '', sep = '//') 
        gt_list = get_keys(ground_truth, parent_key = '', sep = '//')

        return pr_list, gt_list
    
    def merging(self) : 
        '''
        combine dict that have same catalyst name
        '''
        pr_list, gt_list = self.get_key_list_with_value()
        prediction, ground_truth = self.load_data()
        first_key_value_p = prediction[next(iter(prediction))]  
        
        if isinstance(first_key_value_p, list):         

            first_dict_p = first_key_value_p[0]
            first_value_p = self.first_key(first_dict_p)

            if first_value_p != { } : 
                try :      
                    if dupl_catalyst(pr_list) : 
                        prediction_ = merging_result(first_key_value_p, pr_list)
                        prediction  = {}
                        prediction["catalysts"] = prediction_
                except : 
                    prediction = prediction
            else : 
                prediction = prediction
        else : 
            prediction = prediction

        first_key_value_g = ground_truth[next(iter(ground_truth))] 
        
        if isinstance(first_key_value_g, list):       

            first_dict_g = first_key_value_g[0]
            first_value_g = self.first_key(first_dict_g)
            if first_value_g != { } : 

                try :      
                    if dupl_catalyst(gt_list) : 

                        ground_truth_ = merging_result(first_key_value_g, gt_list)
                        ground_truth  = {}
                        ground_truth["catalysts"] = ground_truth_


                except : 
                    ground_truth = ground_truth
            else : 
                ground_truth = ground_truth
        else : 
            ground_truth = ground_truth

        return prediction, ground_truth
    
    
    def first_key(self, dict) : 
        '''
        finding first key of dict
        '''
        first_key = next(iter(dict))

        first_value = dict[first_key]
        return first_value
    
    def get_key_list_with_value_for_structure(self) :
        '''
        combine dict that have same catalyst name
        '''
        prediction, ground_truth = self.merging()
        
        pr_list = get_keys(prediction, parent_key = '', sep = '//') 
        gt_list = get_keys(ground_truth, parent_key = '', sep = '//')

        return pr_list, gt_list 
    
    def run(self) : 
        '''
        calculate structure F1 score
        '''
        TP = [] 
        FP = [] 
        FN = [] 
        corrected = []
        incorrected = []
        
        pr_list, gt_list= self.get_key_list_with_value_for_structure()

        pr_list = [item for item in pr_list if 'condition' not in item]   
        gt_list = [item for item in gt_list if 'condition' not in item]  
        
        structure_pr = []
        structure_gt = []
        for i in pr_list : 
            if '****' in i : 
                structure_pr.append(i.split("****")[0])
            else : 
                if i != '' :
                    structure_pr.append(i) 

        for i in gt_list : 
            if '****' in i : 
                structure_gt.append(i.split("****")[0])
            else : 
                if i != '' :
                    structure_gt.append(i) 
        
        
        f1_pr =  add_indices_to_duplicates(structure_pr)        
        f1_gt =  add_indices_to_duplicates(structure_gt)          

        for vv in f1_pr : 
            if vv in f1_gt : 
                TP.append(vv)
        
            if vv not in f1_gt : 
                FP.append(vv)
        
        for pp in f1_gt : 
            if pp not in f1_pr : 
                FN.append(pp)
        f1_score_l = []

        f1_score = (len(TP) / (len(TP) + (1/2)*(len(FP) + len(FN))))

        print(self.prediction_path.split('/')[-1])
        print(f1_score)
        return f1_score, len(TP)
    
    def run2(self) : 
        '''
        calculate value accuracy
        '''
        print(self.groundTruth_path)

        corrected = []
        incorrected = []
        prediction, ground_truth = self.merging()

        pr_list = get_keys_for_value_accuracy(prediction)
        gt_list = get_keys_for_value_accuracy(ground_truth)

        pr_list = [item for item in pr_list if 'condition' not in item]   
        gt_list = [item for item in gt_list if 'condition' not in item]  
        
        pr_value = []
        gt_value = []

        for i in pr_list : 
            if '****' in i : 
                pr_value.append(i)
        for j in gt_list : 
            if '****' in j : 
                gt_value.append(j)
                
        sep_pr_list = seperate_key_value(pr_value)
        sep_gt_list = seperate_key_value(gt_value)

        str_val_valset_pr = str_val_valset_split(sep_pr_list)
        str_val_valset_gt = str_val_valset_split(sep_gt_list)

        compare_gt = group_by_first_element(str_val_valset_gt)
        compare_pr = group_by_first_element(str_val_valset_pr)

        total = 0
        if not compare_gt and not compare_pr : 

            corrected = [1]
            total = 1
            
            
        elif not compare_gt and compare_pr : 
            right = len(gt_value) - len(pr_value)
            worng = len(pr_value)
            for r in range(0, right) : 
                corrected.append(r)
            for w in range(0, wrong) : 
                incorrected.append(w)
            
        elif compare_gt and compare_pr : 
            for c_pr in compare_pr : 
                for c_gt in compare_gt : 

                    if c_gt[0][0] in flatten_list(c_pr):

                        if len(c_gt) == len(c_pr) : 
                            total = total + len(c_gt)
                        elif len(c_gt) < len(c_pr) : 
                            total = total + len(c_gt)
                        elif len(c_gt) > len(c_pr) : 
                            total = total + len(c_pr)

                        if len(c_gt) == len(c_pr) and len(c_gt) == 1 : 
                            if c_gt[0][1] == c_pr[0][1] :
                                corrected.append(c_gt)
                            else : 
                                incorrected.append(c_gt)
                        else:
                            gt_valset = []
                            pr_valset = []
                            
                            for gt_unit in c_gt : 
                                if gt_unit[-1] == '':
                                    gt_unit[-1] = gt_unit[1]
                                    gt_valset.append(gt_unit)
                                gt_valset.append(gt_unit[-1].split('++'))
                                
                            for pr_unit in c_pr : 
                                if pr_unit[-1] == '':
                                    pr_unit[-1] = pr_unit[1]
                                    pr_valset.append(pr_unit)
                                else : 
                                    pr_valset.append(pr_unit[-1].split('++'))

                            while not all_element_int(gt_valset) : 
                                pair = (-1,-1)
                                max_dupl = float('-inf')
                                for index_gt, value_gt in enumerate(gt_valset) : 
                                    for index_pr, value_pr in enumerate(pr_valset) : 
                                        if finding_pair(value_gt, value_pr) > 0 : 
                                            if finding_pair(value_gt, value_pr) > max_dupl : 
                                                max_dupl = finding_pair(value_gt, value_pr)
                                                pair = (index_gt, index_pr)
  
                                if pair != (-1, -1): 
                                    lenlen = len(gt_valset[index_gt])

                                    if  c_gt[pair[0]][1] == c_pr[pair[1]][1] : 
                                        corrected.append(c_gt[pair[0]][1])

                                    else : 
                                        incorrected.append(c_gt[pair[0]][1])
                                        
                                    gt_valset[pair[0]] = [random.randint(0, 1000000) for _ in range(lenlen)]
                                    pr_valset[pair[1]] = [random.randint(0, 1000000) for _ in range(lenlen)]
                                    

                                    c_gt[pair[0]] = [random.randint(0, 1000000) for _ in range(lenlen)]
                                    c_pr[pair[1]] = [random.randint(0, 1000000) for _ in range(lenlen)]
                                
                                else : 
                                    break  
                                
        total_value_accuracy = len(corrected) / total
        return total_value_accuracy

                
    
    
    
if __name__ == '__main__':
    
    prediction_folder = 'PREDICTION FOLDER PATH'
    groundTruth_folder = 'GROUND TURTH FOLDER PATH'


    test_list = os.listdir(prediction_folder)
    value_ = []
    error = []
    
    # CALCULATE STRUCTURE F1 SCORE
    for file in test_list : 
        try : 
            prediction_path = prediction_folder + '/' + file
            groundTruth_path = groundTruth_folder+ '/' + file
            
            score = evaluation(prediction_path, groundTruth_path)
            # ##################### 벨류 평가 ######################
            # value = score.run2()
            # if value != 0 :
            #     value_.append(value)
                        
            value, _ = score.run()
            value_.append(value)

        except : 
            value_.append(0)
            error.append(file)

    final_value = (sum(value_)) / len(value_)
    print('===========final value===========')
    print(final_value)
    
    
    # CALCULATE VALUE ACCURACY
    for file in test_list : 
            prediction_path = prediction_folder + '/' + file
            groundTruth_path = groundTruth_folder+ '/' + file

            score = evaluation(prediction_path, groundTruth_path)
            value, _ = score.run()
            value_.append(value)
            
    final_value = (sum(value_)) / len(value_)
    print('===========final value===========')
    print(final_value)


















#     prediction_folder = 'C:/NLP/TableProject/ssss_v2'
#     groundTruth_folder = 'C:/NLP/TableProject/ssss_v2'

# # *********************************************************************************************
    
#     test_list = os.listdir(prediction_folder)
#     value_ = []
#     error = []
#     # for file in test_list : 
        
#         # gy_file = file.split('.')[0] + '_converted.json'

#     prediction_path = prediction_folder + '/pr_Elsevier_OER_05189_tbl05.json'
#     groundTruth_path = groundTruth_folder+ '/gt_Elsevier_OER_05189_tbl05.json'
#     # prediction_path = prediction_folder + '/' + file
#     # groundTruth_path = groundTruth_folder+ '/' + file
#     score = evaluation(prediction_path, groundTruth_path)
#     ##################### 벨류 평가 ######################
#     value = score.run2()
#     # if value != 0 :
#     #     value_.append(value)  


        
#     # final_value = (sum(value_)) / len(value_)
#     # print('===========final value===========')
#     # print(final_value)
#     # print(error)