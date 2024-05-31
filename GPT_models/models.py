import json
import os
import openai
import time
from ast import literal_eval
from copy import copy

def fine_tuning(input_path, output_path):
"""
Test fine_tuning model, generates the prediction of table data extraction in json format.
You can use OPENAI PLAYGROUND for training the model. 

Parameters:
input_path : TSV or JSON table representation path
output_path : The path where the prediction is saved

Returns:
json : prediction of table data extraction
"""     

  openai.api_key = "YOUR OPENAI KEY" 
  file_list = os.listdir(input_path)

  response = []
  for file in file_list:
      file_path = ''.join([output_path, file])
      file_name = os.path.basename(file_path)
      with open( input_path + file, 'r', encoding='utf-8-sig') as file:
          loaded_data_string = json.load(file) 
          
      completion = openai.ChatCompletion.create(
        model="FINE TUNED MODEL",
        temperature=0,
        messages=[
          {"role": "system", "content": "this task is to take a string as input and convert it to json format. I want to extract the performance below. [reaction_type, versus, overpotential, substrate, loading, tafel_slope, onset_potential, current_density, BET, specific_activity, mass_activity, surface_area, ECSA, apparent_activation_energy, water_splitting_potential, potential, Rs, Rct, Cdl, TOF, stability, electrolyte, exchange_current_density, onset_overpotential]. If there is information about overpotential and Tafel slope in the input, the output should be generated as follows.\n\n{\n\u201dcatalyst_name\": {\n\"overpotential\": {\n\"electrolyte\": \"1.0 M KOH\",\n\"reaction_type\": \"OER\",\n\"value\": \"230 mV\",\n\"current_density\": \"50 mA/cm2\"\n},\n\"tafel_slope\": {\n\"electrolyte\": \"1.0 M KOH\",\n\"reaction_type\": \"OER\",\n\"value\": \"54 mV/dec\"\n}\n\n}\n\n}\n\nIf information regarding the reaction_type or electrolyte cannot be found in the input, they should not be included in the output as follows.\n\n{\n\u201dcatalyst_name\": {\n\"overpotential\": {\n\"value\": \"230 mV\",\n\"current_density\": \"50 mA/cm2\"\n},\n\"tafel_slope\": {\n\"value\": \"54 mV/dec\"\n}\n\n}\n\n}\n\nIf the string is missing certain information such as 'mass_activity', ‘reaction_type’, ‘value’ or 'current_density', your output should not include those keys.\n\nIf there are no values corresponding to the mentioned performance metrics in the input, simply extract the catalyst name as shown below.\n\n{\n\u201dcatalyst_name\": {}\n}\n\nNote: The output should be a JSON object with keys for only the present metrics."},
          {"role": "user", "content": str(loaded_data_string)}
        ]
      )
      result = completion.choices[0].message['content']
      response.append(result)
      try:
          dict_1 = literal_eval(result)
          json_file_path = os.path.join(output_path, file_name)
          with open(file_path[:-5]+'.json', "w", encoding="utf-8-sig") as json_file:
              json.dump(dict_1, json_file, indent=4)
      except:
          with open(file_path[:-5]+'.txt', "w", encoding="utf-8-sig") as file:
              file.write(result)
              
              

def few_shot(input_path, output_path) :   
"""
Test few shot model, generates the prediction of table data extraction in json format.
You need to give several I/O pairs.

Parameters:
input_path : TSV or JSON table representation path
output_path : The path where the prediction is saved

Returns:
json : prediction of table data extraction
"""        
    client = OpenAI(api_key=  "YOUR OPENAI KEY")
    file_list = os.listdir(input_path)
    for file in file_list : 
        with open(input_path + file, 'r', encoding='utf-8') as file:
            text = file.read()
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            temperature=0,
            frequency_penalty=0,
            presence_penalty=0,
            messages=[
            {"role": "system", "content": "I will extract the performance information of the catalyst from the table and create a JSON format. The types of performance to be extracted will be given as a list: performance_list = [overpotential, tafel_slope, Rct, stability, Cdl, onset_potential, current_density, potential, TOF, ECSA, water_splitting_potential, mass_activity, exchange_current_density, Rs, specific_activity, onset_overpotential, BET, surface_area, loading, apparent_activation_energy]. You can only use the names as they are in the performance_list, and any changes to the names in the performance_list, no matter how slight, are not allowed. The JSON format will have performance within the catalyst, and each performance will include elements present in the table: reaction type, value, electrolyte, condition, current density, versus(ex: RHE) and substrate. Other elements must not be included in performance. Be very strict. The output must contain only json dictionary. Other sentences or opinion must not be in output."},
            
            # X I/O PAIRS
            {"role": "user", "content":''},
            {"role": "assistant", "content": ''},
            
            {"role": "user", "content": text}
        ]
    )
        prediction = response.choices[0].message.content.strip()
        output_filename = output_path + '/' + name 
        try : 
            json_data = json.loads(prediction)
            with open(output_filename + '.json', 'w', encoding='utf-8-sig') as json_file:
                json.dump(json_data, json_file, ensure_ascii = False, indent = 4)

        except : 
            json_data = prediction
            with open(output_filename + '.txt', "w", encoding="utf-8-sig") as txt_file:
                txt_file.write(json_data)


def prompt(messages) : 
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        temperature=0,
        frequency_penalty=0,
        presence_penalty=0,
        messages= messages)
    
    return messages, response.choices[0].message.content


def zero_shot(input_path, output_path) : 
"""
Test zero shot model, generates the prediction of table data extraction in json format.

Parameters:
input_path : TSV or JSON table representation path
output_path : The path where the prediction is saved

Returns:
json : prediction of table data extraction
"""    
    
    client = OpenAI(api_key = 'YOUR OPENAI KEY')
    file_list = os.listdir(input_path)

    for file in file_list :
        data = {'question': [], 'answer': []}
        
        with open(input_path + file, 'r', encoding='utf-8') as file:
            table_representer = file.read()

        table_name = file.split('.')[0]

        instruction = "I'm going to convert the information in the table representer into JSON format.\n CATALYST_TEMPLATE = {'catalyst_name' : {'performance_name' : {PROPERTY_TEMPLATE}}\n PROPERTY_TEMPLATE = {'electrolyte': '', 'reaction_type': '', 'value': '', 'current_density': '', 'overpotential': '',  'potential': '','substrate': '', 'versus':''}\n performance_list = [overpotential, tafel_slope, Rct, stability, Cdl, onset_potential, current_density, potential, TOF, ECSA, water_splitting_potential, mass_activity, exchange_current_density, Rs, specific_activity, onset_overpotential, BET, surface_area, loading, apparent_activation_energy]\n. Table representer is in below \n\n "
        result = {"catalysts":[]}

        message_ = [{"role": "system", "content": instruction + table_representer}]

        catalyst_q = "Show the catalysts present in the table representer as a Python list. Answer must be ONLY python list. Not like '''python ''' Be very very very strict. Other sentences or explanation is not allowed.\n"
        question = catalyst_q
        message_.append({"role": "user", "content": question})
        _, cata_answer = prompt(message_) 
        catalyst_list = eval(cata_answer)
        data['question'].append(copy(message_))
        data['answer'].append(cata_answer)

        message_.append({"role": "assistant", "content": cata_answer}) # 다음 prompt에 이전 답 추가

        for catalyst in catalyst_list : 

            performance_template_q = "Create a CATALYST_TEMPLATE filling in the performance of {catalyst}  from the table representer, strictly adhering to the following 3 rules:\n\n Rule 1: Only include the actual existing performances from the Performance_list in the CATALYST_TEMPLATE.\n Rule 2: Set all values of the keys in PROPERTY_TEMPLATE to be " ". DO NOT INSERT ANY VALUE. BE VERY STRICT.\n Rule 3: Answer must be ONLY json format. Only display the JSON (like string not ```json). Other sentences or explanation is not allowed.".format(catalyst="'''"+catalyst+"'''")
            question = performance_template_q
            message_.append({"role": "user", "content": question})
            _, perfo_answer = prompt(message_)
            
            data['question'].append(copy(message_)) 
            data['answer'].append(perfo_answer)
            
            message_.append({"role": "assistant", "content": perfo_answer})
            property_q = 'In PROPERTY_TEMPLATE, maintain all keys, and fill in values that exist in the table representer. If there are more than two "values" for the same performance, fill in each "value" with the property template and make it into a list. If there is unit information, never create or modify additional keys, but reflect the units in the value.'
            question = property_q
            message_.append({"role": "user", "content": question})
            _, property_answer1 = prompt(message_)

            data['question'].append(copy(message_)) 
            data['answer'].append(property_answer1)
                
            message_.append({"role": "assistant", "content": property_answer1})
            property_title_caption_q = "Modify the previous version of CATALYST_TEMPLATE based solely on the title, caption according to the rules below. Only refer to the title and caption part in table representer. Strictly adhere to the following rules. \n Rule 1: If there is reaction type information in title or caption, reflect the reaction type in previous version of CATALYST_TEMPLATE accordingly. But if there isn't reaction type information in title or caption part, leave CATALYST_TEMPLATE as previous version. Be strict. \n Rule 2: If there is electrolyte information in title or caption part, reflect the electrolyte in previous version of CATALYST_TEMPLATE. But if there isn't electrolyte information in title or caption part, leave CATALYST_TEMPLATE as previous version. Be strict. \n Rule 3: Never modify the keys.  \n Rule 4: Never fill in values for any other keys except reaction_type, electrolyte. Never delete any other keys or value."
            question = property_title_caption_q
            message_.append({"role": "user", "content": question})
            _, property_answer2 = prompt(message_) 
            
            data['question'].append(copy(message_))
            data['answer'].append(property_answer2)

            message_.append({"role": "assistant", "content": property_answer1})
            delete_q ='Remove keys with no values from previous version of CATALYST_TEMPLATE.'
            question = delete_q
            message_.append({"role": "user", "content": question})
            _, delete_answer = prompt(message_)
            
            data['question'].append(copy(message_))
            data['answer'].append(delete_answer)
            
            catalyst_template = json.loads(delete_answer)
            result["catalysts"].append(catalyst_template)
            
            message_ = [{"role": "system", "content": instruction + table_representer}]
            message_.append({"role": "user", "content": catalyst_q})
            message_.append({"role": "assistant", "content": cata_answer})
            
        if len(result["catalysts"]) == 1 : 
            final_result = result["catalysts"][0]

        elif len(result["catalysts"]) > 1 : 
            final_result = result
        try :     
            with open(output_path +  table_name + ".json", "w") as json_file:
                json.dump(final_result, json_file, indent = 4)
        except : 
            with open(output_path +  table_name + ".txt", "w", encoding="utf-8-sig") as txt_file:
                txt_file.write(final_result)
            

            
