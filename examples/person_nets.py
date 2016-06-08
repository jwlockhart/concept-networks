# @author Jeff Lockhart <jwlock@umich.edu>
# Example script for generating network graphs of relations between people
# based on similarity scores. 
# version 1.1

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import sys

sys.path.insert(0,'../')
from network_utils import *

print 'Reading network data files...'
r = pd.read_csv('../data/people_jaccard.tsv', sep='\t')
m = pd.read_csv('../data/people_jaccard_ids.tsv', sep='\t')

print 'Reading person information...'
attr = pd.read_csv('../data/ben_all.tsv', sep='\t')
tmp = pd.read_csv('../data/gabi_all.tsv', sep='\t')

#merge info from both data sets
attr = attr.append(tmp)
attr = attr.drop_duplicates(subset=['uni', 'Participant'])

print 'Meging network and attribute info...'
attr = attr.merge(m, how='left', on=['uni', 'Participant'])

#select just the attributes we care about
attr = attr[['uid', 'uni', 'rank', 'identity',
       'Q3-g', 'Q3-l', 'Q3-b', 'Q3-quest', 'Q3-ace', 'Q3-queer', 'Q4-gq',
       'Q4-t', 'Q4-i', 'Q4-m', 'Q4-f']]

print 'Flattening rank options...'
attr = attr.replace(to_replace='likely-undergrad', value='undergrad')

def flatten_gender(row):
    g = 'unknown'
    if not pd.isnull(row['Q4-t']):
        g = 't'
    elif not pd.isnull(row['Q4-gq']):
        g = 't'
    elif not pd.isnull(row['Q4-i']):
        g = 't'
    elif not pd.isnull(row['Q4-m']):
        g = 'm'
    elif not pd.isnull(row['Q4-f']):
        g = 'f'
        
    return g

print 'Flattening genders into a single variable...'
attr['gender'] = attr.apply(flatten_gender, axis=1)

def flatten_sexuality(row):
    s = 'unknown'
    if row['identity'] == 'cishet':
        s = 'hetero'
    elif not pd.isnull(row['Q3-queer']):
        s = 'queer'
    elif not pd.isnull(row['Q3-ace']):
        s = 'ace'
    elif not pd.isnull(row['Q3-b']):
        s = 'bi'
    elif not pd.isnull(row['Q3-g']):
        s = 'gay'
    elif not pd.isnull(row['Q3-l']):
        s = 'lesbian'       
    return s

print 'Flattening sexualiies into a single variable...'
attr['sexuality'] = attr.apply(flatten_sexuality, axis=1)

print 'Creating network...'
g = make_net_list(r, attributes=attr)

print 'Doing network layout...'
pos = nx.spring_layout(g)

def show_graph_person(g, save_to='test.png', p=None, cat_name=None, cat_values=None):
    '''Display our network. Customize to best suit your own needs.'''
    colors = ['r', 'b', 'g', 'c', 'm', 'y', 'k']
    
    f = plt.figure(figsize=(15,15), facecolor='w', dpi=300)
    a = f.add_subplot(111)
    
    #layout nodes and their labels
    if p is None:
        print 'Arranging nodes...'
        pos = nx.spring_layout(g)
    else:
        pos = p

    #divide edges into groups based on weight
    print 'Selecting edges...'
    e9 = []
    e75 = []
    for (u, v, d) in g.edges(data=True):
        if d['weight'] >= 0.9:
            e9.append((u, v))
        elif d['weight'] >= 0.75:
            e75.append((u, v))
    
    #draw edges in each group
    print 'Drawing edges...'
    nx.draw_networkx_edges(g, pos, edgelist=e9, width=1, alpha=0.3, ax=a)
    nx.draw_networkx_edges(g, pos, edgelist=e75, width=1, alpha=0.2, ax=a)
    
    print 'Drawing nodes...'
    #all nodes:
    if cat_name is None:
        #nx.draw_networkx_nodes(g, pos, node_size=20, ax=a)
        pass
    else:
        for i, cat in enumerate(cat_values):
            tmp = [n for (n, d) in g.nodes(data=True) if d[cat_name] == cat]
            nx.draw_networkx_nodes(g, pos, nodelist=tmp, node_size=20, 
                                   node_color=colors[i], ax=a, label=cat)

    #axes look silly here
    plt.axis('off')
    plt.legend()
    plt.savefig(save_to)
    return

#a list of graphs to make, by name and possible values
to_make = {'identity': ['sgm','cishet'], 
           'uni': ['fordham', 'cwru', 'snc', 'mcu', 'uwg', 'jcu', 'fsu'],
           'rank': ['undergrad', 'grad-pro', 'faculty', 'staff'],
           'sexuality': ['lesbian', 'gay', 'bi', 'queer', 'ace', 'hetero'],
           'gender': ['f', 'm', 't']}

show_graph_person(g, p=pos, save_to='../data/person.png')

for k, v in to_make.iteritems():
    print 'Drawing graph of', k, '...'
    show_graph_person(g, p=pos, cat_name=k, cat_values=v, save_to='../data/person_by_'+k+'.png')

























