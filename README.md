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
```
2. **Create a Conda Environment**:
```bash
conda create --name rag_retrieve python=3.10 -y
conda activate rag_retrieve
```
3. **Install Dependencies**:
 ```bash
 pip install -r requirements.txt
 ```
4. Configure API Keys: Add your OpenAI and Pinecone API keys to the environment variables or .env file.

## Usage
### Data Collection and Processing

1. **Run Web Scraper**:
```bash
python webScraper.py
```
Already scraped data is included in the repository.
   
2. **Preprocess data**:
```bash
python preprocessing.py
```
   
3. **Create Pinecone Index**:
```bash
python createPineconeEmbeddings.py
```
 Note: If re-running, ensure the index name is unique.

 ### Run the Application
 
4. **Launch Streamlit Interface**:
```bash
streamlit run app.py
```

5. **Unit Tests: Run tests to validate the system**:
```bash
python test.py
```
   
6. **Query Accuracy: Test query performance**:
```bash
python prompt.py
```

## Data Sources

- [SONY Headphones](https://electronics.sony.com/audio/headphones/c/all-headphones)
- [SONY Soundbars](https://electronics.sony.com/audio/soundbars/c/all-soundbars)
- [SONY Speakers](https://electronics.sony.com/audio/speakers/c/all-speakers)


## Key Scripts
1. webScraper.py: Web scraping for product attributes like price, EMI, and specifications.
2. preprocessing.py: Tokenizes and preprocesses scraped data.
3. createPineconeEmbeddings.py: Generates vector embeddings and uploads to Pinecone.
4. app.py: Runs the Streamlit UI for querying.
5. test.py: Contains unit tests for edge cases.
6. prompt.py: Evaluates query accuracy and response generation.

## Results
### Model Performance:
1. GPT-4 significantly outperformed GPT-3.5 in accuracy and relevance.
2. Limitations in numerical queries and data inconsistencies impacted results.
 
