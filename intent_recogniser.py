import pandas as pd
import random
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from intent_dict import intent_dict
from logger import logger
from intent_dict import intent_dict

stemmer = PorterStemmer()
qa_csv_path = "resources/QAdataset.csv"

# Function to process text: tokenization and stemming
def process_text(text):
    tokens = text.lower().split()
    tokens = [stemmer.stem(token) for token in tokens if token.isalpha()]
    return tokens

# Function to build the term-document matrix for a given dataset
def build_term_document_matrix(dataset):
    vocabulary = set()
    doc_term_matrix = {}
    
    if isinstance(dataset, pd.DataFrame):  # Handle QA CSV dataset
        for index, row in dataset.iterrows():
            question_id = row["QuestionID"]
            question_text = row["Question"]
            
            tokens = process_text(question_text)
            term_freq = {}
            for term in tokens:
                term_freq[term] = term_freq.get(term, 0) + 1
            doc_term_matrix[question_id] = term_freq
            vocabulary.update(term_freq.keys())
    
    elif isinstance(dataset, dict):  # Handle intent_dict directly
        for intent, inputs in dataset.items():
            for input in inputs:
                # Generate unique ID for each question
                question_id = f"{intent}_{inputs.index(input)}"  
                
                tokens = process_text(input)
                term_freq = {}
                for term in tokens:
                    term_freq[term] = term_freq.get(term, 0) + 1
                doc_term_matrix[question_id] = term_freq
                vocabulary.update(term_freq.keys())
    
    vocabulary = sorted(vocabulary)
    
    td_matrix_df = pd.DataFrame(0, index=doc_term_matrix.keys(), columns=vocabulary)
    for doc_id, term_freq in doc_term_matrix.items():
        for term, freq in term_freq.items():
            if term in td_matrix_df.columns:
                td_matrix_df.at[doc_id, term] = freq
    
    return td_matrix_df, vocabulary

# Function to process query and convert it into a vector based on the vocabulary
def process_query(query, vocabulary):
    tokens = process_text(query)
    query_freq = {term: tokens.count(term) for term in tokens if term in vocabulary}
    return pd.Series([query_freq.get(term, 0) for term in vocabulary], index=vocabulary)

# Function to get top N most similar documents from the term-document matrix
def get_top_n_documents(query_vector, matrix, threshold=0.3, n=10):
    query_vector = query_vector.values.reshape(1, -1)
    similarities = cosine_similarity(query_vector, matrix).flatten()
    top_n_indices = similarities.argsort()[-n:][::-1]
    
    # Filter results by similarity threshold
    top_documents = [(matrix.index[idx], similarities[idx]) for idx in top_n_indices if similarities[idx] >= threshold]
    return top_documents

# Function to recognize the intent of the user query
def recognise(user_query):
    # Load the original dataset and set up columns
    data = pd.read_csv(qa_csv_path, usecols=[0, 1, 2])
    data.columns = ["QuestionID", "Question", "Answer"]

    # Load intent dictionary and build term-document matrices
    qa_td_matrix_df, vocabulary = build_term_document_matrix(data)
    intent_td_matrix_df, custom_vocabulary = build_term_document_matrix(intent_dict)

    # Process query with the original dataset vocabulary first
    query_vector = process_query(user_query, vocabulary)
    
    # Check original dataset first
    top_qa_results = get_top_n_documents(query_vector, qa_td_matrix_df, threshold=0.877)

    if top_qa_results:
        # Take the top document with the highest similarity (first in sorted list)
        doc_id, similarity = top_qa_results[0]
        
        # Instead of returning the answer, return the intent in the form of "print_[id]"
        logger.debug(f"Most relevant document in original dataset (Similarity: {similarity:.4f}):")
        return f"print_{doc_id}"  # The intent is the QuestionID prefixed by "print_"
    else:
        logger.debug("No high similarity matches found in QA dataset. Checking custom dataset...")

    # Fallback to custom dataset if no original results exceed the threshold
    query_vector = process_query(user_query, custom_vocabulary)
    top_intents = get_top_n_documents(query_vector, intent_td_matrix_df, threshold=0.5)
    
    if top_intents:
        logger.debug("Top relevant document(s) in custom dataset:")
        for doc_id, similarity in top_intents:
            intent = doc_id.split('_')[0]  # Extract the action from the question ID
            
            logger.debug(f"Intent ID: {doc_id}, Similarity: {similarity:.4f}, Action: {intent}")
            return intent  # This needs to be moved later on to allow multiple intent functionality
    else:
        return "none_found"

# # Example usage
# user_input = "Hello, I need help with booking a flight"
# qa_csv_path = "QAdataset.csv"
# response = recognise(user_input, qa_csv_path, intent_dict)
# print(response)
