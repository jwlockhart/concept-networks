#!/bin/bash
#script to automate repetitive tasks with processing data for the paper

#select data relevant to the project
python select_subset.py ../data/ben_all.tsv ../data/ben.tsv
python select_subset.py ../data/gabi_all.tsv ../data/gabi.tsv

#merge codes from both coders
python merge_coding.py ../data/ben.tsv ../data/gabi.tsv ../data/merged.tsv

#generate person-level aggregated coding
python aggregate.py ../data/ben.tsv ../data/ben_person.tsv
python aggregate.py ../data/gabi.tsv ../data/gabi_person.tsv
python aggregate.py ../data/merged.tsv ../data/merged_person.tsv

#generate figures used in the paper
python figures_for_paper.py