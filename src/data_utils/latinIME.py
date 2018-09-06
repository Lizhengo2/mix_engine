import sys
import math
import os


args = sys.argv

en_latin_file = args[1]
es_latin_file = args[2]
data_path = args[3]


def vocab_reader(file):

    vocab_dict = dict()
    with open(file, "r") as f:
        count = 0
        for line in f:
            count += 1
            # if count > 10000:
            #     continue
            token, id = line.strip().split("\t")
            if token not in vocab_dict:
                vocab_dict[token] = int(id)
    print("vocabulary size:", len(vocab_dict))
    return vocab_dict


def cal_max_freq(vocab_dict):
    max_freq = 0
    for word in vocab_dict:
        freq = vocab_dict[word]
        if freq > max_freq:
            max_freq = freq

    return max_freq


en_latin_dict = vocab_reader(en_latin_file)
es_latin_dict = vocab_reader(es_latin_file)

en_es_latin_dict = dict(en_latin_dict, **es_latin_dict)
for word in en_es_latin_dict:
    en_es_latin_dict[word] = 0

files_list = os.listdir(data_path)

for file in files_list:
    file_path = os.path.join(data_path, file)
    print(file_path)
    with open(file_path) as f:
        for line in f:
            line = line.rstrip()
            words = line.split()
            for word in words:
                if word in en_es_latin_dict:
                    en_es_latin_dict[word] += 1
                elif word.lower() in en_es_latin_dict:
                    en_es_latin_dict[word.lower()] += 1
print(en_es_latin_dict)


max_freq = cal_max_freq(en_es_latin_dict)
print("max freq:", max_freq)
log_max = math.pow(math.log(max_freq), 2)

with open("main_en_es_unigram", "w") as f:
    max_new_freq = 0
    for word in en_es_latin_dict:
        freq = en_es_latin_dict[word]
        if freq != 0:
            new_freq = round(math.pow(math.log(freq), 2) / log_max * 229) + 1

        else:
            if word in en_latin_dict and word not in es_latin_dict:
                new_freq = en_latin_dict[word]
            elif word not in en_latin_dict and word in es_latin_dict:
                new_freq = es_latin_dict[word]
            else:
                new_freq = round((es_latin_dict[word] + en_latin_dict[word]) / 2)
        if new_freq > max_new_freq:
            max_new_freq = new_freq
        f.write(word + "\t" + str(new_freq) + "\n")
    print("max new freq:", max_new_freq)















