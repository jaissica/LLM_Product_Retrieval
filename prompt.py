#step 4 - Test Prompt feature, calculate accuracy 
from pinecone import Pinecone, ServerlessSpec
import openai
import json
import os
from app import prompt_llm

openai.api_key = "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"


def read_file(path):
    f = open(path, "r")
    prod = json.load(f)
    return prod

#parsing
def parse_txt_to_dict(file_path):
    result_dict = {}
    current_category = None
    current_query = None
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            if line.startswith('# ') and not line.startswith('##'):
                # Set category
                current_category = line[2:].strip()
                result_dict[current_category] = {}
            elif line.startswith('##'):
                # Set query
                current_query = line[2:].strip()
                if current_category:
                    result_dict[current_category][current_query] = []
            elif line and current_category and current_query:
                # Add link to the current query
                result_dict[current_category][current_query].append(line)
    
    return result_dict

# calculate accuracy
def get_acurracy_mat(query_data, query_res):
    accuracy = defaultdict(dict)
    for type, ques in parsed_data.items():
        for q in ques:
            
            pred = set(query_res[type][q])
            truth = set(query_data[type][q])
            accuracy[type][q] = {"true_positive" : 0, "false_positive" : 0, "total" : len(truth)}
            for p in pred:
                if p in truth:
                    accuracy[type][q]["true_positive"]+= 1
                else :
                    accuracy[type][q]["false_positive"]+= 1
    return accuracy


# Example usage
file_path = 'Proj_data.txt' 
parsed_data = parse_txt_to_dict(file_path)
print(parsed_data)

from collections import defaultdict
ans35 = defaultdict(dict)
ans4 = defaultdict(dict)

for type, ques in parsed_data.items():
    for q in ques:
        ans35[type][q] = prompt_llm(q )
        ans4[type][q] = prompt_llm(q, "4")

# functions to calculate accuracy
print("-------")
print("GPT 3.5 Accuracy")
print(get_acurracy_mat(parsed_data, ans35))
print("-------")
print("GPT 4 Accuracy")
print(get_acurracy_mat(parsed_data, ans4))