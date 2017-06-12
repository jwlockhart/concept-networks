# Code for conducting automated sentiment analysis (positive/negative)
# of comment text.
#
# Code here borrows from / builds on reedcoke's work here:
# https://github.com/reedcoke/bigDataCamp2016
# as used in 
# https://github.com/jwlockhart/mi_trans_comments
#
# This parallel implementation improves upon the speed of the 
# examples above, but is still limited by making separate command
# line calls to the java Stanford CoreNLP library. Sadly, 
# sentiment analysis is not yet implemented in their API (this would 
# save significant overhead).
#
# Recommendation: run this on with 1/4 as many engines as cores. 
# On a 12 core machine, running this on 4 cores tends to use about 
# 95% of the total processing capacity due to java startup and 
# shutdown costs. :(
# version 1.1

import pandas as pd
import numpy
import re
import subprocess
import os
import ipyparallel

print('Reading data...')
data = pd.read_csv('../data/ben_all.tsv', sep='\t')

def get_q(txt):
    q = ''
    #nongreedy search for question no. in case comment has a ';'
    m = re.search('Question: (.+?);', txt)
    if m:
        q = m.group(1)
    return q

def get_txt(txt):
    t = ''
    #multiline search to grab whole comments even with '\n' characters
    p = re.compile('Answer: (.+)', re.MULTILINE)
    m = re.search(p, txt)
    if m:
        t = m.group(1)
    return str(t)

print('Parsing out question and answer text...')
data['Question'] = data['Excerpt Copy'].apply(get_q)
data['Answer'] = data['Excerpt Copy'].apply(get_txt)

#select just the columns we care about
data = data[['uni', 'Participant', 'Start', 'Question', 'Answer']]

print('Saving just the cleaned up answer text...')
data.to_csv('../data/just_answers.tsv', sep='\t', index=False)

print('Separating comments before feeding them to the sentiment analyzer...')
j = 0
n = len(data)
for (i, d) in data.iterrows():
    #temporary files. 
    with open('../data/sentiment/' +d.uni+'_'+str(d.Participant)+'_'+str(d.Start)+'_.txt','w') as out:
        out.write(d.Answer)
    j += 1
    if j % 1000 == 0:
        print(j, 'of', n)
print('Done!')

print('Creating cluster client and view...')
c = ipyparallel.Client()
c[:].apply_sync(os.chdir, os.getcwd())
view = c.load_balanced_view()

def ippRunSentiment(fname):
    import subprocess
    from numpy import mean
    from numpy import std
    
    #Stanford sentiment gives text ratings, we want numeric ratings
    points = {'very negative' : -3, 'negative' : -1, 'neutral' : 0,
              'positive' : 1, 'very positive' : 3}
    
    classPath = '-cp "/home/jwlock/research/workspace/stanford-corenlp-full-2015-12-09/*"'
    settings = ' -mx5g edu.stanford.nlp.sentiment.SentimentPipeline'
    inputFile = ' -file ../data/sentiment/' + fname
    outputFile = ' > ' + fname + '_result.txt'
    command = 'java ' + classPath +  settings + inputFile #+ outputFile

    child = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    out, err = child.communicate()

    #divide results by line
    scores = out.split('\n')[1:]
    values = []

    for score in scores:
        try:
            #if this line is in our scores dict
            values.append(points[score.strip().lower()])
        except KeyError:        
            continue

    #return summary stats            
    return {'name': fname, 
            'mean': mean(values), 
            'sd': std(values), 
            'n': len(values),  
            'raw': out
           }

def ippGatherSentiment():
    dataDir = '../data/sentiment'
    print('Listing answers...')
    speeches = [fname for fname in os.listdir(dataDir) if '.txt' in fname]
    
    print('Starting parallel sentiment analysis...')
    results = view.map_async(ippRunSentiment, speeches)
    results.wait_interactive()
    
    print('Analysis complete! Packaging as DataFrame...')
    return pd.DataFrame.from_records(results)
            
r = ippGatherSentiment()

print('Cleaning up DF formating...')
r['uni'] = r.name.str.split('_').str.get(0)
r['Participant'] = r.name.str.split('_').str.get(1)
r['Start'] = r.name.str.split('_').str.get(2)
r = r[['uni', 'Participant', 'Start', 'mean', 'sd', 'n', 'raw']]

print('Saving results...')
r.to_csv('../data/sentiment_scores.tsv', sep='\t', index=False)
print('Done!')

