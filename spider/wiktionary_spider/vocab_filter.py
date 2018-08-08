# -*- coding: utf-8 -*-

vocab = "wiktionary_es_verbs.txt"
f = open(vocab, "r")
count = 0
spanish_count = 0
not_english_but_spanish_list = []

for line in f:
    is_english = False
    is_spanish = False
    line_split = line.strip().split("\t")
    if len(line_split) > 1:
        word = line_split[0]
        for language in line_split[1:]:
            if "English" in language:
                is_english = True
            if "Spanish" in language:
                is_spanish = True
        if not is_english:
            count += 1
            if is_spanish:
                spanish_count += 1
                not_english_but_spanish_list.append(word)
#                 print(line.strip())
# print(count)
# print(spanish_count)

f.close()

fr = open("../../vocab/es_US_unigram_2w", "r")
fw = open("../../vocab/es_US_unigram_2w_filted", "w")

id = 0
for line in fr:
    word, count = line.strip().split("\t")
    id += 1
    if word in not_english_but_spanish_list:
        print(word, count, id)
    fw.write(word + "\t" + count + "\n")

fr.close()
fw.close()
