#!/bin/bash
#script to automate repetitive tasks with processing data for the paper

#merge codes from both coders
python merge_coding.py ../data/ben.tsv ../data/gabi.tsv ../data/merged.tsv

#generate person-level aggregated coding
python aggregate.py ../data/ben.tsv ../data/ben_person.tsv
python aggregate.py ../data/gabi.tsv ../data/gabi_person.tsv
python aggregate.py ../data/merged.tsv ../data/merged_person.tsv

#generate figures used in the paper
python figures_for_paper.py