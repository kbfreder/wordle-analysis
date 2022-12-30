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
WORD_LIST_PATH = "../input/words_solutions.txt"

def parse_args():
    parser = argparse.ArgumentParser(description=ABOUT)
    # parser.add_argument(
    #     "-h",  "--help",
    #     action="store_true",
    #     help="Print help message",
    #     default=False,
    # )
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
        self.word_list = self._load_word_list()
        self._calc_letter_freq()

    def _load_word_list(self):
        with open(WORD_LIST_PATH, "r") as file:
            raw_words = []
            for line in file.readlines():
                raw_words.append(line.strip().strip("\n"))
        
        word_list = []
        for row in raw_words:
            for x in row.split(","):
                if x != "":
                    word_list.append(x.strip().strip('"'))
        
        return word_list
    
    def _calc_letter_freq(self):
        word_list = self.word_list
        letter_word_counts = {}
        for char in [chr(x) for x in range(97, 123)]:
            num_words = len([word for word in word_list if char in word])
            letter_word_counts[char] = num_words / len(word_list)

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