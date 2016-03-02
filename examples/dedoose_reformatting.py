# @author Jeff Lockhart <jwlock@umich.edu>
# Example script for cleaning and reformatting Dedoose excerpt export files. 
# version 1.0

import pandas as pd
import re

#Import our data from Dedoose
raw = pd.read_excel("data/DedooseChartExcerpts_2016_3_1_2317-ben.xlsx")

'''
One of my descriptor variables in Dedoose, 'school', wasn't merged properly.
Here I merge the columns back together.
'''
school_cols = ['school', 'school.1', 'school.2', 'school.3',
              'school.4', 'school.5',]

def school_merge(row):
    for c in school_cols:
        if pd.notnull(row[c]):
            #Each row will only have one school.
            #We can stop when we find it.
            return row[c]
    return ''
    
tmp = raw
tmp['uni'] = ''
tmp['uni'] = tmp.apply(school_merge, axis=1)


'''
Dedoose does some things I don't like with column names, like titling code 
applications as 'Code: xxx Applied' and calling my participant ID numbers 
'Document Title'. This is some quick column renaming. 
'''
raw = raw.rename(columns=lambda x: re.sub('Code: ','',x))
raw = raw.rename(columns=lambda x: re.sub(' Applied','',x))
raw = raw.rename(columns=lambda x: re.sub('Document Title',
                                          'Participant',x))
raw = raw.rename(columns=lambda x: re.sub('Package','Start',x))

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
keep_cols = ['uni', 'Participant', 'Start', 'Excerpt Copy']
keep_cols = keep_cols + code_cols
df = raw[keep_cols]

#Flag whether this excerpt has been coded with any of the codes we care about.
df['coded'] = False

def check_codes(row):
    for c in code_cols:
        if row[c] == True:
            return True
    return False

df['coded'] = df.apply(check_codes, axis=1)

#Drop excerpts without any codes we care about
df = df[df['coded'] == True]
df.shape

'''
Sort our excerpts by which set they are from (uni), then their number 
(participant numbers are only unique within sets in my data), then by 
the index where the excerpt starts. This isn't strictly necessary, but 
I like that it gives me meaningful groupings.
'''
df.sort_values(by=['uni', 'Participant', 'Start'], axis=0, inplace=True)

#Export the data to tsv for later use
df.to_csv('data/clean.tsv', sep='\t', encoding='utf-8', index=False)