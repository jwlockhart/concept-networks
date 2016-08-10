#!/bin/bash
#script to automate repetitive tasks with processing data for the paper

#select data relevant to the project
#concurrently in background
python select_subset.py ../data/ben_all.tsv ../data/sgm_stud/ben.tsv sgm &
python select_subset.py ../data/gabi_all.tsv ../data/sgm_stud/gabi.tsv sgm &
python select_subset.py ../data/lizzie_all.tsv ../data/sgm_stud/lizzie.tsv sgm &

python select_subset.py ../data/ben_all.tsv ../data/ch_stud/ben.tsv cishet &
python select_subset.py ../data/gabi_all.tsv ../data/ch_stud/gabi.tsv cishet &
python select_subset.py ../data/lizzie_all.tsv ../data/ch_stud/lizzie.tsv cishet &

python select_subset.py ../data/ben_all.tsv ../data/ben_relevant.tsv all &
python select_subset.py ../data/gabi_all.tsv ../data/gabi_relevant.tsv all &
python select_subset.py ../data/lizzie_all.tsv ../data/lizzie_relevant.tsv all &

#wait for all background jobs to finish before moving on
wait

#merge codes from both coders
python merge_coding.py ../data/sgm_stud/ben.tsv ../data/sgm_stud/gabi.tsv ../data/sgm_stud/merged.tsv &
python merge_coding.py ../data/ch_stud/ben.tsv ../data/ch_stud/gabi.tsv ../data/ch_stud/merged.tsv &
python merge_coding.py ../data/ben_relevant.tsv ../data/gabi_relevant.tsv ../data/merged_relevant.tsv &

#wait for these jobs to finish before stepping forward
wait

#merge in 3rd coder
python merge_coding.py ../data/sgm_stud/lizzie.tsv ../data/sgm_stud/merged.tsv ../data/sgm_stud/merged.tsv &
python merge_coding.py ../data/ch_stud/lizzie.tsv ../data/ch_stud/merged.tsv ../data/ch_stud/merged.tsv &
python merge_coding.py ../data/lizzie_relevant.tsv ../data/merged_relevant.tsv ../data/merged_relevant.tsv &

wait

#generate person-level aggregated coding
python aggregate.py ../data/sgm_stud/merged.tsv ../data/sgm_stud/merged_person.tsv &
python aggregate.py ../data/ch_stud/merged.tsv ../data/ch_stud/merged_person.tsv &
python aggregate.py ../data/merged_relevant.tsv ../data/ch_stud/merged_relevant_person.tsv &

wait

#calculate inter-coder reliability
python multi_icr.py > ../data/icr_results.txt &

#generate figures used in the paper
python figures_for_paper.py &

wait 

echo "Done with all"

