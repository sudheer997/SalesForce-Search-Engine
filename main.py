# Import libraries and dependencies 
import logging
import os
import re
import pandas as pd
# importing required libraries
import re
import nltk
import time
from nltk.corpus import movie_reviews
import numpy as np
import string
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from tqdm import tqdm
from sklearn.utils import shuffle
nltk.download('movie_reviews')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import BM25Retriever
from haystack.utils import launch_es
launch_es()


# Define the logger
logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)

# Get the host where Elasticsearch is running, default to localhost
host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
document_store = ElasticsearchDocumentStore(host=host, username="", password="", index="document")

import xml.etree.ElementTree as ET

# Load XML file
tree = ET.parse('salesforce.stackexchange.com/Posts.xml')

# Get the root element
root = tree.getroot()

# Initialize dictionaries
questions = {}
answers = {}

# Iterate over each 'row' element
for row in root.iter('row'):
    post_type_id = row.attrib.get('PostTypeId')
    if post_type_id == "1":
        # This is a question
        question_id = row.attrib.get('Id')
        title = row.attrib.get('Title')
        body = row.attrib.get('Body')
        score = row.attrib.get('Score')
        questions[question_id] = {'title': title, 'body': body, 'score' : score}
    elif post_type_id == "2":
        # This is an answer
        answer_id = row.attrib.get('Id')
        question_id = row.attrib.get('ParentId')
        text = row.attrib.get('Body')
        text = text.strip().lower()
        text = re.sub("<.*?>", " ", text)
        score = row.attrib.get('Score')
        answer_dict = {'answer_id': answer_id, 'body': text, 'score' : score}
        if question_id in answers:
            answers[question_id].append(answer_dict)
        else:
            answers[question_id] = [answer_dict]


porter_stemmer = PorterStemmer()
punctuations = set(string.punctuation)
stopwords=stopwords.words('english')
stopwords.remove('no')
stopwords.remove('nor')
stopwords.remove('not')
for item in stopwords:
    if "n't" in item:
        stopwords.remove(item)

def process_sentence(sentence):
    if sentence == np.NaN:
      return
    sentence = sentence.lower()
    # Remove trailing spaces
    sentence = sentence.strip()
    
    # Remove HTMl tages from the text
    sentence = re.sub("<.*?>", " ", sentence)
    
     # Remove special characters and numbers in the string
    sentence = re.sub(r'[^\w\s]',' ',sentence)
    sentence = re.sub(" \d+", " ",sentence)
    
    # Remove \n and \t in sentence
    sentence = re.sub("\n", "", sentence)
    sentence = re.sub("\t", "", sentence)
    sentence = ''.join(ch for ch in sentence if ch not in punctuations)
    
    # Remove stop words and word has length less than 3
    tokenized_sentence = sentence.split(" ")
    processed_review = [token for token in tokenized_sentence if token and token not in stopwords and len(token) >= 3 and not token.isdigit()]
    # Get the stem the word
    processed_review = " ".join(list(map(lambda x: porter_stemmer.stem(x), processed_review)))
#     processed_review = " ".join(processed_review)
    return processed_review

start_time = time.time()
bm25_processed_docs = []
for item in questions:
  title = questions[item]["title"]
  body = questions[item]["body"]
  processed_text = process_sentence(title + body)
  score = questions[item]["score"]
  bm25_processed_docs.append({"content" : processed_text, "meta": {"question_id": item, "score": score}})
end_time = time.time()
print("Time taken to prepocess the text data for BM25 model : ", end_time - start_time)

# Define the elastic search document store


# Get the host where Elasticsearch is running, default to localhost
host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
elastic_document_store = ElasticsearchDocumentStore(host=host, username="", password="", index="document-dim", similarity="cosine", recreate_index=True)

# Write the processed document to the elastic search document store
start_time = time.time()
elastic_document_store.write_documents(bm25_processed_docs)
print("Time taken to write and index the documents in Elastic search datastore for the BM25 model : ", time.time() - start_time)

print(f"Loaded {elastic_document_store.get_document_count()} documents")

# Define the BM25 Retriever
bm25_retriever = BM25Retriever(elastic_document_store)

for item in bm25_retriever.retrieve(process_sentence("What ports and IP addresses does Live Agent need for an agent to be able to connect to the chat from inside a corporate network."), top_k=10):
  print(item.to_dict())