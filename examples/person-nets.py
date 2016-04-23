import pandas as pd
import sys
sys.path.insert(0,'../')
from network_utils import *

print 'Loading, indexing, and grouping data...'
#read in all coded data
answers = pd.read_csv('../data/merged_all.tsv', sep='\t')
#set indices
answers = answers.set_index(['uni', 'Participant', 'Start'])
#group codes at the person level
people = answers.groupby(level=['uni', 'Participant']).any()

def jaccard(a, b):
    n = len(a)
    union = 0.0
    intersection = 0.0
    
    for i in range(0, n):
        if a[i] & b[i]:
            union = union + 1
            intersection = intersection + 1
        elif a[i] | b[i]:
            intersection = intersection + 1
    
    result = 0.0
    if intersection > 0:
        result = union / intersection
    
    return result

def all_v_all_jaccard_sim(df):
    #add a unique ID column
    n = len(df) + 1
    idx = range(1, n)
    df['uid'] = idx
    id_map = df[['uid']]
    df = df.set_index(['uid'])
    
    data = df.transpose()
    result = pd.DataFrame(0, index=idx, columns=idx)
    
    for i in range(1, n):
        if i % 50 == 0:
            print (i*100.0)/n, '% of', n, 'done...'
        for j in range(1, i):
            result.ix[i, j] = jaccard(data[i], data[j])
    
    return (id_map, result)

print 'Computing person v person Jaccard similarity...'
(m, r) = all_v_all_jaccard_sim(people)
r.to_csv('../data/people_jaccard.tsv', sep='\t')
m.to_csv('../data/people_jaccard_ids.tsv', sep='\t')

print 'Computing answer v answer Jaccard similarity...'
(m, r) = all_v_all_jaccard_sim(answers)
r.to_csv('../data/ans_jaccard.tsv', sep='\t')
m.to_csv('../data/ans_jaccard_ids.tsv', sep='\t')

print 'Done!'