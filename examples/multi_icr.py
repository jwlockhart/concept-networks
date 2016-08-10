# @author Jeff Lockhart <jwlock@umich.edu>
# Example script for computing intercoder reliability
# assumptions:
# - nominal data
# - 2+ coders
# - missing values okay
# version 1.0

import pandas as pd
import sys

sys.path.insert(0,'../')
import icr
import dedoose_utils as du

print 'Loading data files...'
d1 = pd.read_csv('../data/ben_all.tsv', sep='\t')
d2 = pd.read_csv('../data/gabi_all.tsv', sep='\t')
d3 = pd.read_csv('../data/lizzie_all.tsv', sep='\t')

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
             'community_victim', 
             'angry_cishet']

def merge_idx(row):
    return row['uni']+'_'+str(row['Participant'])+'_'+str(row['Start'])

def form(df):
    df['idx'] = df.apply(merge_idx, axis=1)
    df = df.set_index('idx')
    df = df[code_cols]
    df = du.drop_uncoded(df, code_cols)
    return df

print 'Formatting dataframes...'
d1 = form(d1)
d2 = form(d2)
d3 = form(d3)

print "Computing ICR..."
results = icr.compute_multi_icr([d1, d2, d3])
means = results.mean()
print "Mean ICR stats:\n", means
print "\nPer-code ICR stats:\n", results

print "\nDone!"