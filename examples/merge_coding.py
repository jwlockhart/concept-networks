# @author Jeff Lockhart <jwlock@umich.edu>
# Example script for merging codes from multiple coders. 
# version 1.0

import pandas as pd
import sys

sys.path.insert(0,'../')
import icr

argv = sys.argv
if len(argv) != 4:
    print 'Please run this script with exactly 3 arguments.\n$ merge_coding.py [infile_1.tsv] [infile_2.tsv] [outfile.tsv]'
    sys.exit()

print 'Loading data files...'
d1 = pd.read_csv(argv[1], sep='\t')
d2 = pd.read_csv(argv[2], sep='\t')

#columns we're interested in
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

#tell Pandas which columns are our indices
d1 = d1.set_index(['uni', 'Participant', 'Start'])
d2 = d2.set_index(['uni', 'Participant', 'Start'])

#drop any remaining columns that aren't index or interesting codes
d1 = d1[code_cols]
d2 = d2[code_cols]

print 'Counting code applications...'
c = icr.count_codes([d1,d2])
print 'Found', c.shape[0], 'coded excerpts.'
print 'Code counts:'
print icr.summarize(c)

print 'How many coders have coded each excerpt:'
c = icr.count_codes([d1,d2], keep_coder_counts=True)
print c['xxx_n_coders_xxx'].head()
print 'Summarize that:'
print c['xxx_n_coders_xxx'].value_counts()

print 'Merging code applications where any coder has applied a code'
m_any = icr.simple_merge([d1,d2], threshold=1)
print 'Summary of merged code applications:'
print icr.summarize(m_any)

print 'Merging code applications where all coders agree on a code'
m_all = icr.simple_merge([d1,d2], threshold=1, unanimous=True)
print 'Summary of merged code applications:'
print icr.summarize(m_all)

print 'Merging code applications where at least two coders have applied a code'
m_two = icr.simple_merge([d1,d2], threshold=2)
print 'Summary of merged code applications:'
print icr.summarize(m_two)

print 'Saving final code applications to', argv[3], '...'
m_any.to_csv(argv[3], sep='\t')

print 'Done!'

















