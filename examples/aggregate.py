# @author Jeff Lockhart <jwlock@umich.edu>
# Example script aggregating excerpts at a higher level (e.g. participant)
# version 1.1

import pandas as pd
import sys

sys.path.insert(0,'../')
import network_utils as nu

argv = sys.argv
if len(argv) != 3:
    print('Please run this script with exactly 2 arguments.\n$ merge_coding.py [infile.tsv] [outfile.tsv]')
    sys.exit()

print 'Loading data files...'
d1 = pd.read_csv(argv[1], sep='\t')

#tell Pandas which columns are our indices
d1 = d1.set_index(['uni', 'Participant', 'Start'])

print('Code frequencies in excerpts:')
print(d1.mean())

print('Aggregating...')
#takes the union of the sets of codes applied to each excerpt within each participant
d2 = d1.groupby(level=['uni', 'Participant']).any()
#counts all codes applied to each excerpt within each participant
d3 = d1.groupby(level=['uni', 'Participant']).sum()

print('Code frequencies in participants:')
print(d2.mean())

print('Saving final code applications to', argv[2], '...')
d2.to_csv(argv[2], sep='\t')

print('Done!')