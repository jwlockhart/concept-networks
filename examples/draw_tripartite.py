# @author Jeff Lockhart <jwlock@umich.edu>
# Script for drawing the tripartite network underlying analysis.
# version 1.0

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import sys
#add the parent directory to the current session's path
sys.path.insert(0, '../')
from network_utils import *

#read our cleaned up data
df = pd.read_csv('../data/sgm_stud/merged.tsv', sep='\t')

#The list of codes we're interested in. 
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
             'community_victim']

#generate unique ID keys for each student and excerpt
def s_id(row):
    return row['uni'] + str(row['Participant'])

def e_id(row):
    return row['s_id'] + '-' + str(row['Start'])

df['s_id'] = df.apply(s_id, axis=1)
df['e_id'] = df.apply(e_id, axis=1)

#make a graph
g = nx.Graph()

#add all of our codes as nodes
for c in code_cols:
    g.add_node(c, t='code')

#add each excerpt of text as a node. Connect it with relevant 
#students and codes.
st = []
ex = []
last = ''
for row in df.iterrows():
    #add the student node
    g.add_node(row[1]['s_id'], t='student')
    #if we haven't seen this student before, save the order we saw them in
    if last != row[1]['s_id']:
        last = row[1]['s_id']
        st.append(last)
    
    #add this excerpt node. Save its order to our list.
    g.add_node(row[1]['e_id'], t='excerpt')
    ex.append(row[1]['e_id'])
    
    #add the edge joining this student and excerpt.
    g.add_edge(row[1]['s_id'], row[1]['e_id'])
    
    #for each code this excerpt has, draw an edge to it
    for c in code_cols:
        if row[1][c]:
            g.add_edge(row[1]['e_id'], c)

#get a dictionary of our code nodes' labels
l = {}
for c in code_cols:
    l[c] = c

#fix the positions of each node type in columns
pos = dict()
#space out the student and code nodes to align with excerpt column height
pos.update( (n, (1, i*5.57)) for i, n in enumerate(st) )
pos.update( (n, (2, i)) for i, n in enumerate(ex) ) 
pos.update( (n, (3, i*90)) for i, n in enumerate(code_cols) ) 

#make our figure big so we can see
plt.figure(figsize=(20,20))

#draw our nodes
nx.draw_networkx_nodes(g, pos, nodelist=st, node_color='r', 
                      node_shape='^')
nx.draw_networkx_nodes(g, pos, nodelist=ex, node_color='b', 
                      node_shape='o', alpha=0.5)
#draw our edges with low alpha so we can see
nx.draw_networkx_edges(g, pos, alpha=0.2)

#axes look silly
plt.axis('off')
#save the edges and nodes as one image
plt.savefig('../data/tripartite_unlabeled.png')

#save the labels for the codes as a different image
#this lets me edit them in with GIMP so that they're better positioned.
plt.figure(figsize=(20,20))
nx.draw_networkx_labels(g, pos, labels=l, font_size=20)
nx.draw_networkx_edges(g, pos, alpha=0)
plt.axis('off')
plt.savefig('../data/tripartite_labeles.png')



