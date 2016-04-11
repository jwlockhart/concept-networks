# @author Jeff Lockhart <jwlock@umich.edu>
# Example script for selecting the subset of our data that matches
# our study criteria. 
# version 1.0

import pandas as pd
import sys
#add the parent directory to the current session's path
sys.path.insert(0, '../')
#import utility file from parent directory
from dedoose_utils import *

argv = sys.argv
if len(argv) != 4:
    print 'Please run this script with exactly 3 arguments. \n$ dedoose_reformatting.py [infile.tsv] [outfile.tsv] [sgm|cishet]'
    sys.exit()

#Import our data from Dedoose
print 'Reading in data...'
raw = pd.read_csv(argv[1], sep='\t')
print 'Found', raw.shape[0], 'excerpts.'

#The list of codes I'm interested in
code_cols = ['culture_problem', 
#             'culture_absent', 
             'culture_solution', 
             'culture_helpless', 
             'culture_victim', 
             'cishet_problem', 
             'cishet_victim', 
             'cishet_solution', 
#             'cishet_absent', 
             'cishet_helpless', 
             'sgm_victim', 
             'sgm_problem', 
             'sgm_helpless', 
#             'sgm_absent', 
             'sgm_solution', 
             'school_problem', 
             'school_solution', 
#             'school_absent', 
             'school_victim', 
             'school_helpless', 
             'community_problem', 
             'community_solution', 
             'community_helpless', 
#             'community_absent', 
             'community_victim']

#Select just the columns I want to use in analysis
print 'Selecting columns...'
keep_cols = ['uni', 'Participant', 'Start', 'Excerpt Copy', 
             'rank', 'identity']
keep_cols = keep_cols + code_cols
df = raw[keep_cols]

#drop excerpts that don't have any interesting codes
print 'Selecting coded excerpts...'
df = drop_uncoded(df, code_cols)
print 'Found', df.shape[0], 'excerpts with interesting codes applied.'

#drop excerpts from people outside my population of interest
print 'Selecting study population...'
df = df[df['identity'] == argv[3]]
    
print 'Found', df.shape[0], 'of those excerpts from  the population.'
df = df[(df['rank'] == 'undergrad') |
        (df['rank'] == 'likely-undergrad') |
        (df['rank'] == 'grad-pro')]
print 'Found', df.shape[0], 'of those excerpts from students.'

'''
Sort our excerpts by which set they are from (uni), then their number 
(participant numbers are only unique within sets in my data), then by 
the index where the excerpt starts. This isn't strictly necessary, but 
I like that it gives me meaningful groupings.
'''
print 'Sorting on indices...'
df.sort_values(by=['uni', 'Participant', 'Start'], axis=0, inplace=True)

#Export the data to tsv for later use
print 'Saving...'
df.to_csv(argv[2], sep='\t', encoding='utf-8', index=False)

print 'Done!'
