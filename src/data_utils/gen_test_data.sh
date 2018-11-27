#! /bin/bash
corpus_path=$1
output_path=$2

mkdir -p ${output_path}

nums="2 3 4 5 6 7 8 9"
for num in ${nums};
do
python3 data_produce_simple.py words_dict/main_en_es_unigram words_dict/wordMap_en_es words_dict/emojis ${corpus_path}/user_${num} ${output_path}/test_data_${num} 0.8 20000 10000 5000 0 0
done


