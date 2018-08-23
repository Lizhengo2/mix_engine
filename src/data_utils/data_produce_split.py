#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import re
import os
import numpy as np


class TrainDataProducer:

    def __init__(self):

        self.word_regex = "^[a-zA-Z'áéíóúüñ]+$"
        self.num_regex = "^[+-]*[0-9]+.*[0-9]*$"
        self.pun_regex = "^[^a-zA-Z0-9']*$"

        self.vocab_split_flag = "##"
        self.line_split_flag = "#"
        self.pad_flag = "_PAD"
        self.eos_flag = "<eos>"
        self.num_flag = "<num>"
        self.pun_flag = "<pun>"
        self.emoji_flag = "<emoji>"
        self.unk_flag = "<unk>"
        self.und_flag = "<und>"
        self.start_flag = "<start>"
        self.not_phrase_flag = "<unp>"
        self.en_flag = "<en>"
        self.es_flag = "<es>"

        self.emojis_dict = dict()
        self.en_full_words_dict = dict()
        self.es_full_words_dict = dict()

        self.in_word_id_dict = dict()
        self.letter_id_dict = dict()
        self.out_word_id_dict = dict()
        self.phrase_id_dict = dict()

        self.words_keys_pair = dict()

    def load_vocab(self, vocab_file, split_flag, max_num, vocab_type=None):
        if vocab_type is not None:
            assert vocab_type in ["en", "es", "mix"]
        vocab_dict = dict()
        count = 0
        with open(vocab_file, "r") as f:
            for line in f:
                count += 1
                if count > max_num > 0:
                    break
                line = line.strip()
                line_split = re.split(split_flag, line)
                if len(line_split) == 2:
                    token, id = line_split
                    if vocab_type is not None:
                        token = "<" + vocab_type + ">" + token
                    vocab_dict[token] = int(id)
                elif len(line_split) == 1:
                    token = line_split[0]
                    if vocab_type is not None:
                        token = "<" + vocab_type + ">" + token
                    vocab_dict[token] = 1
                else:
                    print(vocab_type + " vocab split error : " + line)
        f.close()
        return vocab_dict

    def save_map_to_file(self, id_map, vocab_file_out):
        with open(vocab_file_out, "w") as f:
            id = 0
            for word in id_map:
                f.write(word + self.vocab_split_flag + str(id) + "\n")
                id += 1
        f.close()

        return

    def save_vocab_files(self, data_path_out):
        if not os.path.isdir(data_path_out):
            os.makedirs(data_path_out)
        self.save_map_to_file(self.in_word_id_dict, data_path_out + "/vocab_in_words")
        self.save_map_to_file(self.out_word_id_dict, data_path_out + "/vocab_out")
        self.save_map_to_file(self.letter_id_dict, data_path_out + "/vocab_in_letters")
        self.save_map_to_file(self.phrase_id_dict, data_path_out + "/vocab_phrase")

        return

    def convert_in_words_ids(self, words):

        if len(words) >= 2:
            ids_list = [self.in_word_id_dict[self.eos_flag]]
            for word in words:
                if word in self.in_word_id_dict:
                    ids_list.append(self.in_word_id_dict[word])
                elif word.lower() in self.in_word_id_dict:
                    ids_list.append(self.in_word_id_dict[word.lower()])
                elif word in self.emojis_dict:
                    ids_list.append(self.in_word_id_dict[self.emoji_flag])
                elif re.match(self.num_regex, word):
                    ids_list.append(self.in_word_id_dict[self.num_flag])
                elif re.match(self.pun_regex, word):
                    ids_list.append(self.in_word_id_dict[self.pun_flag])
                else:
                    ids_list.append(self.in_word_id_dict[self.unk_flag])

            str_ids = " ".join([str(id) for id in ids_list])
            return str_ids
        else:
            return None

    def convert_out_words_ids(self, words, lang):
        if lang == "en":
            eos_flag = self.en_flag + self.eos_flag
            und_flag = self.en_flag + self.und_flag
            unk_flag = self.en_flag + self.unk_flag
        else:
            eos_flag = self.es_flag + self.eos_flag
            und_flag = self.es_flag + self.und_flag
            unk_flag = self.es_flag + self.unk_flag

        if len(words) >= 2:
            ids_list = [self.out_word_id_dict[eos_flag]]
            for word in words:
                if word in self.out_word_id_dict:
                    ids_list.append(self.out_word_id_dict[word])
                elif word.lower() in self.out_word_id_dict:
                    ids_list.append(self.out_word_id_dict[word.lower()])
                elif lang == "en" and word[4:] in self.en_full_words_dict and word[4:] not in self.emojis_dict:
                    ids_list.append(self.out_word_id_dict[und_flag])
                else:
                    ids_list.append(self.out_word_id_dict[unk_flag])

            str_ids = " ".join([str(id) for id in ids_list])
            return str_ids
        else:
            return None

    def convert_letters_ids(self, letters_list):

        if len(letters_list) >= 2:
            str_letters_ids_list = [str(self.letter_id_dict[self.start_flag])]
            for letters in letters_list:
                letter_ids_list = [self.letter_id_dict[self.start_flag]]
                if len(letters) > 0 and letters not in self.emojis_dict:
                    for letter in letters:
                        if letter in self.letter_id_dict:
                            letter_ids_list.append(self.letter_id_dict[letter])
                        else:
                            letter_ids_list.append(self.letter_id_dict[self.unk_flag])
                str_letter_ids = " ".join([str(id) for id in letter_ids_list])
                str_letters_ids_list.append(str_letter_ids)
            str_letters_ids = "#".join(str_letters_ids_list)

            return str_letters_ids
        else:
            return None

    def convert_phrase_ids(self, words):

        if len(words) >= 2:
            ids_list = [self.phrase_id_dict[self.pad_flag]]
            for i in range(len(words)):
                if i + 1 < len(words):
                    phrase_2 = words[i] + " " + words[i+1]
                    if phrase_2 in self.phrase_id_dict:
                        ids_list.append(self.phrase_id_dict[phrase_2])
                        continue
                if i + 2 < len(words):
                    phrase_3 = words[i] + " " + words[i+1] + " " + words[i+2]
                    if phrase_3 in self.phrase_id_dict:
                        ids_list.append(self.phrase_id_dict[phrase_3])
                        continue
                if i + 1 < len(words):
                    ids_list.append(self.phrase_id_dict[self.not_phrase_flag])
                else:
                    ids_list.append(self.phrase_id_dict[self.pad_flag])

            str_ids = " ".join([str(id) for id in ids_list])
            return str_ids
        else:
            return None

    def convert_to_ids_file(self, data_path_in, data_path_out, lang, is_train):
        assert lang in ["en", "es"]
        phase = "train" if is_train else "dev"
        raw_file_reader = open(os.path.join(data_path_in, phase + "_data"), "r")
        words_id_file_writer = open(os.path.join(data_path_out, phase + "_in_ids_lm"), "a")
        letters_id_file_writer = open(os.path.join(data_path_out, phase + "_in_ids_letters"), "a")
        phrase_id_file_writer = open(os.path.join(data_path_out, phase + "_ids_phrase"), "a")

        for line in raw_file_reader:
            line = line.rstrip()
            line_split = line.split("|#|")
            letters = line_split[0].split("\t")
            in_words = line_split[1].split("\t")
            out_words = [self.en_flag + word for word in in_words] if lang == "en" else \
                [self.es_flag + word for word in in_words]

            if len(letters) != len(in_words):
                print(phase + " data line split error :", line)

            if len(in_words) == len(out_words) >= 2:
                in_words_id = self.convert_in_words_ids(in_words)
                out_words_id = self.convert_out_words_ids(out_words, lang)
                in_letters_id = self.convert_letters_ids(letters)
                phrase_id = self.convert_phrase_ids(in_words)

                if in_words_id and out_words_id and in_letters_id and phrase_id:
                    words_id_file_writer.write(in_words_id + "#" + out_words_id + "\n")
                    letters_id_file_writer.write(in_letters_id + "\n")
                    phrase_id_file_writer.write(phrase_id + "\n")

        raw_file_reader.close()
        words_id_file_writer.close()
        letters_id_file_writer.close()
        phrase_id_file_writer.close()

        return

    def convert_to_ids(self, en_path_in, es_path_in, data_path_out):
        self.convert_to_ids_file(en_path_in, data_path_out, lang="en", is_train=True)
        self.convert_to_ids_file(en_path_in, data_path_out, lang="en", is_train=False)

        self.convert_to_ids_file(es_path_in, data_path_out, lang="es", is_train=True)
        self.convert_to_ids_file(es_path_in, data_path_out, lang="es", is_train=False)

        return

    def build_words_keys_pair(self, file):
        words_keys_pair = dict()
        with open(file, "r") as f:
            for line in f:
                word, key, freq = line.strip().split("\t")
                if word not in words_keys_pair:
                    words_keys_pair[word] = {}
                words_keys_pair[word][key] = int(freq)

        for word in words_keys_pair.keys():
            keys_dict = words_keys_pair[word]
            freq_list = list(keys_dict.values())
            new_key_set = list(keys_dict.keys())

            num_samples = float(sum(freq_list))
            num_scale = [sum(freq_list[:i + 1]) / num_samples for i in range(len(freq_list))]
            words_keys_pair[word] = (new_key_set, num_scale)
        return words_keys_pair

    def words_keys_pair_replace(self, words):
        letters = []
        for word in words:

            if word not in self.words_keys_pair and word.lower() not in self.words_keys_pair:
                letters.append(word.lower())
            else:
                if word in self.words_keys_pair:
                    replaced_word = word
                else:
                    replaced_word = word.lower()
                random_number_01 = np.random.random_sample()
                keys, scale = self.words_keys_pair[replaced_word]
                id = min([i for i in range(len(scale)) if scale[i] > random_number_01])
                letters.append(keys[id])
        return letters

    def read_vocabs(self, path, phase):
        word_vocab_in = self.load_vocab(os.path.join(path, "vocab_in_words"),
                                           self.vocab_split_flag, 10000)
        word_vocab_out = self.load_vocab(os.path.join(path, "vocab_out"),
                                         self.vocab_split_flag, 10000, phase)
        letter_vocab = self.load_vocab(os.path.join(path, "vocab_in_letters"),
                                       self.vocab_split_flag, -1)
        phrase_vocab = self.load_vocab(os.path.join(path, "vocab_phrase"),
                                       self.vocab_split_flag, 10000)
        return word_vocab_in, word_vocab_out, letter_vocab, phrase_vocab

    def vocab_id_sort(self, vocab_dict):
        sorted_id_vocab = dict()
        id = 0
        for word in vocab_dict:
            if word in sorted_id_vocab:
                print("word repeat error:", word)
                continue
            sorted_id_vocab[word] = id
            id += 1
        return sorted_id_vocab

    def combine_vocab(self, en_path, es_path, en_es_path):
        en_word_vocab_in, en_word_vocab_out, en_letter_vocab, en_phrase_vocab = \
            self.read_vocabs(en_path, "en")
        es_word_vocab_in, es_word_vocab_out, es_letter_vocab, es_phrase_vocab = \
            self.read_vocabs(es_path, "es")
        en_es_word_vocab_in, en_es_word_vocab_out, en_es_letter_vocab, en_es_phrase_vocab = \
            self.read_vocabs(en_es_path, "mix")

        # self.in_word_id_dict = self.vocab_id_sort(dict(dict(en_word_vocab_in, **es_word_vocab_in), **en_es_word_vocab_in))
        # self.out_word_id_dict = self.vocab_id_sort(dict(dict(en_word_vocab_out, **es_word_vocab_out), **en_es_word_vocab_out))
        # self.letter_id_dict = self.vocab_id_sort(dict(dict(en_letter_vocab, **es_letter_vocab), **en_es_letter_vocab))
        # self.phrase_id_dict = self.vocab_id_sort(dict(dict(en_phrase_vocab, **es_phrase_vocab), **en_es_phrase_vocab))
        
        self.in_word_id_dict = self.vocab_id_sort(dict(en_word_vocab_in, **es_word_vocab_in))
        self.out_word_id_dict = self.vocab_id_sort(dict(en_word_vocab_out, **es_word_vocab_out))
        self.letter_id_dict = self.vocab_id_sort(dict(en_letter_vocab, **es_letter_vocab))
        self.phrase_id_dict = self.vocab_id_sort(dict(en_phrase_vocab, **es_phrase_vocab))

        return

    def combine_words_keys_pair(self, en_map_file, es_map_file):

        en_words_keys_pair = self.build_words_keys_pair(en_map_file)
        es_words_keys_pair = self.build_words_keys_pair(es_map_file)
        self.words_keys_pair = dict(en_words_keys_pair, **es_words_keys_pair)
        print("combine words keys map size :", len(self.words_keys_pair))

        return


if __name__ == "__main__":

    args = sys.argv

    en_path_in = args[1]
    es_path_in = args[2]
    en_es_path_in = args[3]
    en_word_keys_pair_map = args[4]
    es_word_keys_pair_map = args[5]
    en_full_vocab = args[6]
    es_full_vocab = args[7]
    emojis_file = args[8]
    en_es_path_out = args[9]

    data_producer = TrainDataProducer()
    data_producer.emojis_dict = data_producer.load_vocab(emojis_file, "\t+", -1)
    # data_producer.phrase_dict = data_producer.load_vocab(phrase_file, "##", "phrase")
    data_producer.en_full_words_dict = data_producer.load_vocab(en_full_vocab, "\t+", -1)
    data_producer.es_full_words_dict = data_producer.load_vocab(es_full_vocab, "\t+", -1)
    data_producer.combine_words_keys_pair(en_word_keys_pair_map, es_word_keys_pair_map)
    data_producer.combine_vocab(en_path_in, es_path_in, en_es_path_in)
    data_producer.save_vocab_files(en_es_path_out)

    data_producer.convert_to_ids(en_path_in, es_path_in, en_es_path_out)







