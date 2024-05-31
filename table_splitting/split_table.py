from bs4 import BeautifulSoup
import json
import os
from bs4 import NavigableString
import copy
import pickle
import nltk
import re

class TablePaser:
    def __init__(self, json_path, table_path, pickle_path):
        self.json_path = json_path
        self.table_path = table_path
        self.pickle_path = pickle_path
        self.table_list = os.listdir(self.table_path)
        self.merged_cell = '<merge {}={}>{}</merge>'
        self.both_merged_cell = '<merge {}={} {}={}>{}</merge>'
        self.cell = '{}\\t'
        self.line_breaking = '\\n'
        self.table_tag = '<table>{}</table>'
        self.caption_tag = '<caption>{}</caption>'    
        self.title_tag = '<title>{}</title>'
        
    def text_filter(self, out):
        """
        Remove unnecessary text and HTML tags from the given string.
        """
        out = re.sub('\\xa0', ' ', out)  
        out = re.sub('\\u2005', ' ', out)
        out = re.sub('\\u2009', ' ', out)
        out = re.sub('\\u202f', ' ', out)
        out = re.sub('\\u200b', '', out)
        out = re.sub('<b>', '', out)
        out = re.sub('</b>', '', out)
        out = re.sub(r'<cap>(\(\d+\)|\d+|\[\d+\]|\d+\,\d+|\d+\,\d+\,\d+|\d+\,\d+\–\d+|\d+\D+|\(\d+\,\s*\d+\)|\(\d+\D+\))</cap>', r'\1', out) 
        out = re.sub(r'<cap>(\s*ref\.\s\d+.*?)</cap>', r'\1', out)
        out = re.sub(r'\(<cap>(\s*(ref\.\s\d+.*?)\s*)</cap>\)', r'\1', out)
        out = re.sub(r'<cap>(\s*Ref\.\s\d+.*?)</cap>', r'\1', out)
        out = re.sub(r'\(<cap>(\s*(Ref\.\s\d+.*?)\s*)</cap>\)', r'\1', out)
        out = re.sub(r'<cap>(\[\d+|\d+\])</cap>', r'\1', out)
        out = re.sub(r'<cap>((.*?)et al\..*?)</cap>', r'\1', out)
        out = re.sub(r'<cap>((.*?)Fig\..*?)</cap>', r'\1', out)
        out = re.sub(r'<cap>(Song and Hu \(2014\))</cap>', r'\1', out)
        out = re.sub(r'<div> <cap>  </cap> </div> ', '', out)
        out = re.sub(r'<cap>(mA\.cm)</cap>', r'\1', out)
        out = re.sub(r'<cap>(https.*?)</cap>', r'\1', out)
        out = re.sub(r'<cap>(\d+\.\d+\@\d+)</cap>', r'\1', out)
        out = re.sub(r'\[<ref>(\d+)</ref>\]','['+r'\1'+']', out)
        return out   

    def metadata(self, file_name):
        file_name_parts = file_name.split('.')[0]
        json_file_name = file_name_parts + '.json'
        file_path = os.path.join(self.json_path, json_file_name)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            metadata = json.load(file)

        return file_name, metadata
    
    def process_table(self, t):
        """
        Remove unnecessary HTML tags from the table element.
        """
        for tag in ['img', 'em', 'i', 'p', 'span', 'strong', 'math', 'mi', 'script', 'svg', 'mrow', 'mo', 'mn', 'br', 'msub', 'msubsup', 'mtext', 'mjx-container', 'mjx-math', 'mjx-mrow', 'mjx-msub', 'mjx-mi', 'mjx-c', 'mjx-script', 'mjx-mspace', 'mjx-assistive-mml', 'mspace']:
            if t.find(tag):
                if tag == 'em' or tag == 'i' or tag == 'p' or tag == 'span' or tag == 'strong' or tag == 'mi' or tag == 'mrow'or tag == 'mo'or tag == 'mn' or tag == 'br' or tag =='msub' or tag == 'msubsup' or tag =='mtext'or tag =='mjx-container' or tag == 'mjx-math' or tag =='mjx-mrow' or tag=='mjx-msub' or tag =='mjx-mi' or tag == 'mjx-c' or tag=='mjx-script' or tag =='mjx-mspace' or tag=='mjx-assistive-mml' or tag=='mspace':
                    for strong_tag in t.find_all(tag):
                        strong_tag.unwrap()
                elif tag == 'img' or tag == 'script' or tag == 'svg':
                    img_tag = t.find(tag)
                    img_tag.decompose()           
        return t
    
    def make_table_representer(self, table_representer, table_element, head=None):
        """
        Create a table representation with the appropriate formatting.
        """
        out = []
        if head == True:
            head_height = len(table_element.find_all('tr'))  
            for i in range(head_height):
                out.append([])
                for j in range(self.width):
                    out[i].append('')   
        elif head == False:
            body_height = len(table_element.find_all('tr')) 
            for i in range(body_height):
                out.append([])
                for j in range(self.width):
                    out[i].append('') 
        else:  
            for i in range(self.height):
                out.append([])
                for j in range(self.width):
                    out[i].append('')           
        i = 0    

        for tr in table_element.find_all('tr'):
            j = 0

            for t in tr.find_all(re.compile('(?<!ma)th|td')):
                for sub_tag in t.find_all('sub'):
                    for strong_tag in sub_tag.find_all('strong'):
                        strong_tag.unwrap()
                for a_tag in t.find_all('a'):
                    for a_tag in t.find_all('a'):
                        a_text = a_tag.get_text()
                        if a_text.isdigit():
                            ref_tag = BeautifulSoup().new_tag('ref')
                            ref_tag.string = a_text
                            a_tag.replace_with(ref_tag)
                        else:    
                            cap_tag = BeautifulSoup().new_tag('cap')
                            cap_tag.string = a_text
                            a_tag.replace_with(cap_tag)
                if t.find('math'):        
                    t.find('math').unwrap()
                t = self.process_table(t)    
                while(out[i][j] != ''): j += 1
                
                if t.get('colspan') and t.get('rowspan'):
                    refined_text = ''.join(str(element) for element in t.contents)
                    colspan = int(t.get('colspan'))
                    rowspan = int(t.get('rowspan'))
                    for c in range(i, i + colspan):
                        for r in range(j, j + rowspan):
                            out[c][r] = self.text_filter(refined_text)                 
                    out[i][j] = self.text_filter(refined_text)           
                elif t.get('colspan'):
                    refined_text = ''.join(str(element) for element in t.contents)
                    colspan = int(t.get('colspan'))
                    rowspan = 0
                    out[i][j] = self.text_filter(refined_text)
                elif t.get('rowspan'):
                    refined_text = ''.join(str(element) for element in t.contents)
                    rowspan = int(t.get('rowspan'))
                    colspan = 0
                    out[i][j] = self.text_filter(refined_text)
                else:
                    colspan = 0
                    rowspan = 0
                    if not t.contents and not t.string:
                        t.contents = [' ']
                    refined_text = ''.join(str(element) for element in t.contents)
                    out[i][j] = self.text_filter(refined_text)

                try:
                    if colspan != 0:
                        for c in range(colspan-1):
                            out[i][j+c+1] = out[i][j]
                    if rowspan!= 0:    
                        for r in range(rowspan-1):
                            out[i+r+1][j] = out[i][j]

                except:
                    pass
                while(out[i][j] != ''): 
                    if j != self.width-1:
                        j += 1    
                    else:
                        if head == True:
                            if i != head_height-1:
                                i += 1
                                break

                            else:
                                break
                        elif head == False:
                            if i != self.height-2:
                                i += 1
                                break

                            else:
                                break
                        else:
                            if i != self.height-1:
                                i += 1
                            else:
                                break
        return out      
    def remove_sup_tags(self, data):
        """
        Remove <sub> and <sup> tags from the table data.
        """
        result = [[item.replace('<sub>', '').replace('</sub>', '') for item in inner_list] for inner_list in data]
        result = [[item.replace('<sup>', '').replace('</sup>', '') for item in inner_list] for inner_list in result]
        return   result
    
    def run(self):  
        cap_table_list = []
        cap_table_dict = {}
        for table in self.table_list:
            final_table_representer = {}

            file_name, metadata = self.metadata(table)
            table_title = metadata.get('title', '')
            table_caption = metadata.get('caption', '')
            table_tag = metadata.get('tag', '')
            soup = BeautifulSoup(table_tag, 'html.parser')
            thead = soup.find('thead') if soup.find('thead') else None
            tbody = soup.find('tbody') if soup.find('tbody') else None

            if len(soup.find_all()) == 0:
                continue
            self.width = 0
            for t in soup.find('tbody').find('tr').find_all(re.compile('(?<!ma)th|td')):
                if t.get('colspan'):
                    self.width += int(t.get('colspan'))
                else:
                    self.width += 1

            self.height = len(soup.find_all('tr'))  
            table_representer = ''

            tbody_element = self.make_table_representer(table_representer, tbody)

            final_table_representer['body'] = tbody_element
            table_list = tbody_element

            directory = './table_representer'
            if not os.path.exists(directory):
                os.makedirs(directory)
                        for i in range(0, len(table_list)):
                if i != 0:
                    if table_list[i][0] == ' ':
                        if "merge" in table_list[i-1][0]:
                            table_list[i][0] = '::'
                        
                        else:
                            table_list[i][0] = table_list[i-1][0]
                            
            
            if not os.path.exists(self.pickle_path):
                os.makedirs(pickle_directory)                            
            save_path = os.path.join(self.pickle_path, file_name[:-5]+'.pickle')       
          
            with open(save_path, 'wb') as f:
                pickle.dump(table_list, f) 
        return table_list

    
class DivideHtml() : 
    def __init__(self, html_path, pickle_path, save_path) : 
        self.html_path = html_path
        self.pickle_path = pickle_path
        self.save_path = save_path
        
    def load_pickle(self) : 
        '''
        load pickle data in ./data/pickle_folder
        '''
        with open(self.pickle_path, 'rb') as file:
            data = pickle.load(file)
            
        empty_row = []
        for row in data : 

            if all(element == '' for element in row):
                empty_row.append(row)
            if all(element == ' ' for element in row):
                empty_row.append(row)
            if all(element == '  ' for element in row):
                empty_row.append(row)
            if all(element == '   ' for element in row):
                empty_row.append(row)
            if all(element == ' \u2006' for element in row) : 
                empty_row.append(row)     
            if all(element == '&nbsp;' for element in row) : 
                empty_row.append(row)   
            if all(element == '&thinsp;' for element in row) : 
                empty_row.append(row)
                
        for r in empty_row : 
            data.remove(r)
        return data

    def head_tag(self) : 
        '''
        Finding head in html
        '''
        with open(self.html_path, 'r', encoding = 'utf-8-sig') as file : 
            html = file.read()
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')

        head_list =[]
        head_element = table.find_all('thead')

        if len(head_element) == 0 : 
            return None
        else : 
            head = head_element[0]
            return head
    
    def head_body_decision_making(self) :
        '''
        Finding sub-header in body
        '''
        data = self.load_pickle()
            
        row_h_b_list = []
    
        for row in data :
            if len(list(set(row))) == 1 :  
                if len(row) >1 : 
                    row_h_b_list.append('head')
                
                else : pass
            
            else : 
                td_list = []
                for td in row : 
                    if td.lower() == 'empty cell' : 
                        td = td.replace('empty cell', ' ')

                    if td == '-' : 
                        td = td.replace('-', '0')
                    if td == '—' : 
                        td = td.replace('—', '0')
                    if td == '–' : 
                        td = td.replace('–', '0')
                    if td == '--' : 
                        td = td.replace('--', '0')
                    if td == '---' : 
                        td = td.replace('---', '0')                   
                    if td == '----' : 
                        td = td.replace('----', '0') 
                    if td == '' : 
                        td = td.replace('', '0')               
                    if td == ' ' : 
                        td = td.replace(' ', '0')      
                    if 'work' in td : 
                        td = '0 ' + td   
                    if 'et al' in td : 
                        td = '0 ' + td   
                                                                        
                    tokens = nltk.word_tokenize(td)
                    for t in tokens : 
                        t.strip()
                        
                    if 'ref' in tokens : 
                        tokens.remove('ref')
                    if 'Ref' in tokens : 
                        tokens.remove('Ref')
                    if '<ref>' in tokens : 
                        tokens.remove('<ref>')
                    if '</ref>' in tokens : 
                        tokens.remove('</ref>')
                    if 'mV' in tokens : 
                        tokens.remove('mV')
                    if 'V'  in tokens : 
                        tokens.remove('V')
                    if '%' in tokens : 
                        tokens.remove('%') 
                    if 'sup' in tokens : 
                        tokens.remove('sup')
                    if '/sup' in tokens : 
                        tokens.remove('/sup')
                    if 'sub' in tokens : 
                        tokens.remove('sub')
                    if '/sub' in tokens : 
                        tokens.remove('/sub')

                    cleaned_tokens = []
                    final_tokens = []

                    for item in tokens:
                        cleaned_item = ''.join(e for e in item if e.isalnum() or e.isspace())
                        cleaned_tokens.append(cleaned_item)

                    for i in cleaned_tokens : 
                        if i != '' : 
                            final_tokens.append(i)

                    if final_tokens == [] : 
                        pass
                    
                    else :
                        try : 
                            token_string = final_tokens[0]
                            token_lll = token_string.split()
                            
                            float(token_lll[0]) 
                            td_list.append('b')
                        
                        except : 
                            td_list.append('h')
                
                if 'b' in td_list : 
                    row_h_b_list.append('body')
                
                else : 
                    row_h_b_list.append('head')     
        row_h_b_list[-1] = 'body'
        return row_h_b_list

    def split_list_by_indexes(self, body, index_list): 
        '''
        Split the list by the header in the double-header to create N lists.
        '''
        result = []
        start = 0
        for index in index_list:
            result.append(body[start:index])
            start = index
        result.append(body[start:])
        return result

    def case_1(self, origin_head, origin_body, body_h_b_list) : 
        '''
        When the header comes at the top of the body
        '''
        head_index = []
        body_index = []
        for i, decision in enumerate(body_h_b_list) : 
            if decision == 'head' : 
                head_index.append(i)
            else : 
                body_index.append(i)
                
        head = []
        body = []
        
        for h in head_index : 
            head.append(origin_body[h])
        for b in body_index : 
            body.append(origin_body[b])
            
        for i, row in enumerate(head) : 
            formatted_list = [f'<td>{item}</td>' for item in row]
            result_head = ' '.join(formatted_list)
            result_head = '<tr> ' + result_head + ' </tr>'
            
        if origin_head == None : 
            modified_head = '<thead>' + result_head + '</thead>'
        
        else : 
            origin_head = str(origin_head)
            modified_head = origin_head.replace('</thead>', '')
            modified_head = modified_head + result_head + '</thead>'     

        for i, row in enumerate(body) : # body html 형식으로 변환
            formatted_list = [f'<td>{item}</td>' for item in row]
            result_body = ' '.join(formatted_list)
            result_body = '<tr> ' + result_body + ' </tr>'
            final_body = '<tbody>' + result_body + '</tbody>' # 행별로 tbody 붙여줌
            
            padded_index = str(i + 1).zfill(2)

            html_string = f"<table class='table'><table>{str(modified_head)}{str(final_body)}</table>"
            with open(self.save_path + f"/{file_name}_{padded_index}.html", "w", encoding="utf-8") as file:
                file.write(html_string)

        
    def case_2(self, origin_head, origin_body, body_h_b_list) :
        '''
        When the structure of the header repeats within the body
        '''
        table_seperate_index = []
        
        for i, hb in enumerate(body_h_b_list) : 
            if hb == 'head' : 
                table_seperate_index.append(i)

        table_seperate_index_result = []
        current_sequence = []

        for num in table_seperate_index:
            if not current_sequence or num == current_sequence[-1] + 1:
                current_sequence.append(num)
            else:
                table_seperate_index_result.append(current_sequence[0])
                current_sequence = [num]

        if current_sequence:
            table_seperate_index_result.append(current_sequence[0])
        
        table_split = self.split_list_by_indexes(origin_body, table_seperate_index_result)
        index_split = self.split_list_by_indexes(body_h_b_list, table_seperate_index_result)
        total_table = []
        for table_num in range(0, len(index_split)) : 

            if 'head' not in index_split[table_num] : 
                body_string_list = []
                for row_ in table_split[table_num] : 

                    for i, row in enumerate(row_) : # head html 형식으로 변환
                        formatted_list = [f'<td>{item}</td>' for item in row_]
                        result_ = ' '.join(formatted_list)
                        result_ = '<tbody> <tr> ' + result_+ ' </tr> </tbody>'
                    body_string_list.append(result_)

                origin_head = str(origin_head)
                for table_ in body_string_list : 
                    table_ = origin_head + table_
                    total_table.append(table_)
            else : 
                table_head = []
                table_body = []
                
                for row_index in range(0, len(table_split[table_num])) :

                    if index_split[table_num][row_index] == 'head' : 

                        formatted_list = [f'<td>{item}</td>' for item in table_split[table_num][row_index]]
                        result_ = ' '.join(formatted_list)
                        result_ = '<tr> ' + result_ + ' </tr>'
                        table_head.append(result_)

                    else : 
                        formatted_list = [f'<td>{item}</td>' for item in table_split[table_num][row_index]]
                        result_ = ' '.join(formatted_list)
                        result_ = '<tr> ' + result_ + ' </tr>'
                        table_body.append(result_)
                
                table_head = ''.join(table_head)
                for body_row in table_body : 
                    body_row = '<tbody>' + body_row + '</tbody>'
                    f_table = '<thead>' + table_head + '</thead>' + body_row
                    total_table.append(f_table)

        for i, row in enumerate(total_table) : 
            
            padded_index = str(i + 1).zfill(2)

            html_string = f"<table class='table'><table>{str(row)}</table>"
            with open(self.save_path + f"/{file_name}_{padded_index}.html", "w", encoding="utf-8") as file:
                file.write(html_string)
                
    def case_3(self, origin_head, origin_body, body_h_b_list) : 
        '''
        When the common header comes in the header and the sub-header comes in the body
        '''
        table_seperate_index = []
        
        for i, hb in enumerate(body_h_b_list) : 
            if hb == 'head' : 
                table_seperate_index.append(i)

        table_seperate_index_result = []
        current_sequence = []

        for num in table_seperate_index:
            if not current_sequence or num == current_sequence[-1] + 1:
                current_sequence.append(num)
            else:
                table_seperate_index_result.append(current_sequence[0])
                current_sequence = [num]

        if current_sequence:
            table_seperate_index_result.append(current_sequence[0])

        table_seperate_index_result.pop(0)        
        table_split = self.split_list_by_indexes(origin_body, table_seperate_index_result)
        index_split = self.split_list_by_indexes(body_h_b_list, table_seperate_index_result)

        table_final = []
        for split_index in range(0, len(table_split)) : 
            table_ =[]
            for row_index in range(0, len(table_split[split_index])) : 
                table_head = []
                table_body = []

                if index_split[split_index][row_index] == 'head' : 

                    formatted_list = [f'<td>{item}</td>' for item in table_split[split_index][row_index]]
                    result_ = ' '.join(formatted_list)
                    result_ = '<tr> ' + result_ + ' </tr>'
                    table_head.append(result_)
                        
                else : 
                    formatted_list = [f'<td>{item}</td>' for item in table_split[split_index][row_index]]
                    result_ = ' '.join(formatted_list)
                    result_ = '<tr> ' + result_ + ' </tr>'
                    table_body.append(result_)
                
                if table_head != [] : 
                    table_.append(table_head)
                else : 
                    table_.append(table_body)
                
            head_index = list(filter(lambda x: index_split[split_index][x] == 'head', range(len([split_index]))))
            body_index = []
            for i in range(0, len(index_split[split_index])) : 
                if i not in head_index : 
                    body_index.append(i)
            
            head_string = ''
            body_string_list = []
            for head in head_index : 
                head_string += table_[head][0]
                
            if origin_head == None : 
                head_string = '<thead>' + str(head_string) + '</thead>'
            else :
                origin_head = str(origin_head) 
                origin_head = origin_head.replace("</thead>", " ")
                head_string = origin_head + head_string + '</thead>'
                
            for body in body_index : 
                body_string_list.append('<tbody>' + table_[body][0] + '</tbody>')
            
            for fi in body_string_list : 
                table_final.append(head_string + fi)
        
        
        for i, row in enumerate(table_final) :           
            padded_index = str(i + 1).zfill(2)

            html_string = f"<table class='table'><table>{str(row)}</table>"
            with open(self.save_path + f"/{file_name}_{padded_index}.html", "w", encoding="utf-8") as file:
                file.write(html_string)
                

    def normal(self, origin_head, origin_body) : 
        '''
        Normal table
        '''
        table_final = []
        f_body = []
        origin_head = str(origin_head)
        for row in origin_body : 
            formatted_list = [f'<td>{item}</td>' for item in row]
            result_ = ' '.join(formatted_list)
            result_ = '<tbody> <tr> ' + result_ + ' </tr> </tbody>'
            f_body.append(result_)
        
        for f in f_body : 
            f = origin_head + f
            table_final.append(f)
            
            
        for i, row in enumerate(table_final) :          
            padded_index = str(i + 1).zfill(2)

            html_string = f"<table class='table'><table>{str(row)}</table>"
            with open(self.save_path + f"/{file_name}_{padded_index}.html", "w", encoding="utf-8") as file:
                file.write(html_string)
        
    def run(self) : 
        '''
        Determining the type of table,
        then splitting it according to the rule.
        '''
        f_name = self.html_path.split('/')[-1]
        print(f_name)
        
        origin_body = self.load_pickle()
        origin_head = self.head_tag()
        row_h_b_list = self.head_body_decision_making()
        print(origin_body)
        if all(element == 'body' for element in row_h_b_list) :      
            ######### normal #########
            self.normal(origin_head, origin_body)
            
        elif row_h_b_list.count('head') > 6 : 
            print('outlier')
        
        else :
            if row_h_b_list[0] == 'head' : 
                last_head = len(row_h_b_list) - row_h_b_list[::-1].index('head') - 1
                
                if 'body' not in row_h_b_list : 
                    print('outlier')

                else :     
                    if last_head == row_h_b_list.count('head') - 1:
                        ######### case 1 #########
                        self.case_1(origin_head, origin_body, row_h_b_list)
           
                    else : 
                        ######### case 2 #########
                        if origin_head == None : 
                            self.case_2(origin_head, origin_body, row_h_b_list)
                        ######### case 3 #########
                        else : 
                            self.case_3(origin_head, origin_body, row_h_b_list)
            else : 
                ######### case 2 #########
                self.case_2(origin_head, origin_body, row_h_b_list)
