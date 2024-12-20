import os
import re
import openai
import json
import streamlit as st
from pinecone import Pinecone

# Constants
TOKEN_SIZE_35 = 3500
TOKEN_SIZE_4 = 15000

# Initialize API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "pcsk_zEUE2_TZQDwfpndSzzg3rKkQLQXvRX7Rs6DA4hgGwZwB4L6AwAgXTNrQdSgZskYbnPBN3")

# Validate API keys
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not set. Please set the OPENAI_API_KEY environment variable.")
if not PINECONE_API_KEY:
    raise ValueError("Pinecone API key not set. Please set the PINECONE_API_KEY environment variable.")

# Configure APIs
openai.api_key = OPENAI_API_KEY
pc = Pinecone(api_key=PINECONE_API_KEY)

# Connect to Pinecone index
index_name = "json-vector-index"
index = pc.Index(index_name)

# Functions
def generate_embeddings(text):
    """Generate embeddings using OpenAI."""
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']

def similarity_search(query, top_k=100):
    """Query Pinecone for similar documents."""
    query_embedding = generate_embeddings(query)
    search_results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    return search_results['matches']

def fetch_documents_as_string(index, match_result, model_name="3.5"):
    """Fetch documents and combine them as a string."""
    token_size = TOKEN_SIZE_35 if model_name == "3.5" else TOKEN_SIZE_4
    doc_ids = [match['id'] for match in match_result]
    documents = index.fetch(ids=doc_ids)
    cur = 0
    result_lines = []

    for doc_id, doc_info in documents['vectors'].items():
        content = doc_info['metadata'].get('text', "No text found")
        cur += len(content.split(" "))
        if cur > token_size + 200:
            break
        result_lines.append(f"Document ID: {doc_id}\nContent: {content}\n")
    
    return "\n\n".join(result_lines)

def run_llm(query, context, model_name="3.5"):
    """Run LLM on the retrieved documents."""
    model = "gpt-3.5-turbo-0125" if model_name == "3.5" else "chatgpt-4o-latest"
    prompt = f"Query: {query}\n\nContext:\n{context}\n\nAnswer:"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "Given context, answer the question."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

def query_pipeline(user_query, top_k=100, model_name="3.5"):
    """Complete pipeline: query → similarity search → LLM."""
    matches = similarity_search(user_query, top_k=top_k)
    context = fetch_documents_as_string(index, matches, model_name=model_name)
    llm_output = run_llm(user_query, context, model_name=model_name)
    return llm_output

def prompt_llm(query, model_name="3.5"):
    """Wrapper function for LLM query."""
    query = query + ", only URL links separated by character '|'"
    response = query_pipeline(query, top_k=100, model_name=model_name)
    links = [link.strip() for link in response.split("|") if link.strip()]
    return links

def main():
    # Add a custom title with styling
    st.markdown(
        """
        <style>
        .title {
            font-size: 36px;
            font-weight: bold;
            color: #007BFF; /* Blue color */
            text-align: center;
        }
        .subtitle {
            font-size: 18px;
            color: #6c757d;
            text-align: center;
        }
        .footer {
            font-size: 14px;
            color: #6c757d;
            text-align: center;
            margin-top: 30px;
        }
        .stButton button {
            font-size: 18px !important;
            padding: 10px 20px !important;
            background-color: #007BFF !important;
            color: white !important;
            border: none !important;
            border-radius: 5px !important;
            cursor: pointer !important;
        }
        .stButton button:hover {
            background-color: #0056b3 !important; /* Darker blue on hover */
        }
        </style>
        <div class="title">Retrieval of Products using LLM</div>
        <div class="subtitle">A powerful tool to find products quickly and effectively</div>
        """,
        unsafe_allow_html=True
    )

    # Add a horizontal divider
    st.markdown("---")

    # Input query with a description
    st.markdown("### 🛒 Enter Your Product Query:")
    query = st.text_input("For example: 'Get me links of headphones'")

    # Model selection dropdown with icons
    st.markdown("### 🤖 Select the LLM Model:")
    model = st.selectbox("Choose the best model for your query:", ["3.5", "4.0"])

    # Add a larger, styled button
    submit_button = st.button("🔍 Search")

    # Add spacing
    st.markdown("<br>", unsafe_allow_html=True)

    # Process the query when the button is clicked
    if submit_button:
        if not query.strip():
            st.warning("Please enter a query before submitting!")
        else:
            st.write("Processing your query...")
            with st.spinner("Querying the model..."):
                try:
                    # Call the LLM function (replace with actual logic)
                    result = prompt_llm(query, model_name=model)

                    # Display results
                    st.success("Query processed successfully!")
                    st.markdown("### 🎯 Results:")
                    for link in result:
                        st.markdown(f"- 🔗 [{link}]({link})")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    # Add a footer
    st.markdown(
        """
        <div class="footer">Powered by OpenAI and Pinecone | Built with ❤️ using Streamlit</div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

