#!/bin/bash
#script to automate repetitive tasks with processing data for the paper

#select data relevant to the project
python select_subset.py ../data/ben_all.tsv ../data/sgm_stud/ben.tsv sgm
python select_subset.py ../data/gabi_all.tsv ../data/sgm_stud/gabi.tsv sgm

python select_subset.py ../data/ben_all.tsv ../data/ch_stud/ben.tsv cishet
python select_subset.py ../data/gabi_all.tsv ../data/ch_stud/gabi.tsv cishet

python select_subset.py ../data/ben_all.tsv ../data/ben_relevant.tsv all
python select_subset.py ../data/gabi_all.tsv ../data/gabi_relevant.tsv all

#merge codes from both coders
python merge_coding.py ../data/sgm_stud/ben.tsv ../data/sgm_stud/gabi.tsv ../data/sgm_stud/merged.tsv
python merge_coding.py ../data/ch_stud/ben.tsv ../data/ch_stud/gabi.tsv ../data/ch_stud/merged.tsv
python merge_coding.py ../data/ben_relevant.tsv ../data/gabi_relevant.tsv ../data/merged_relevant.tsv

#calculate inter-coder reliability
python compute_icr.py ../data/ben_relevant.tsv ../data/gabi_relevant.tsv > ../data/icr_results.txt

#generate person-level aggregated coding
python aggregate.py ../data/sgm_stud/ben.tsv ../data/sgm_stud/ben_person.tsv
python aggregate.py ../data/sgm_stud/gabi.tsv ../data/sgm_stud/gabi_person.tsv
python aggregate.py ../data/sgm_stud/merged.tsv ../data/sgm_stud/merged_person.tsv

python aggregate.py ../data/ch_stud/merged.tsv ../data/ch_stud/merged_person.tsv

#generate figures used in the paper
python figures_for_paper.py
