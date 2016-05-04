# @author Jeff Lockhart <jwlock@umich.edu>
# Example script for cleaning and reformatting Dedoose excerpt export files. 
# version 2.0

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


#Some of my descriptor variables in Dedoose, 'school', weren't merged 
#properly. Here I merge the columns back together.
print 'Merging school columns...'
school_cols = ['school', 'school.1', 'school.2', 'school.3',
              'school.4', 'school.5',]
raw['uni'] = raw.apply(col_merge, cols=school_cols, fill_na='fsu', axis=1)

print 'Merging identity columns...'
cols = raw.columns.values
#a list of column sets we want to merge back together
to_merge = ['Q3-g', 'Q3-l', 'Q3-b', 'Q3-ace', 'Q3-s', 'Q3-queer', 'Q3-other',
            'Q3-quest', 'Q3-ally', 'Q4-m', 'Q4-f', 'Q4-gq', 'Q4-t', 
            'Q4-i', 'Q4-other']
for a in to_merge:
    #for each set, make a regex matching it
    regex=re.compile('^' + a + '.*')
    #select all columns matching the set
    these_cols = [m.group(0) for l in cols for m in [regex.search(l)] if m]
    print 'Merging', these_cols, "..."
    raw[a] = raw.apply(col_merge, cols=these_cols, axis=1)

print 'Identifying SGMs and CisHets...'
def find_ident(row, q_cols):
    result = 'unknown'
    #see if they match any of the SGM identities
    for c in q_cols:
        if row[c] != '':
            result = 'sgm'
    #if not, see if they are cisgender and heterosexual
    if result == 'unknown':
        if row['Q4-f'] or row['Q4-m']:
            if row['Q3-s'] != '':
                result = 'cishet'
    return result

q_c = ['Q3-g', 'Q3-l', 'Q3-b', 'Q3-quest', 'Q3-other', 
       'Q3-ace', 'Q3-queer', 'Q4-gq', 'Q4-t', 'Q4-i', 'Q4-other']
raw['identity'] = raw.apply(find_ident, q_cols=q_c, axis=1)

print 'Merging rank columns...'
rank_cols = ['status.5','status.4','status.3','status.2', 
             'status.1', 'status']
raw['rank'] = raw.apply(col_merge, cols=rank_cols, 
                        fill_na='likely-undergrad', axis=1)

#Simplify column names
print 'Renaming columns...'
raw = clean_col_names(raw)
raw = raw.rename(columns=lambda x: re.sub('Document Title',
                                          'Participant',x))
raw = raw.rename(columns=lambda x: re.sub('Media Title',
                                          'Participant',x))

#similarly, I want my particpant IDs as ints, not strings
print 'Converting participant IDs to ints...'
raw = raw.replace({'Participant: ': ''}, regex=True)
raw['Participant'] = raw['Participant'].astype('int64')

#The list of codes
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
keep_cols = ['uni', 'Participant', 'Start', 'Excerpt Copy', 
             'rank', 'identity', 'Q3-g', 'Q3-l', 'Q3-b', 'Q3-quest',
             'Q3-ace', 'Q3-queer', 'Q4-gq', 'Q4-t', 'Q4-i', 'angry_cishet']
keep_cols = keep_cols + code_cols
df = raw[keep_cols]

#drop excerpts that don't have any interesting codes
print 'Counting coded excerpts...'
tmp = drop_uncoded(df, code_cols)
print 'Found', tmp.shape[0], 'excerpts with interesting codes applied.'

'''
Sort our excerpts by which set they are from (uni), then their number 
(participant numbers are only unique within sets in my data), then by 
the index where the excerpt starts. This isn't strictly necessary, but 
it gives me meaningful groupings.
'''
print 'Sorting on indices...'
df.sort_values(by=['uni', 'Participant', 'Start'], axis=0, inplace=True)

#Export the data to tsv for later use
print 'Saving...'
df.to_csv(argv[2], sep='\t', encoding='utf-8', index=False)

print 'Done!'
