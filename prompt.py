#step 4 - Test Prompt feature, calculate accuracy 
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
import openai
import json
import os

openai.api_key = "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"

content = """
context : 

Joseph Vissarionovich Stalin[f] (born Dzhugashvili;[g] 18 December [O.S. 6 December] 1878 – 5 March 1953) was a Soviet politician and 
revolutionary who led the Soviet Union from 1924 until his death in 1953. He held power as General Secretary of the Communist Party 
from 1922 to 1952 and as Chairman of the Council of Ministers from 1941 until his death. Initially governing as part of a collective 
leadership, Stalin consolidated power to become a dictator by the 1930s. He codified his Leninist interpretation of Marxism as 
Marxism–Leninism, while the totalitarian political system he established became known as Stalinism.

----

question:
when was stalin born?
"""
response = openai.chat.completions.create(
    model="gpt-3.5-turbo",  # or "gpt-4" or gpt-3
    messages=[
        {"role": "system", "content": "Given context answer the question"},
        {"role": "user", "content": content}
    ]
)
# print(response)

TOKEN_SIZE_35 = 3500
TOKEN_SIZE_4 = 15000

# Initialize OpenAI API
ai = OpenAI(api_key="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")

# Initialize Pinecone
pc = Pinecone(api_key="pcsk_czo9P_UXvKtN4Ce16nuPg9Ae6ctjBgLBPYySuCnTubvEme3RbHR9F8BDNmRpbR1zhY585")

# Connect to Pinecone index
index_name = "json-vector-index"
index = pc.Index(index_name)

# Function to generate embeddings using OpenAI
def generate_embeddings(text):
    response = ai.embeddings.create(
        model="text-embedding-ada-002",  # Use the correct embedding model
        input=text
    )
    return response.data[0].embedding

# Function to query Pinecone for similar documents
def similarity_search(query, top_k=100):
    # Generate embedding for the query
    query_embedding = generate_embeddings(query)
    # Search Pinecone index for similar vectors
    search_results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True  # Include metadata if needed
    )
    return search_results['matches']

# Function to run an LLM on the retrieved documents
def run_llm(query, context, model_name = "3.5"):
    # Combine the query and context
    prompt = f"Query: {query}\n\nContext:\n{context}\n\nAnswer:"
    response = ""
    model = "gpt-3.5-turbo-0125" if model_name == "3.5" else "chatgpt-4o-latest"
    response = openai.chat.completions.create(
        model= model,  # or "gpt-4"
        messages=[
            {"role": "system", "content": "Given context answer the question"},
            {"role": "user", "content": prompt}
        ]
    )
    return response

def fetch_documents_as_string(index, match_result, model_name = "3.5"):
    token_size = TOKEN_SIZE_35 if model_name == "3.5" else TOKEN_SIZE_4
    # Extract IDs from match result
    doc_ids = [match['id'] for match in match_result]
    # Fetch documents from Pinecone
    documents = index.fetch(ids=doc_ids)
    cur = 0
    # Build the result string
    result_lines = []
    for doc_id, doc_info in documents['vectors'].items():
        # print(len(doc_info['metadata'].get('text', "No text found").split(" ")))
        cur += len(doc_info['metadata'].get('text', "No text found").split(" "))
        if cur > token_size + 200:
            break
        content = doc_info['metadata'].get('text', "No text found")
        result_lines.append(f"Document ID: {doc_id}\nContent: {content}\n")

    return "\n\n".join(result_lines)

# Complete pipeline: query → similarity search → LLM
def query_pipeline(user_query, top_k=100, model_name = "3.5"):
    # Step 1: Retrieve similar documents
    matches = similarity_search(user_query, top_k=top_k)
    # Step 2: Combine retrieved contexts
    context = fetch_documents_as_string(index, matches, model_name = model_name)
    # Step 3: Run the query with LLM
    llm_output = run_llm(user_query, context, model_name = model_name)
    return llm_output

# Example Usage
def prompt_llm(query, model_name= "3.5"):
    query = query + ", only url links seperated by chracter '|'"
    response = query_pipeline(query, top_k=100, model_name = model_name)
    res = response.choices[0].message.content
    final = res.split("|")
    final = [link.replace(" ", "") for link in final]
    if "" in final:
        final.remove("")
    return final

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

# Testing the prompt feature
prompt_llm("Get me links of headphones", model_name="4")
print("-------")
res = response.choices[0].message.content
final = res.split("|")
total = 0
all_jsons = []
for fold in ["Headphones", "Soundbars", "Speakers"]:
    fold_count = 0
    for fn in os.listdir(os.path.join("./Final_Corpus/", fold)):
        file_path = os.path.join("./Final_Corpus/", fold, fn)
        d =  read_file(file_path)
        print(d[fn.strip(".json")]["link"])
    print()

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

print("-------")
get_acurracy_mat(parsed_data, ans35)
print("-------")
get_acurracy_mat(parsed_data, ans4)