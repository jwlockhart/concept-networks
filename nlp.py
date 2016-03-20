# utility functions for NLP-based similarity metrics
# version 1.0
# code modified from: 
# https://stackoverflow.com/questions/8897593/similarity-between-two-text-documents

import nltk 
import string
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) 
                              for char in string.punctuation)

def stem_tokens(tokens):
    '''word stems'''
    return [stemmer.stem(item) for item in tokens]

def normalize(text):
    '''remove punctuation, lowercase, stem'''
    clean = text.lower().translate(remove_punctuation_map)
    tokens = nltk.word_tokenize(clean)
    return stem_tokens(tokens)

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

def cosine_sim(texts):
    '''return cosine similarity of an array of documents, such that
    any individual similarity is conditional on not just the two
    vectors being compared, but all other vectors present.
    '''
    tfidf = vectorizer.fit_transform(texts)
    return (tfidf * tfidf.T).A

def cosine_sim_2(text1, text2):
    '''return cosine similarity of two documents. Will be higher
    than the similarity between those documents in cosine_sim_all
    because that includes more documents in the space.
    '''
    return cosine_sim_all([text1, text2])[0,1]

def cosine_sim_pd(docs, codes):
    '''convert output to pandas dataframe with labels.
    '''
    cosine_similarities = cosine_sim(docs)
    return pd.DataFrame(cosine_similarities, columns=codes, 
                      index=codes)

def make_docs(df, code_cols, text_col='Excerpt Copy'):
    '''Create documents containing all text from text_col matching 
    each code in code_cols. 
    '''
    #a list of one string for each code
    documents = []

    #concat all strings for each code into a single document
    for code in code_cols:
        #select matching subset
        tmp = df[df[code] == True]
    
        #select the text of answers
        answers = tmp[text_col]
    
        #join all the answers into one document
        merged = ' .\n'.join(answers)
    
        documents.append(merged)
        
    return documents