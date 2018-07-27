#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys


class DataAnalyse:
    def __init__(self, en_US_vocab_file=None, es_US_vocab_file=None, emojis_file= None):

        if en_US_vocab_file and es_US_vocab_file and emojis_file:
            self.en_US_id2token_in_words, self.es_US_id2token_in_words, self.emojis_id2token_in_words = {}, {}, {}
            self.en_US_token2id_in_words, self.es_US_token2id_in_words, self.emojis_token2id_in_words = {}, {}, {}

            self.special_flags = ["<unk>", "<und>", "<eos>"]
            self.word_regex = "^[a-zA-Z']+$"
            self.num_regex = "^[+-]*[0-9]+.*[0-9]*$"
            self.pun_regex = "^[^a-zA-Z0-9']*$"

            id = 0
            with open(en_US_vocab_file, mode="r") as f:
                for line in f:
                    token, _ = line.strip().split("\t")
                    if token in self.special_flags:
                        continue
                    self.en_US_id2token_in_words[id] = token
                    self.en_US_token2id_in_words[token] = id
                    id += 1
            print("en US words vocabulary size =", str(len(self.en_US_id2token_in_words)))

            id = 0
            with open(es_US_vocab_file, mode="r") as f:
                for line in f:
                    token, _ = line.strip().split("\t")
                    if token in self.special_flags:
                        continue
                    self.es_US_id2token_in_words[id] = token
                    self.es_US_token2id_in_words[token] = id
                    id += 1
            print("es US vocabulary size =", str(len(self.es_US_id2token_in_words)))

            id = 0
            with open(emojis_file, mode="r") as f:
                for line in f:
                    token, _ = line.strip().split("\t")
                    if token in self.special_flags:
                        continue
                    self.emojis_id2token_in_words[id] = token
                    self.emojis_token2id_in_words[token] = id
                    id += 1
            print("emojis vocabulary size =", str(len(self.emojis_token2id_in_words)))

    def is_mixed_corpus(self, words):
        for word in words:
            if word not in self.en_US_token2id_in_words and word.lower() not in self.en_US_token2id_in_words and \
                    not re.match(self.pun_regex, word) and not re.match(self.num_regex, word):
                return True
        return False

    def calc_ratio(self, test_file, en_US_first=True):

        first_language = "en_US" if en_US_first else "es_US"
        second_language = "es_US" if en_US_first else "en_US"

        same_language_count, first_language_count, second_language_count, unk_count, total_line = 0, 0, 0, 0, 0

        f = open(test_file, "r")
        first_vocab = self.en_US_token2id_in_words if en_US_first else self.es_US_token2id_in_words
        second_vocab = self.es_US_token2id_in_words if en_US_first else self.en_US_token2id_in_words

        same_words = dict()
        for line in f:
            words = line.strip().split()
            # if not self.is_mixed_corpus(words):
            #     continue
            total_line += 1

            for word in words:

                if word not in self.emojis_token2id_in_words:
                    if word in first_vocab and word in second_vocab:
                        same_language_count += 1
                        if word not in same_words:
                            same_words[word] = 1
                        else:
                            same_words[word] += 1
                    elif word.lower() != word and word.lower() in first_vocab and word.lower() in second_vocab and \
                        word not in first_vocab and word not in second_vocab:
                        same_language_count += 1
                        if word.lower() not in same_words:
                            same_words[word.lower()] = 1
                        else:
                            same_words[word.lower()] += 1
                    elif word in first_vocab or word.lower() in first_vocab \
                       and word not in second_vocab and word.lower() not in second_vocab:
                        first_language_count += 1
                    elif word in second_vocab or word.lower() in second_vocab \
                       and word not in first_vocab and word.lower() not in first_vocab:
                        second_language_count += 1
                    else:
                        unk_count += 1
        ratio = (first_language_count + same_language_count)/second_language_count if en_US_first \
            else first_language_count/(second_language_count + same_language_count)
        total_words = same_language_count + first_language_count + second_language_count + unk_count
        f.close()
        print("first language is :", first_language, "; second language is :", second_language)
        print("sentences count :", total_line, "; words count without emoji :", total_words)
        print("first language count :", first_language_count, "; first language ratio :", first_language_count/total_words)
        print("second language count :", second_language_count, "; second language count :", second_language_count/total_words)
        print("same language count :", same_language_count, "; same language count :", same_language_count/total_words)
        print("unk word count :", unk_count, "; unk count :", unk_count/total_words)

        print("first language : second language ratio is :", ratio)
        print(same_words)

    def calc_id_count(self, min, max, id_list):
        count = 0
        for id in id_list:
            if min <= id <= max:
                count += 1
        return count

    def diff_vocab(self):
        same_word_count = 0
        en_US_same_id_list, es_US_same_id_list = [], []
        for word in self.es_US_token2id_in_words:
            if word not in self.emojis_token2id_in_words and word in self.en_US_token2id_in_words:
                same_word_count += 1
                es_US_same_id_list.append(self.es_US_token2id_in_words[word])
                en_US_same_id_list.append(self.en_US_token2id_in_words[word])
        print("vocab same rate :", same_word_count/len(self.es_US_token2id_in_words))

        en_US_same_count_1_to_5000 = self.calc_id_count(1, 5000, en_US_same_id_list)
        en_US_same_count_5000_to_10000 = self.calc_id_count(5000, 10000, en_US_same_id_list)
        en_US_same_count_10000_to_20000 = self.calc_id_count(10000, 20000, en_US_same_id_list)

        es_US_same_count_1_to_5000 = self.calc_id_count(1, 5000, es_US_same_id_list)
        es_US_same_count_5000_to_10000 = self.calc_id_count(5000, 10000, es_US_same_id_list)
        es_US_same_count_10000_to_20000 = self.calc_id_count(10000, 20000, es_US_same_id_list)

        print("en_US_same_count_1_to_5000 :", en_US_same_count_1_to_5000)
        print("en_US_same_count_5000_to_10000 :", en_US_same_count_5000_to_10000)
        print("en_US_same_count_10000_to_20000 :", en_US_same_count_10000_to_20000)
        print("total_en_US_same_count :", len(en_US_same_id_list))

        print("es_US_same_count_1_to_5000 :", es_US_same_count_1_to_5000)
        print("es_US_same_count_5000_to_10000 :", es_US_same_count_5000_to_10000)
        print("es_US_same_count_10000_to_20000 :", es_US_same_count_10000_to_20000)
        print("total_es_US_same_count :", len(es_US_same_id_list))

    def sentence_filter(self, test_file, en_US_first=True):

        f = open(test_file, "r")
        first_vocab = self.en_US_token2id_in_words if en_US_first else self.es_US_token2id_in_words
        second_vocab = self.es_US_token2id_in_words if en_US_first else self.en_US_token2id_in_words

        total_line, mix_line = 0, 0

        for line in f:
            words = line.strip().split()
            native_count, lish_count = 0, 0
            total_line += 1
            for word in words:
                if word in first_vocab:
                    native_count += 1
                elif word in second_vocab:
                    lish_count += 1
            total_count = native_count + lish_count

            if native_count >= total_count * 0.3 and lish_count >= total_count * 0.3:
                mix_line += 1

        f.close()
        print("mix_sentences_ratio :", mix_line/total_line)


if __name__ == "__main__":
    args = sys.argv

    test_file = args[1]
    emojis_file = args[2]
    en_US_vocab_file = args[3]
    es_US_vocab_file = args[4]
    data_analyse = DataAnalyse(en_US_vocab_file, es_US_vocab_file, emojis_file)
    data_analyse.diff_vocab()
    # data_analyse.sentence_filter(test_file, en_US_first=True)
    data_analyse.calc_ratio(test_file, en_US_first=True)

