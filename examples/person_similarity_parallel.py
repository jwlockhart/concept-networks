# @author Jeff Lockhart <jwlock@umich.edu>
# Example script computing the pairwise similarity of people and/or 
# responses in a sample. Parallel implementation using ipyparallel. 
# 
# version 1.1

import pandas as pd
import ipyparallel
import sys
sys.path.insert(0,'../')
from network_utils import *

print('Creating cluster client and view...')
c = ipyparallel.Client()
view = c.load_balanced_view()

print('Loading, indexing, and grouping data...')
#read in all coded data
answers = pd.read_csv('../data/merged_all.tsv', sep='\t')
#set indices
answers = answers.set_index(['uni', 'Participant', 'Start'])
#group codes at the person level
people = answers.groupby(level=['uni', 'Participant']).any()


def parallel_jaccard(dic):
    '''Map function to be used in parallel computation of 
    all v all jaccard similarity. Individual pairwise comparisons
    proved to be too small of jobs for decent parallel computation.
    Thus, each job compares one element i to all other elements 
    in range(0, i).
    For space efficiency, a dictionary of non-zero scores is returned
    instead of an adjacency matrix.
    '''
    #what column to use as our reference
    i = dic['i']
    #our data
    data = dic['dat']
    a = data[i]
    #the number of codes we're comparing across columns
    codes = data.shape[0]

    output = {}
    
    #loop over all the columns we need to compare
    for k in range(0, i):
        #temp variables
        union = 0.0
        intersection = 0.0
        b = data[k]
        #loop over the codes to compare in these cols
        for j in range(0, codes):
            #if at least one has a code
            if a[j] | b[j]:
                intersection = intersection + 1
                #if both have the code
                if a[j] & b[j]:
                    union = union + 1
        #only save scores > 0
        if (intersection > 0) & (union > 0):
            output[k] = (union / intersection) 
            
    return {'i':i, 'Jaccard':output}

def list_people_data(df):
    '''Generates a list of input to be mapped to parallel_jaccard().'''
    #add a unique ID column
    n = len(df)
    idx = range(0, n)
    df['uid'] = idx
    id_map = df[['uid']]
    df = df.set_index(['uid'])
    #transpose data frame for easier indexing
    data = df.transpose()
    result = []
    #create a list of jobs where each job is an element and a
    #set of other elements to compare it with.
    for i in range(0, n):
        dic = {'i':i, 'dat':data.ix[:,0:i+1]}
        result.append(dic)
            
    return (id_map, result)


print('Creating job list for person v person Jaccard similarity...')
(id_map, result) = list_people_data(people)

print('Saving uids...')
ids = id_map.reset_index()
ids.to_csv('../data/people_jaccard_ids.tsv', sep='\t', index=False)

print('Computing person v person similarity...')
output = view.map_async(parallel_jaccard, result)
output.wait_interactive()
print('Computations finished!')

print('Stitching results together...')
tmp = []
for o in output:
    tmp.append(pd.DataFrame.from_dict(o))
tmp = pd.concat(tmp)

#now make things pretty for saving
tmp['j'] = tmp.index
tmp = tmp[['i','j','Jaccard']]
print('Saving results...')
tmp.to_csv('../data/people_jaccard.tsv', sep='\t', index=False)
print('Done!')

print('Creating job list for answer v answer Jaccard similarity...')
(m2, r2) = list_people_data(answers)

print('Saving uids...')
ids = m2.reset_index()
ids.to_csv('../data/answers_jaccard_ids.tsv', sep='\t', index=False)

print('Computing answer v answer similarity...')
output2 = view.map_async(parallel_jaccard, r2)
output2.wait_interactive()
print('Computations finished!')

print('Stitching results together...')
tmp = []
for o in output2:
    tmp.append(pd.DataFrame.from_dict(o))
tmp = pd.concat(tmp)

#now make things pretty for saving
tmp['j'] = tmp.index
tmp = tmp[['i','j','Jaccard']]
print('Saving results...')
tmp.to_csv('../data/answers_jaccard.tsv', sep='\t', index=False)
print('All Done!')