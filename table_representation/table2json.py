from bs4 import BeautifulSoup
import pandas as pd
import json
import os
from bs4 import NavigableString
from collections import OrderedDict


class TableProcessor :
    def __init__(self, json_path) :
        self.json_path = json_path

    def load_table(self):
        '''
        load the table in format
        '''
        
        with open(self.json_path, 'r', encoding = 'utf-8') as file:
            data = json.load(file)
            
        title = data['title']
        caption = data['caption']
        table_tag = data["tag"]
        soup = BeautifulSoup(table_tag, 'html.parser')
        return soup, title, caption
    
    def caption_process(self):
        '''
        finding caption and ref data in html table, 
        giving caption data <cap> </cap> tag,
        giving reference data <ref> </ref> tag  
        '''
        
        table, _, _ = self.load_table()
        
        for tfoot in table.find_all('tfoot'):
            tfoot.decompose()
            
        td_elements = table.find_all('td')
        th_elements = table.find_all('th')
        
        for th in th_elements:
            link = th.find('a')
            if link:
                link_text = link.get_text()
                if len(link_text) == 1 and link_text.isalpha() or link_text == '*':
                    link.string = "<cap>" + link_text + "</cap>"
                elif len(link_text) == 1 and link_text == '*':
                    link.string = "<cap>" + link_text + "</cap>"
                else :
                    link.string = "<ref>" + link_text + "</ref>"

        for td in td_elements:
            link = td.find_all('a')

            if len(link) == 1:
                linktext = link[0]
                link_text = linktext.get_text()
                if len(link_text) == 1 and link_text.isalpha():
                    link[0].string = "<cap>" + link_text + "</cap>"
                elif len(link_text) == 1 and link_text == '*':
                    link[0].string = "<cap>" + link_text + "</cap>"
                else : 
                    link[0].string = "<ref>" + link_text + "</ref>"
          
            elif len(link) > 1 :
                link_string = []
                for i in link : 
                    link_str = i.get_text()
                    link_string.append(link_str)                    
                combined_string = ','.join(link_string)           
                link[0].string = "<ref>" + combined_string + "</ref>"
                for j in (1, len(link)-1) :
                    link[j].string = ''

        return table
      
    def supb_process(self):
        '''
        finding sub and sup in html table, 
        giving sub <sub> </sub> tag,
        giving sup <sup> </sup> tag  
        '''
        
        table = self.caption_process()
        for i_tag in table.find_all('i'):
            i_tag.unwrap()
        td_elements = table.find_all('td')
        th_elements = table.find_all('th')
        for th in th_elements:
            sup_ = th.find_all('sup')
            sub_ = th.find_all('sub')
            if sup_:
                for q in sup_:
                    sup_text = q.get_text() if q.get_text() else ""
                    q.string = "<sup>" + sup_text + "</sup>"
            if sub_:
                for e in sub_ :
                    sub_text = e.get_text() if e.get_text() else ""
                    e.string = "<sub>" + sub_text + "</sub>"
        for td in td_elements:
            sup = td.find_all('sup')
            sub = td.find_all('sub')
            if sup:
                for b in sup : 
                    sup_text = b.get_text() if b.get_text() else ""
                    b.string = "<sup>" + sup_text + "</sup>"
            if sub:
                for a in sub:
                    sub_text = a.get_text() if a.get_text() else ""
                    a.string = "<sub>" + sub_text + "</sub>"
            
        return table

    def header_process(self):
        '''
        Filling empty cells in the header with '-'.
        '''
        
        table = self.supb_process()
        th_elements = table.find_all('th')
        for th in th_elements :
            if not th.text.strip() :
                th.insert(0, '-')
            th['align'] = 'left'
        
        return table
    
    def body_process(self):
        '''
        Copy the first cell of the previous row if the first cell is empty.
        '''

        table = self.header_process()
        has_empty_cells = False
        prev_value = None
        for row in table.find_all('tr'):
            first_cell = row.find('td') 
            if first_cell:
                cell_text = first_cell.text.strip()
                if cell_text == '' and prev_value:
                    first_cell.string = prev_value
                if cell_text == '':
                    has_empty_cells = True
                prev_value = cell_text 

        return table

    def convert_to_dataframe(self):
        '''
        Conveert the html table to dataframe
        '''
        
        table = self.body_process()
        dfs = pd.read_html(str(table))
        df_table = dfs[0]
        df_table.fillna("NaN", inplace=True) 
        
        return df_table

    def convert_to_json(self, table_name, save_directory):
        '''
        Convert dataframe to json.
        '''
        _, title, caption = self.load_table()
        table_name = table_name.split('.')[0]
        name_element = table_name.split('_')
        df_for_json = self.convert_to_dataframe()
        header_row = df_for_json.columns.nlevels
        df_for_json_key = list(df_for_json.columns)
        num_columns = df_for_json.shape[1]

        key_list = []
        value_list = []
        for i in range(0, num_columns):
            key_list.append(df_for_json_key[i])
            value_list.append(df_for_json.iloc[:, i].tolist())

        result = {}
        if header_row > 1:
            for i, keys in enumerate(key_list):
                current_dict = result
                for j, key in enumerate(keys):
                    if key not in current_dict:
                        current_dict[key] = {}
                    if j == len(keys) - 1:
                        current_dict[key] = value_list[i]
                    current_dict = current_dict[key]
        elif header_row == 1 : 
            for i, keys in enumerate(key_list):
                current_dict = result

                current_dict[keys] = value_list[i]
                
        # try : 
        key_to_extract = caption
        title_to_extract = title
        key_to_extract = {
            
            "caption": key_to_extract
        }
        title_to_extract = {
            
            "Title": title_to_extract
        }

        result.update(key_to_extract)
        title_to_extract.update(result)
        save_directory_ = save_directory + '/' + table_name + '.json'
        
        with open(save_directory_, 'w', encoding='utf-8') as f:
            json.dump(title_to_extract, f, indent=4)


# if __name__ == '__main__':
#     json_path = 'Z:/NLP Project/table/code_upload/data/split/table_split_json'
#     json_file_list = os.listdir(json_path)
#     save_directory = 'Z:/NLP Project/table/code_upload/data/split/json_representation'
    

#     for i in json_file_list:
#         a = i.split('.')[0]
#         table_processor = TableProcessor(json_path + a + '.json')
#         table_processor.convert_to_json(i, save_directory)
    
    
