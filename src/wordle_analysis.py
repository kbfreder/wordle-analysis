#!/bin/python

"""
Version notes:
- v2
    - keep class / program open. Leverages user input. 
        Eliminates re-calc of word frequencies with each command

TODO:
- add better error handling (e.g. if `letter-frequency` gets passed string 
    that isn't 'all' or a single letter)
- detect pressing up key to repeat last command
"""

import argparse
import readline # not used but necessary
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
        # self._calc_letter_freq()
        # self._calc_word_scores()
        self.word_score_dict = None
        self.letter_freq = None

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

    def _calc_word_scores(self):

        wordle_df = self._score_word_list(self.word_list, 'wordle')
        dict_df = self._score_word_list(self.dict_list, 'dictionary')
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

    def _score_word_list(self, word_list, label):
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

    def get_random_words(self, word_list=None, n=10):
        if word_list is None:
            word_list = self.word_list
        print(random.sample(word_list, n))
    
    def show_letter_freq(self, letter):
        if self.letter_freq is None:
            self._calc_letter_freq()
        if letter == "all":
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
        if self.word_score_dict is None:
            self._calc_word_scores()
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
        print(f"Number of words with letter pattern: {num:,}")
        if show_words:
            matching_words.sort()
            print(matching_words)

    def starts_with(self, pattern, show_words=False):
        regex_patt = r"^" + re.escape(pattern)
        matching_words = [w for w in self.word_list if re.search(regex_patt, w) is not None]
        num = len(matching_words)
        print(f"Number of words that start with pattern: {num:,}")
        if show_words:
            matching_words.sort()
            print(matching_words)

    def ends_with(self, pattern, show_words=False):
        regex_patt = re.escape(pattern) + r"$"
        matching_words = [w for w in self.word_list if re.search(regex_patt, w) is not None]
        num = len(matching_words)
        print(f"Number of words that end with pattern: {num:,}")
        if show_words:
            matching_words.sort()
            print(matching_words)

    def cheat(self, yes_letters, no_letters, show=False):
        yes_letters = [x.lower() for x in yes_letters]
        no_letters = [x.lower() for x in no_letters]

        matching_words = [w for w in self.word_list if 
                          len(set(w).intersection(set(yes_letters))) 
                          == len(yes_letters)]
        remaining_words = [w for w in matching_words if 
                   len(set(w).intersection(set(no_letters))) == 0]
        print(f"Number remaining words: {len(remaining_words)}")
        if show:
            matching_words.sort()
            print(remaining_words)


def error_msg():
    print("Command not recognized. Please try again.")
    print(help_msg)
    print()

if __name__ == "__main__":
    wa = WordleAnalysis()
    print("Welcome to Wordle Analysis")

    help_msg = """Available commands:
    help: Print list of commands
    random: Print 10 random number of words from word list
    word-score WORD: Print word score for that word
    letter-frequency LETTER: Print letter frequency of LETTER.
        Pass 'all' to show frequency for all letters. 
    letter-pattern PATTERN [show|print]: Print statistics for words that
        contain PATTERN. Optionally, show (print) these words.
    starts-with PATTERN [show|print]: Print number of words that 
        start with PATTERN. Optionally, show (print) these words.
    ends-with PATTERN [show|print]: Print number of words that 
        end with PATTERN. Optionally, show (print) these words.
    cheat YES-LETTERS NO-LETTERS [show|print]: Show words that contain 
        YES-LETTERS but don't container NO-LETTERS. Does not take 
        letter positions into account. Optionally show (print)
        these words.
    exit: Exit the program.
    """

    default_msg = """Please type a command. 
    Type 'help' to list commands.
    Type 'exit' to exit the program.
    """
    
    entry = ""
    print(default_msg)
    while True:
        entry = input()
        
        if entry == "help":
            print(help_msg)
        elif entry == "random":
            print("Getting random words")
            wa.get_random_words()
        elif entry in ["", "\n"]:
            continue
        elif entry in ["exit", "EXIT", "quit", "QUIT"]:
            print("Goodbye")
            sys.exit(0)
        else:
            entry_list = entry.split(" ")
            cmd = entry_list[0]
            args = entry_list[1:]
            if cmd == "letter-frequency":
                wa.show_letter_freq(args[0])
            elif cmd == "word-score":
                wa.get_score_of_word(args[0])
            elif cmd == "letter-pattern":
                if args[-1] in ['SHOW', 'show', 'PRINT', 'print']:
                    wa.letter_pattern(args[0], True)
                else:
                    wa.letter_pattern(args[0], False)
            elif cmd == "starts-with":
                if args[-1] in ['SHOW', 'show', 'PRINT', 'print']:
                    wa.starts_with(args[0], True)
                else:
                    wa.starts_with(args[0], False)
            elif cmd == "ends-with":
                if args[-1] in ['SHOW', 'show', 'PRINT', 'print']:
                    wa.ends_with(args[0], True)
                else:
                    wa.ends_with(args[0], False)
            elif cmd == "cheat":
                print("Cheater!")
                if args[-1] in ['SHOW', 'show', 'PRINT', 'print']:
                    wa.cheat(args[0], args[1], show=True)
                else:
                    wa.cheat(args[0], args[1], show=False)
            else:
                error_msg()
        print()


