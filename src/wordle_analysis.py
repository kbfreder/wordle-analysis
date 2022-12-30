#!/bin/python

import argparse
import os
import sys
import random
from collections import Counter, OrderedDict


ABOUT = """
    WordleAnalysis: scripts to analzye letters
    and letter combinations found in the Wordle word list.
    """
WORD_LIST_PATH = "../input/nyt_wordle_list.txt"

def parse_args():
    parser = argparse.ArgumentParser(description=ABOUT)
    parser.add_argument(
        "--random",
        help="Print 10 random number of words from word list.",
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "--letter-frequency",
        help="Show letter frequency. Sumbit 'all' to show frequency "
        "for all letters. Submit a letter to see frequency for that "
        "letter.",
    )
    args = parser.parse_args()
    return args


class WordleAnalysis:
    """
    """

    def __init__(self):
        self.dict_list, self.word_list = self._load_word_list()
        self._calc_letter_freq()

    def _load_word_list(self):
        with open(WORD_LIST_PATH, "r") as file:
            raw_words = file.readline()
        
        raw_words = raw_words.split(',')
        parsed_words = [w.strip('"') for w in raw_words]
        
        # this is a guess as to what the first & second parts of the list represent
        split_idx = parsed_words.index('cigar')
        dict_words = parsed_words[:split_idx]
        wordle_words = parsed_words[split_idx:]

        return dict_words, wordle_words
    
    def _calc_letter_freq(self):
        word_list = self.word_list

        # How often a word contains a letter (irrespective of repeat letters in word)
        letter_word_counts = {}
        for char in [chr(x) for x in range(97, 123)]:
            num_words = len([word for word in word_list if char in word])
            letter_word_counts[char] = num_words / len(word_list)

        # How often letter appears in words (irrespective of repeat letters in word)
        letter_freq = Counter()
        for word in word_list:
            letter_freq.update(word)

        letter_freq_norm = {k:v/len(word_list) for k,v in letter_freq.items()}
        letter_freq_sorted = OrderedDict(sorted(letter_freq_norm.items()))

        self.letter_word_counts = letter_word_counts
        self.letter_freq = letter_freq_sorted

    def get_random_words(self, word_list=None, n=10):
        if word_list is None:
            word_list = self.word_list
        print(random.sample(word_list, n))
    
    def show_letter_freq(self, letter):
        if letter == "all":
            print(self.letter_freq)
        else:
            print(f"Frequency of words containing letter: "
                f"{self.letter_word_counts[letter]*100:.01f}%")
            print("Frequency of letter in all words: " 
            f"{self.letter_freq[letter]*100:.01f}%")




if __name__ == "__main__":
    wa = WordleAnalysis()
    args = parse_args()
    print("Welcome to Wordle Analysis")
    # print(args)

    if args.random:
        wa.get_random_words()
    
    if args.letter_frequency is not None:
        wa.show_letter_freq(args.letter_frequency)