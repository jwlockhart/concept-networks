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
import icr

argv = sys.argv
if len(argv) != 3:
    print 'Please run this script with exactly 3 arguments.\n$ merge_coding.py [infile_1.tsv] [infile_2.tsv]'
    sys.exit()

print 'Loading data files...'
d1 = pd.read_csv(argv[1], sep='\t')
d2 = pd.read_csv(argv[2], sep='\t')

d1 = d1.set_index(['uni', 'Participant', 'Start'])
d2 = d2.set_index(['uni', 'Participant', 'Start'])

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

d1 = d1[code_cols]
d2 = d2[code_cols]

print "Computing ICR...\n"
results = icr.compute_icr(d1, d2)
means = results.mean()
print "Mean ICR stats:\n", means
print "\nPer-code ICR stats:\n", results

print "\nDone!"