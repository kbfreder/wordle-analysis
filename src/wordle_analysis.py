#!/bin/python

"""
Version notes:
- v2
    - keep class / program open. Leverages user input. 
        Eliminates re-calc of word frequencies with each command
"""

import argparse
import os
import sys
import random
from collections import Counter, OrderedDict
import regex as re
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


ABOUT = """
    WordleAnalysis: scripts to analzye letters
    and letter combinations found in the Wordle word list.
    Only one command can be run at a time
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
    parser.add_argument(
        "--word-score",
        help="Show 'score' for a word, based on letter frequencies.",
    )
    args = parser.parse_args()
    return args


class WordleAnalysis:
    """
    """

    def __init__(self):
        self.dict_list, self.word_list = self._load_word_list()
        self._calc_letter_freq()
        self._calc_word_scores()

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

        self.letter_word_freq = letter_word_counts
        self.letter_freq = letter_freq_sorted

    def score_word_list(self, word_list, label):
        wf_scores = []
        lf_scores = []
        for w in word_list:
            wf_score = 0
            lf_score = 0
            char_set = set()
            for char in w:
                if char not in char_set:
                    char_set.add(char)
                    wf_score += self.letter_word_freq[char]
                    lf_score += self.letter_freq[char]

            wf_scores.append(wf_score)
            lf_scores.append(lf_score)

        word_score_df = pd.DataFrame(
            data=[word_list, wf_scores, lf_scores]).T
        word_score_df.columns=['word', 'word_freq_score', 'letter_freq_score']
        word_score_df['label'] = label
        return word_score_df

    def _calc_word_scores(self):

        wordle_df = self.score_word_list(self.word_list, 'wordle')
        dict_df = self.score_word_list(self.dict_list, 'dictionary')
        comb_df = pd.concat([wordle_df, dict_df], axis=0)
        
        mm_scaler = MinMaxScaler()
        scaled_scores = mm_scaler.fit_transform(
            comb_df[['word_freq_score', 'letter_freq_score']])

        scaled_scores_df = pd.DataFrame(scaled_scores, 
            columns=['word_freq_score', 'letter_freq_score'])
        scaled_scores_df['word'] = list(comb_df['word'])
        scaled_scores_df['label'] = list(comb_df['label'])

        scaled_scores_df.set_index('word', inplace=True)
        self.word_score_dict = scaled_scores_df.to_dict(orient='index')


    def get_random_words(self, word_list=None, n=10):
        if word_list is None:
            word_list = self.word_list
        print(random.sample(word_list, n))
    
    def show_letter_freq(self, letter):
        if letter == "all":
            # print(self.letter_freq)
            print("\n".join([f"{l}: {f:.3f}" for l,f in self.letter_freq.items()]))
        else:
            print(f"Frequency of words containing letter: "
                f"{self.letter_word_freq[letter]*100:.01f}%")
            print("Frequency of letter in all words: " 
            f"{self.letter_freq[letter]*100:.01f}%")
            print()

    def get_score_of_word(self, word):
        """Get word "score", based on letter frequencies
        Useful for starting guess
        """
        score_dict = self.word_score_dict.get(word, None)
        if score_dict is None:
            print("Word is not in dictionary.")

        else:
            score = np.mean([score_dict['word_freq_score'], 
                            score_dict['letter_freq_score']])
            print(f"{score:.04f}")
            if score_dict['label'] == 'dictionary':
                print("Note: word is not in Wordle list.")
    
    def letter_pattern(self, pattern, show_words=False):
        regex_patt = f'({pattern})'
        matching_words = [w for w in self.word_list if re.search(regex_patt, w) is not None]
        num = len(matching_words)
        pct = num / len(self.word_list)
        print(f"Number of words with letter pattern {num:,}")
        print(f"Fraction of words with letter pattern {pct*100:.2f}%")
        if show_words:
            print(matching_words)


def error_msg():
    print("Command not recognized. Please try again.")
    print(help_msg)
    print()

if __name__ == "__main__":
    wa = WordleAnalysis()
    # args = parse_args()
    print("Welcome to Wordle Analysis")
    # print(args)

    # if args.random:
    #     wa.get_random_words()
    
    # if args.letter_frequency is not None:
    #     wa.show_letter_freq(args.letter_frequency)
    
    # if args.word_score is not None:
    #     wa.get_score_of_word(args.word_score)

    help_msg = """Available commands:
    help: Print list of commands
    random: Print 10 random number of words from word list
    letter-frequency LETTER: Show letter frequency. 
        Sumbit 'all' to show frequency for all letters. 
    letter-pattern PATTERN [show|print]: Show statistics for words that
        contain PATTERN. Optionally, show (print) these words.
    word-score WORD: Show word score for that word
    exit: Exit the program.
    """

    default_msg = """Please type a command. 
    Type 'help' to list commands.
    Type 'exit' to exit the program.
    """
    
    cmd = ""
    print(default_msg)
    while cmd != "exit":
        cmd = input()
        
        if cmd == "help":
            print(help_msg)
        elif cmd == "random":
            print("Getting random words")
            wa.get_random_words()
        elif cmd in ["", "\n"]:
            continue
        else:
            cmd_list = cmd.split(" ")
            if len(cmd_list) == 2:
                print("parsing cmd + arg")
                arg, val = cmd_list
                if arg == "letter-frequency":
                    print("Fetching letter frequency")
                    wa.show_letter_freq(val)
                elif arg == "letter-pattern":
                    wa.letter_pattern(val)
                elif arg == "word-score":
                    print("Calculating word score")
                    wa.get_score_of_word(val)
                else: 
                    print("bad spot - 1")
                    error_msg()
            elif len(cmd_list) == 3:
                print("parsing cmd + arg + opt")
                arg, val, opt = cmd.split(" ")
                if arg == "letter-pattern":
                    if opt in ['SHOW', 'show', 'PRINT', 'print']:
                        wa.letter_pattern(val, True)
                    else:
                        print("bad spot - 2")
                        error_msg()
            else:
                print("bad spot - 3")
                error_msg()
        print()


