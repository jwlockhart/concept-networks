# @author Jeff Lockhart <jwlock@umich.edu>
# Example script computing the pairwise similarity of people and/or 
# responses in a sample. Serial implementation. 
# Time complexity: O((n^2 -n)/2) 
# Space complexity: O(n^2)
# (i.e. this is very slow for medium data sets--see the parallel 
# implementation for speed).
# version 1.2

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

print 'Computing person v person Jaccard similarity...'
(m, r) = all_v_all_jaccard_sim(people)
r.to_csv('../data/people_jaccard.tsv', sep='\t')
m.to_csv('../data/people_jaccard_ids.tsv', sep='\t')

print 'Computing answer v answer Jaccard similarity...'
# Warning: at n = 9,000, this is a 12+ hour computation and a 350 MB file
(m, r) = all_v_all_jaccard_sim(answers)
r.to_csv('../data/ans_jaccard.tsv', sep='\t')
m.to_csv('../data/ans_jaccard_ids.tsv', sep='\t')

print 'Done!'