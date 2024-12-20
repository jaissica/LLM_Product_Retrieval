#step 4 - Test Prompt feature, calculate accuracy 
from pinecone import Pinecone, ServerlessSpec
import openai
import json
from app import prompt_llm
import os

openai.api_key = "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"

# # Test with an empty query
# query = ""  
# # Assert that the query is not empty or None
# assert query and query.strip(), "Query cannot be empty or None"
# response_links_model_3 = prompt_llm(query, model_name="3.5")

# validate if the result has SONY links
response_links_model_3 = prompt_llm("Get me links of headphones", model_name="3.5")
assert any("sony" in link.lower() for link in response_links_model_3), "No Sony link found in the results"



# View for results
# testing with gpt-3.5-turbo-0125 model
print("========================")
response_links_model_3 = prompt_llm("Get me links of headphones", model_name="3.5")
print("\n".join(response_links_model_3))

print("========================")
response_links_model_3 = prompt_llm("Get me links of speakers", model_name="3.5")
print("\n".join(response_links_model_3))


# testing with gpt chatgpt-4o-latest model
print("========================")
response_links_model_3 = prompt_llm("Get me links of headphones", model_name="4.0")
print("\n".join(response_links_model_3))

print("========================")
response_links_model_3 = prompt_llm("Get me links of speakers", model_name="4.0")
print("\n".join(response_links_model_3))




