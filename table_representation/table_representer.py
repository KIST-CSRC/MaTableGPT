import os
import json
from bs4 import BeautifulSoup
import re

class TableRepresenter:
    def __init__(self, table_path):
        self.table_path = table_path
        self.table_list = os.listdir(self.table_path)

        # Initialize cell representation strings
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
        
        # Remove or replace specific patterns
        patterns = [
            (r'<cap>(\(\d+\)|\d+|\[\d+\]|\d+\,\d+|\d+\,\d+\,\d+|\d+\,\d+\–\d+|\d+\D+|\(\d+\,\s*\d+\)|\(\d+\D+\))</cap>', r'\1'),
            (r'<cap>(\s*ref\.\s\d+.*?)</cap>', r'\1'),
            (r'\(<cap>(\s*(ref\.\s\d+.*?)\s*)</cap>\)', r'\1'),
            (r'<cap>(\s*Ref\.\s\d+.*?)</cap>', r'\1'),
            (r'\(<cap>(\s*(Ref\.\s\d+.*?)\s*)</cap>\)', r'\1'),
            (r'<cap>(\[\d+|\d+\])</cap>', r'\1'),
            (r'<cap>((.*?)et al\..*?)</cap>', r'\1'),
            (r'<cap>((.*?)Fig\..*?)</cap>', r'\1'),
            (r'<cap>(Song and Hu \(2014\))</cap>', r'\1'),
            (r'<div> <cap>  </cap> </div> ', '',),
            (r'<cap>(mA\.cm)</cap>', r'\1'),
            (r'<cap>(https.*?)</cap>', r'\1'),
            (r'<cap>(\d+\.\d+\@\d+)</cap>', r'\1')
        ]
        
        for pattern, repl in patterns:
            out = re.sub(pattern, repl, out)
        
        return out

    def caption_process(self, caption):
        """
        Process the caption text and extract key-value pairs.
        """
        pattern = r'(\w+): (.*?)(?:;|$)'
        matches = re.findall(pattern, caption)
        result_dict = {key.strip(): value.strip() for key, value in matches}
        print(result_dict)

    def load_data(self, file_name):
        """
        Load JSON data from the specified file.
        """
        file_path = os.path.join(self.table_path, file_name)
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            data = json.load(file)
        return data

    def process_table(self, t):
        """
        Remove unnecessary HTML tags from the table element.
        """
        tags_to_remove = ['img', 'em', 'i', 'p', 'span', 'strong', 'math', 'mi', 'br', 'script', 'svg', 'mrow', 'mo', 'mn', 'msub', 'msubsup', 'mtext', 'mjx-container', 'mjx-math', 'mjx-mrow', 'mjx-msub', 'mjx-mi', 'mjx-c', 'mjx-script', 'mjx-mspace', 'mjx-assistive-mml', 'mspace']
        
        for tag in tags_to_remove:
            elements = t.find_all(tag)
            for element in elements:
                if tag in ['img', 'script', 'svg']:
                    element.decompose()
                else:
                    element.unwrap()
        
        return t

    def make_table_representer(self, table_representer, table_element, head=None):
        """
        Create a table representation with the appropriate formatting.
        """
        out = [['' for _ in range(self.width)] for _ in range(self.height if head is None else len(table_element.find_all('tr')))]
        
        i = 0
        for tr in table_element.find_all('tr'):
            j = 0
            for t in tr.find_all(re.compile('(?<!ma)th|td')):
                for sub_tag in t.find_all('sub'):
                    for strong_tag in sub_tag.find_all('strong'):
                        strong_tag.unwrap()
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

                while out[i][j] != '': 
                    j += 1

                refined_text = ''.join(str(element) for element in t.contents)
                colspan = int(t.get('colspan', 0))
                rowspan = int(t.get('rowspan', 0))

                if colspan and rowspan:
                    for c in range(i, i + colspan):
                        for r in range(j, j + rowspan):
                            out[c][r] = '::'
                    out[i][j] = self.both_merged_cell.format('colspan', colspan, 'rowspan', rowspan, self.text_filter(refined_text))
                elif colspan:
                    out[i][j] = self.merged_cell.format('colspan', colspan, self.text_filter(refined_text))
                elif rowspan:
                    out[i][j] = self.merged_cell.format('rowspan', rowspan, self.text_filter(refined_text))
                else:
                    if not t.contents and not t.string:
                        t.contents = [' ']
                    out[i][j] = self.text_filter(refined_text)

                if colspan:
                    for c in range(colspan - 1):
                        out[i][j + c + 1] = "::"
                if rowspan:
                    for r in range(rowspan - 1):
                        out[i + r + 1][j] = "::"

                while out[i][j] != '': 
                    if j != self.width - 1:
                        j += 1    
                    else:
                        if head is True and i != len(table_element.find_all('tr')) - 1:
                            i += 1
                            break
                        elif head is False and i != self.height - 2:
                            i += 1
                            break
                        elif head is None and i != self.height - 1:
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
        return result
    
    def run(self, table, save_directory):  
        cap_table_list = []

        final_table_representer = {}
        print(table)

        data = self.load_data(table)
        table_tag = data["tag"]
        soup = BeautifulSoup(table_tag, 'html.parser')
        thead = soup.find('thead')
        tbody = soup.find('tbody')

        self.width = sum(int(t.get('colspan', 1)) for t in soup.find('tbody').find('tr').find_all(re.compile('(?<!ma)th|td')))
        self.height = len(soup.find_all('tr'))

        table_representer = ''
        if thead is None:
            tbody_element = self.make_table_representer(table_representer, tbody)
            final_table_representer['body'] = tbody_element
            table_list = tbody_element
        else:
            thead_element = self.make_table_representer(table_representer, thead, head=True)
            tbody_element = self.make_table_representer(table_representer, tbody, head=False)
            final_table_representer['head'] = thead_element
            final_table_representer['body'] = tbody_element
            table_list = thead_element + tbody_element

        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        
        # Copy the cells above if there are blank spaces in the first column
        for i in range(0, len(table_list)):
            if i != 0:
                if table_list[i][0] == ' ':

                    if "merge" in table_list[i-1][0]:
                        table_list[i][0] = '::'
                    
                    else:
                        table_list[i][0] = table_list[i-1][0]          
        # print(table_list)

        for i, rows in enumerate(table_list):
            pattern = r'(\(\d{1,2}\)|\[\d{1,2}\]|\[\d{1,2}\] HER|\(\d{1,2}\)\)|\(this work\)|\(This work\))$'
            rows[0] = re.sub(pattern, r'<ref>\1</ref>', rows[0])
            table_list[i] = rows

        result = ''

        for table_row in table_list:
            for element in table_row:
                if element == '::':
                    pass
                else:
                    result += self.cell.format(element)
            result += self.line_breaking
            
        final_result = self.table_tag.format(result)
        
        caption = data['caption']
        title = data['title']
        
        final_result = self.title_tag.format(title) + final_result

        for table_row in table_list:
            for element in table_row:
                if "<cap>" in element:
                    cap_table_list.append(table)
        
        cap_table_list = list(set(cap_table_list))

        if caption:
                
            final_result += '\n'
            if isinstance(caption, dict):
                caption_str = ', '.join([f"{key}: {value}" for key, value in caption.items()])
                final_result += self.caption_tag.format(caption_str)
            else:
                final_result += self.caption_tag.format(caption)

        save_path = os.path.join(save_directory, table[:-5]+'.txt')       
        with open (save_path, 'a', encoding='utf-8-sig') as f:
            f.write(final_result)                                
        
# if __name__ == "__main__": 
#     table_path = 'example_json folder path'
#     save_directory = 'Z:/NLP Project/table/code_upload/data/split/tsv_representation'
#     table_path = 'Z:/NLP Project/table/code_upload/data/split/table_split_json/'
#     table_list = os.listdir(table_path)
#     table = TableRepresenter(table_path) 
    
#     for table_element in table_list:
#         print(table_element)
#         table.run(table_element, save_directory)
    