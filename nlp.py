

# code modified from 
# https://stackoverflow.com/questions/8897593/similarity-between-two-text-documents

import nltk 
import string
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

def cosine_sim_2(text1, text2):
    '''return cosine similarity of two documents. Will be higher
    than the similarity between those documents in cosine_sim_all
    because that includes more documents in the space.
    '''
    tfidf = vectorizer.fit_transform([text1, text2])
    print (tfidf * tfidf.T).A
    return ((tfidf * tfidf.T).A)[0,1]

def cosine_sim_all(texts):
    '''return cosine similarity of an array of documents, such that
    any individual similarity is conditional on not just the two
    vectors being compared, but all other vectors present.
    '''
    tfidf = vectorizer.fit_transform(texts)
    return (tfidf * tfidf.T).A