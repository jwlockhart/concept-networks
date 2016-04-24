# @author Jeff Lockhart <jwlock@umich.edu>
# Example script computing the pairwise similarity of people and/or 
# responses in a sample. Parallel implementation using ipyparallel. 
# 
# version 0.1

import pandas as pd
import ipyparallel
import sys
sys.path.insert(0,'../')
from network_utils import *

print 'Creating cluster client and view...'
c = ipyparallel.Client()
view = c.load_balanced_view()

print 'Loading, indexing, and grouping data...'
#read in all coded data
answers = pd.read_csv('../data/merged_all.tsv', sep='\t')
#set indices
answers = answers.set_index(['uni', 'Participant', 'Start'])
#group codes at the person level
people = answers.groupby(level=['uni', 'Participant']).any()

print 'Creating job list for person v person Jaccard similarity...'
(id_map, result) = list_people_data(people)
print 'Computing person v person similarity...'
output = view.map_sync(parallel_jaccard, result)
print 'Computations finished!'

#TODO: save results


# 

print 'Creating job list for answer v answer Jaccard similarity...'
(m2, r2) = list_people_data(answers)
print 'Computing answer v answer similarity...'
output2 = view.map_sync(parallel_jaccard, r2)
print 'Computations finished!'

#TODO: save results

print 'Done!'