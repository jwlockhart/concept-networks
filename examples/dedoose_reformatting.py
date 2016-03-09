# @author Jeff Lockhart <jwlock@umich.edu>
# Example script for cleaning and reformatting Dedoose excerpt export files. 
# version 1.1

import pandas as pd
import re
import sys
#add the parent directory to the current session's path
sys.path.insert(0, '../')
#import utility file from parent directory
from dedoose_utils import *

argv = sys.argv
if len(argv) != 3:
    print 'Please run this script with exactly 2 arguments. \n$ dedoose_reformatting.py [infile.xlsx] [outfile.tsv]'
    sys.exit()

#Import our data from Dedoose
print 'Reading in data...'
raw = pd.read_excel(argv[1])

print 'Found', raw.shape[0], 'excerpts.'

'''
One of my descriptor variables in Dedoose, 'school', wasn't merged properly.
Here I merge the columns back together.
'''
print 'Merging school columns...'
school_cols = ['school', 'school.1', 'school.2', 'school.3',
              'school.4', 'school.5',]   
raw['uni'] = ''
raw['uni'] = raw.apply(col_merge, cols=school_cols, axis=1)


#Simplify column names
print 'Renaming columns...'
raw = clean_col_names(raw)
raw = raw.rename(columns=lambda x: re.sub('Document Title',
                                          'Participant',x))
raw = raw.rename(columns=lambda x: re.sub('Media Title',
                                          'Participant',x))

#similarly, I want my particpant IDs as ints, not strings:
raw = raw.replace({'Participant: ': ''}, regex=True)
raw['Participant'] = raw['Participant'].astype('int64')

#The list of codes I'm interested in
code_cols = ['culture_problem', 
             'culture_absent', 
             'culture_solution', 
             'culture_helpless', 
             'culture_victim', 
             'cishet_problem', 
             'cishet_victim', 
             'cishet_solution', 
             'cishet_absent', 
             'cishet_helpless', 
             'sgm_victim', 
             'sgm_problem', 
             'sgm_helpless', 
             'sgm_absent', 
             'sgm_solution', 
             'school_problem', 
             'school_solution', 
             'school_absent', 
             'school_victim', 
             'school_helpless', 
             'community_problem', 
             'community_solution', 
             'community_helpless', 
             'community_absent', 
             'community_victim']

#Select just the columns I want to use in analysis
print 'Selecting columns...'
keep_cols = ['uni', 'Participant', 'Start', 'Excerpt Copy']
keep_cols = keep_cols + code_cols
df = raw[keep_cols]

#drop excerpts that don't have any interesting codes
print 'Selecting excerpts...'
df = drop_uncoded(df, code_cols)
print 'Found', df.shape[0], 'excerpts with relevant codes applied.'

'''
Sort our excerpts by which set they are from (uni), then their number 
(participant numbers are only unique within sets in my data), then by 
the index where the excerpt starts. This isn't strictly necessary, but 
I like that it gives me meaningful groupings.
'''
df.sort_values(by=['uni', 'Participant', 'Start'], axis=0, inplace=True)

#Export the data to tsv for later use
print 'Saving...'
df.to_csv(argv[2], sep='\t', encoding='utf-8', index=False)

print 'Done!'
