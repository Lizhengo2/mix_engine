#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys


class DataAnalyse:
    def __init__(self, en_US_vocab_file=None, es_US_vocab_file=None, emojis_file=None, stress_word_map_file=None,
                 en_uniGram=None, es_uniGram=None):

        if en_US_vocab_file and es_US_vocab_file and emojis_file:
            self.en_US_id2token_in_words, self.es_US_id2token_in_words, self.emojis_id2token_in_words = {}, {}, {}
            self.en_US_token2id_in_words, self.es_US_token2id_in_words, self.emojis_token2id_in_words = {}, {}, {}

            self.stress_word_map = dict()
            self.special_flags = ["<unk>", "<und>", "<eos>"]
            self.word_regex = "^[a-zA-Z']+$"
            self.num_regex = "^[+-]*[0-9]+.*[0-9]*$"
            self.pun_regex = "^[^a-zA-Z0-9']*$"
            self.stress_letters = "áéíóúü"
            self.no_stress_letters = "aeiouu"
            self.en_es_regex = "^[a-zA-Z'áéíóúüñ]+$"

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

            with open(stress_word_map_file, mode="r") as f:
                for line in f:
                    no_stress_word, stress_word = line.strip().split("\t")
                    if no_stress_word not in self.stress_word_map:
                        self.stress_word_map[no_stress_word] = stress_word
            print("stress word vocabulary size =", str(len(self.stress_word_map)))

        if en_uniGram and es_uniGram:
            self.en_uniGram, self.es_uniGram = [], []

            with open(en_uniGram, mode="r") as f:
                for line in f:
                    line = line.strip()[1:-1]
                    res = line.split(",")
                    if len(res) == 2:
                        token, id = res
                        if token not in self.emojis_token2id_in_words and token in self.en_US_token2id_in_words:
                            self.en_uniGram.append(token)

            print("en US uniGram size =", str(len(self.en_uniGram)))

            with open(es_uniGram, mode="r") as f:
                for line in f:
                    line = line.strip()[1:-1]
                    res = line.split(",")
                    if len(res) == 2:
                        token, id = res
                        if token not in self.emojis_token2id_in_words and token in self.es_US_token2id_in_words:
                            self.es_uniGram.append(token)

            print("es US uniGram size =", str(len(self.es_uniGram)))

    def is_mixed_corpus(self, words):
        for word in words:
            if word not in self.en_US_token2id_in_words and word.lower() not in self.en_US_token2id_in_words and \
                    not re.match(self.pun_regex, word) and not re.match(self.num_regex, word):
                return True
        return False

    def is_stress_es_word(self, word):
        if word in self.stress_word_map:
            return self.stress_word_map[word]
        else:
            return None

    def calc_ratio(self, test_file, en_US_first=True):

        first_language = "en_US" if en_US_first else "es_US"
        second_language = "es_US" if en_US_first else "en_US"

        same_language_count, first_language_count, second_language_count, unk_count, total_line = 0, 0, 0, 0, 0

        f = open(test_file, "r")
        first_vocab = self.en_US_token2id_in_words if en_US_first else self.es_US_token2id_in_words
        second_vocab = self.es_US_token2id_in_words if en_US_first else self.en_US_token2id_in_words

        same_words = dict()
        unk_words = dict()
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
                        if word not in unk_words:
                            unk_words[word] = 1
                        else:
                            unk_words[word] += 1

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
        # print(sorted(same_words.items(), key=lambda d: d[1], reverse=True))
        # print(sorted(unk_words.items(), key=lambda d: d[1], reverse=True))
        # for (word, freq) in sorted(same_words.items(), key=lambda d: d[1], reverse=True):
        #     print(word)
        # for (word, freq) in sorted(same_words.items(), key=lambda d: d[1], reverse=True):
        #     print(freq)

    def calc_stress_ratio(self, test_file):

        stress_word_count, total_count, unk_count, stress_word_is_lower_count, \
            stress_word_not_lower_count, stress_words_from_data, not_unk_count = 0, 0, 0, 0, 0, 0, 0

        f = open(test_file, "r")

        stress_words = dict()

        for line in f:
            words = line.strip().split()

            for word in words:

                if word not in self.emojis_token2id_in_words and re.match(self.en_es_regex, word):
                    total_count += 1
                    if word not in self.es_US_token2id_in_words and word.lower() not in self.es_US_token2id_in_words and \
                            word not in self.en_US_token2id_in_words and word.lower() not in self.en_US_token2id_in_words:
                        unk_count += 1
                        stress_word = self.is_stress_es_word(word.lower())
                        if stress_word is not None:
                            stress_word_count += 1
                            if stress_word.lower() == word.lower():
                                stress_word_is_lower_count += 1
                            else:
                                stress_word_not_lower_count += 1
                            if word.lower() + "->" + stress_word not in stress_words:
                                stress_words[word.lower() + "->" + stress_word] = 1
                            else:
                                stress_words[word.lower() + "->" + stress_word] += 1
                    if word in self.es_US_token2id_in_words or word.lower() in self.es_US_token2id_in_words:
                        not_unk_count += 1
                        for letter in word:
                            if letter in self.stress_letters:
                                # print(word)
                                stress_words_from_data += 1
                                break

        print("unk words count :", unk_count, "; unk ratio :", unk_count / total_count)
        print("stress words count :", stress_word_count, "; stress word ratio :", stress_word_count / unk_count)
        print("is lower stress words count :", stress_word_is_lower_count,
              "; is lower stress word ratio :", stress_word_is_lower_count / stress_word_count)
        print("not lower stress words count :", stress_word_not_lower_count,
              "; not lower stress word ratio :", stress_word_not_lower_count / stress_word_count)
        print("stress words from data count :", stress_words_from_data/not_unk_count)
        print(stress_words_from_data, not_unk_count)

        # for (word, freq) in sorted(stress_words.items(), key=lambda d: d[1], reverse=True):
        #     print(word)
        # for (word, freq) in sorted(stress_words.items(), key=lambda d: d[1], reverse=True):
        #     print(freq)
        # print(sorted(stress_words.items(), key=lambda d: d[1], reverse=True))

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

    def stress_letter_replace(self, word):
        if len(word) > 0:
            for (stress_letter, no_stress_letter) in zip(self.stress_letters, self.no_stress_letters):
                word = word.replace(stress_letter, no_stress_letter)
            return word
        else:
            return None

    def words_freq_diff(self, en_file, es_file, vocab="en_US"):
        f_en = open(en_file, "r")
        f_es = open(es_file, "r")
        vocab = self.en_US_token2id_in_words if vocab == "en_US" else self.es_US_token2id_in_words
        word_freq_dict_in_en_language, word_freq_dict_in_es_language = {}, {}

        for (en_line, es_line) in zip(f_en, f_es):
            words_in_en_language = en_line.strip().split()
            words_in_es_language = es_line.strip().split()
            for word in words_in_en_language:
                if word in vocab and word not in self.emojis_token2id_in_words:
                    if word in word_freq_dict_in_en_language:
                        word_freq_dict_in_en_language[word] += 1
                    else:
                        word_freq_dict_in_en_language[word] = 1
            for word in words_in_es_language:
                if word in vocab and word not in self.emojis_token2id_in_words:
                    if word in word_freq_dict_in_es_language:
                        word_freq_dict_in_es_language[word] += 1
                    else:
                        word_freq_dict_in_es_language[word] = 1

        f_en.close()
        f_es.close()

        print("word vocab in en language :", len(word_freq_dict_in_en_language))
        print("word vocab in es language :", len(word_freq_dict_in_es_language))

        for word in word_freq_dict_in_es_language:
            if word in word_freq_dict_in_en_language:
                if word_freq_dict_in_es_language[word] >= 5 * word_freq_dict_in_en_language[word] or \
                   word_freq_dict_in_en_language[word] >= 5 * word_freq_dict_in_es_language[word]:
                    if word_freq_dict_in_es_language[word] >= 10 and word_freq_dict_in_en_language[word] >= 10:
                        print(word, "; en_US freq :", word_freq_dict_in_en_language[word],
                              "es_US freq :", word_freq_dict_in_es_language[word])
            no_stress_word = self.stress_letter_replace(word)

            if no_stress_word != word and no_stress_word in word_freq_dict_in_en_language :
                if word_freq_dict_in_es_language[word] >= 5 * word_freq_dict_in_en_language[no_stress_word] or \
                   word_freq_dict_in_en_language[no_stress_word] >= 5 * word_freq_dict_in_es_language[word]:
                    if word_freq_dict_in_es_language[word] >= 10 and word_freq_dict_in_en_language[no_stress_word] >= 10:
                        print(no_stress_word, "->", word, "; en_US freq :", word_freq_dict_in_es_language[no_stress_word],
                              "es_US freq :", word_freq_dict_in_es_language[word])

            if word not in word_freq_dict_in_en_language:
                if word_freq_dict_in_es_language[word] >= 100:
                    print(word, word_freq_dict_in_es_language[word], 0)

    def vocab_same_count(self, min, max, vocab, data_vocab):
        count = 0
        for (word, key) in data_vocab:
            if word in vocab[min: max]:
                count += 1

        return count

    def vocab_freq_diff(self, test_file, en_US=True):

        f = open(test_file, "r")
        vocab = self.en_US_token2id_in_words if en_US else self.es_US_token2id_in_words
        uniGram = self.en_uniGram if en_US else self.es_uniGram
        words_dict = dict()

        for line in f:
            words = line.strip().split()
            for word in words:
                if word not in self.emojis_token2id_in_words:
                    if word in vocab:
                        if word in words_dict:
                            words_dict[word] += 1
                        else:
                            words_dict[word] = 1
                    elif word.lower() in vocab:
                        if word.lower() in words_dict:
                            words_dict[word.lower()] += 1
                        else:
                            words_dict[word.lower()] = 1

        f.close()
        data_vocab = sorted(words_dict.items(), key=lambda d: d[1], reverse=True)
        print(data_vocab)
        print("data vocab size :", len(data_vocab))
        print("2000th word and freq :", data_vocab[2000])

        data_vocab = data_vocab[:2000]
        same_count_1_to_2000 = self.vocab_same_count(0, 2000, uniGram, data_vocab)
        same_count_2000_to_5000 = self.vocab_same_count(2000, 5000, uniGram, data_vocab)
        same_count_5000_to_10000 = self.vocab_same_count(5000, 10000, uniGram, data_vocab)
        same_count_10000_to_20000 = self.vocab_same_count(10000, 20000, uniGram, data_vocab)

        print("same_rate_1_to_2000 :", same_count_1_to_2000/2000)
        print("same_rate_2000_to_5000 :", same_count_2000_to_5000/2000)
        print("same_rate_5000_to_10000 :", same_count_5000_to_10000/2000)
        print("same_rate_10000_to_20000 :", same_count_10000_to_20000/2000)


if __name__ == "__main__":
    args = sys.argv

    test_file = args[1]
    emojis_file = args[2]
    en_US_vocab_file = args[3]
    es_US_vocab_file = args[4]
    stress_word_map_file = args[5]
    en_file = args[6]
    es_file = args[7]
    en_uniGram = args[8]
    es_uniGram = args[9]
    data_analyse = DataAnalyse(en_US_vocab_file, es_US_vocab_file, emojis_file, stress_word_map_file, en_uniGram, es_uniGram)
    data_analyse.diff_vocab()
    # data_analyse.sentence_filter(test_file, en_US_first=True)
    # data_analyse.calc_ratio(test_file, en_US_first=True)
    # data_analyse.calc_stress_ratio(test_file)
    # data_analyse.words_freq_diff(en_file, es_file, vocab="en_US")
    data_analyse.vocab_freq_diff(test_file, en_US=False)

