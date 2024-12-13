#step 4 - Test Prompt feature, calculate accuracy 
from pinecone import Pinecone, ServerlessSpec
import openai
import json
from app import prompt_llm
import os

openai.api_key = "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"

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




