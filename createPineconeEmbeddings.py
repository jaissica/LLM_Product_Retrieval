# Step 3 - Create pinecone
from pinecone import Pinecone, ServerlessSpec
from nltk.tokenize import word_tokenize
import re
import openai
import json
import os
import nltk


openai.api_key = "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"

# Initialize Pinecone
pc = Pinecone(
    api_key="pcsk_zEUE2_TZQDwfpndSzzg3rKkQLQXvRX7Rs6DA4hgGwZwB4L6AwAgXTNrQdSgZskYbnPBN3"
)

# Create or connect to a Pinecone index
index_name = "json-vector-index"
if index_name not in pc.list_indexes():
    pc.create_index(index_name, dimension=1536,spec=ServerlessSpec(
            cloud="aws",  # Use 'gcp' or 'aws' based on your environment
            region="us-east-1"  # Replace with your desired region
        ))  # Assuming OpenAI embeddings
index = pc.Index(index_name)

#tokenize
def tokenize(f):
    fstr = str(f)
    final = re.sub(r'[\[\]\{\}\(\)]', '\n', fstr)
    final = re.sub(r'[\'\"]', '', final)
    final = re.sub(r"\\u[a-fA-F0-9]{4}", " ", final)
    final = re.sub(r":", " ", final)
    final = re.sub(r",", " ", final)
    
    words = word_tokenize(final)
    print(words)
    rm_stop = []
    for w in words:
        if w not in nltk.corpus.stopwords.words('english'):
            rm_stop.append(w)

    return rm_stop

# Function to extract meaningful content from JSON
def extract_text_from_json(json_data, fields_to_extract=None):
    tokens = tokenize(json_data)
    return " ".join(tokens)

# Function to generate embeddings
def get_embeddings(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return openai.Embedding.create(input = [text], model=model).data[0].embedding

# Function to parse JSONs and upload vectors to Pinecone
def process_jsons_and_upload(json_list, fields_to_extract=None):
    for idx, json_data in enumerate(json_list):
        # Extract text from JSON
        content = extract_text_from_json(json_data, fields_to_extract)
        # Generate embeddings
        embedding = get_embeddings(content)
        # Use a unique ID for Pinecone (e.g., index or key)
        json_id = f"doc-{idx}"
        # Upsert data into Pinecone
        index.upsert([(json_id, embedding, {"text": content})])
        print(f"Uploaded JSON ID: {json_id}")

def read_file(path):
    f = open(path, "r")
    prod = json.load(f)
    return prod

def tokenize(f):
    fstr = str(f)
    final = re.sub(r'[\[\]\{\}\(\)]', '\n', fstr)
    final = re.sub(r'[\'\"]', '', final)
    final = re.sub(r"\\u[a-fA-F0-9]{4}", " ", final)
    final = re.sub(r":", " ", final)
    final = re.sub(r",", " ", final)
    
    words = word_tokenize(final)
    print(words)
    rm_stop = []
    for w in words:
        if w not in nltk.corpus.stopwords.words('english'):
            rm_stop.append(w)

    return rm_stop

# Example JSON list
json_list = [
    {"title": "Document 1", "body": "This is the content of the first document."},
    {"title": "Document 2", "body": "Here is some other content for the second document."},
    {"title": "Document 3", "description": "Description of document 3", "body": "And its detailed content."}
]

# Specify fields to extract from the JSON (optional)
fields_to_extract = ["about_us"]

total = 0
all_jsons = []
for fold in ["Headphones", "Soundbars", "Speakers"]:
    fold_count = 0
    for fn in os.listdir(os.path.join("./Final_Corpus/", fold)):
        file_path = os.path.join("./Final_Corpus/", fold, fn)
        d =  read_file(file_path)
        d = d[fn.strip(".json")] 
        all_jsons.append(d)

# Process and upload the JSONs
process_jsons_and_upload(all_jsons, fields_to_extract)