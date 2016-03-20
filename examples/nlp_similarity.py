# @author Jeff Lockhart <jwlock@umich.edu>
# Example script for computing intercoder reliability
# assumptions:
# - binary data
# - 2 coders
# - no missing values
# version 1.0

import pandas as pd
import sys

sys.path.insert(0,'../')
import nlp

argv = sys.argv
if len(argv) != 2:
    print 'Please run this script with exactly 1 argument.\n$ nlp_similarity.py [infile.tsv]'
    sys.exit()

#name of the column with the text of answers
text_col = 'Excerpt Copy'

#names of the columns with the codes we care about
code_cols = ['culture_problem', 
             #'culture_absent', 
             'culture_solution', 
             'culture_helpless', 
             'culture_victim', 
             'cishet_problem', 
             'cishet_victim', 
             'cishet_solution', 
             #'cishet_absent', 
             'cishet_helpless', 
             'sgm_victim', 
             'sgm_problem', 
             'sgm_helpless', 
             #'sgm_absent', 
             'sgm_solution', 
             'school_problem', 
             'school_solution', 
             #'school_absent', 
             'school_victim', 
             'school_helpless', 
             'community_problem', 
             'community_solution', 
             'community_helpless', 
             #'community_absent', 
             'community_victim']
    
    
print 'Loading data file...'
df = pd.read_csv(argv[1], sep='\t')

'''Remove the labels Dedoose adds. Generally, they follow
the form 'Question: xxx; Answer:'. In my particular data,
all questions 'xxx' match the regex 'Q\d*\w?'. You will need to 
modify this regex to work with your question labels. Alternatively, 
you could omit this step, but then the similarity of your documents
would be biased in favor of those with more of the same questions.
'''
df = df.replace({'Question: Q\d*\w?; Answer:': ''}, regex=True)

print 'Combining answers from each code into documents...'
documents = nlp.make_docs(df, code_cols, text_col)

print 'Calculating cosine similarity between all codes...'
result = nlp.cosine_sim_pd(docs=documents, codes=code_cols)

print 'Results:'
print result

print "\nDone!"