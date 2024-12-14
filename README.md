# LLM Product Retrieval

This repository demonstrates an end-to-end system integrating Natural Language Processing (NLP), Large Language Models (LLMs), and Pinecone (vector database) to enable efficient product data querying. The system collects product data via web scraping, preprocesses it, and provides a user-friendly querying interface using Streamlit.

---

## Features

- **Web Scraping**: Dynamically collects product data from specified sources.
- **Data Preprocessing**: Tokenizes and cleans data to improve processing efficiency.
- **Vector Embeddings**: Utilizes OpenAI embeddings for product descriptions.
- **Semantic Search**: Facilitates context-aware search through Pinecone.
- **Streamlit UI**: Provides an intuitive interface for querying product information.
- **Model Integration**: Leverages GPT models for natural language query responses.

---

## Tech Stack

- **Python Libraries**: Selenium, BeautifulSoup, NLTK, OpenAI API, Pinecone, Streamlit
- **LLMs**: OpenAI's GPT-3.5 and GPT-4
- **Vector Database**: Pinecone for similarity-based retrieval

---

## Prerequisites

- Python 3.10 or later
- OpenAI API key
- Pinecone API key

---

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/jaissica/LLM_Product_Retrieval.git
   cd LLM_Product_Retrieval
   conda create --name rag_retrieve python=3.10 -y
   conda activate rag_retrieve
   pip install -r requirements.txt
   ```

