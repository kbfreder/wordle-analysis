#!/bin/python

"""
Version notes:
- v2
    - keep class / program open. Leverages user input. 
        Eliminates re-calc of word frequencies with each command

TODO:
- create a "setup script" that computes
    - word lists (split between "dictionary" and "wordle" words)
    - letter frequencies
    - word scores (?)
    --> then, here, we just load them
- allow addition of word to wordle list (and remember them!)
    - probably in this setup script
- add better error handling (e.g. if `letter-frequency` gets passed string 
    that isn't 'all' or a single letter)
"""

import os
import argparse
import readline # not used but necessary
import sys
import random
from collections import Counter, OrderedDict
from itertools import chain
import regex as re
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


ABOUT = """
    WordleAnalysis: scripts to analzye letters
    and letter combinations found in the Wordle word list.
    Only one command can be run at a time
    """
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
WORD_LIST_PATH = "../input/nyt_wordle_list.txt"


class WordleAnalysis:
    """
    """

    def __init__(self):
        self.dict_list, self.word_list = self._load_word_list()
        self.word_score_dict = None
        self.letter_freq = None

    def _load_word_list(self):
        word_list_path = os.path.join(BASE_DIR, WORD_LIST_PATH)
        with open(word_list_path, "r") as file:
            raw_words = file.readline()
        
        raw_words = raw_words.split(',')
        parsed_words = [w.strip('"').upper() for w in raw_words]
        
        # this is a guess as to what the first & second parts of the list represent
        split_idx = parsed_words.index('CIGAR')
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
        if self.letter_freq is None:
            self._calc_letter_freq()
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
    
    def get_letter_freq(self, letter):
        # letter = letter.lower()
        if self.letter_freq is None:
            self._calc_letter_freq()
        if letter == "all":
            print("\n".join([f"{l}: {f:.3f}" for l,f in self.letter_freq.items()]))
        elif letter in self.letter_freq.keys():
            print(f"Frequency of words containing letter: "
                f"{self.letter_word_freq[letter]*100:.01f}%")
            print("Frequency of letter in all words: " 
            f"{self.letter_freq[letter]*100:.01f}%")
            print()
        else:
            print(f"Letter not found in dictionary: {letter}")

    def get_score_of_word(self, word):
        """Get word "score", based on letter frequencies
        Useful for starting guess
        """
        # word = word.lower()
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
        # pattern = pattern.lower()
        regex_patt = re.escape(pattern) 
        matching_words = [w for w in self.word_list if re.search(regex_patt, w) is not None]
        num = len(matching_words)
        print(f"Number of words with letter pattern: {num:,}")
        if show_words:
            matching_words.sort()
            print(matching_words)

    def starts_with(self, pattern, show_words=False):
        # pattern = pattern.lower()
        regex_patt = r"^" + re.escape(pattern)
        matching_words = [w for w in self.word_list if re.search(regex_patt, w) is not None]
        num = len(matching_words)
        print(f"Number of words that start with pattern: {num:,}")
        if show_words:
            matching_words.sort()
            print(matching_words)

    def ends_with(self, pattern, show_words=False):
        # pattern = pattern.lower()
        regex_patt = re.escape(pattern) + r"$"
        matching_words = [w for w in self.word_list if re.search(regex_patt, w) is not None]
        num = len(matching_words)
        print(f"Number of words that end with pattern: {num:,}")
        if show_words:
            matching_words.sort()
            print(matching_words)

    def cheat(self, green, yellow, gray, show=False):
        """
        Prints number, and optionally the list, of words matching supplied patterns.

        params:
        --------
        green (str): pattern of green letters, using '-' to denote
            non-green positions. Ex: -a-e-
            Enter a blank string if no green letters known.
        yellow (list[str]): yellow letter patterns. Letters that are known to 
            be in the word, but for which exact position is not known. 
            Ex: [---l-, ----t] or [-e-e-]
            Enter an empty string if no yellow letters known.
        gray (str): gray letters. Letters that are known to not be in 
            the word. Ex: pos
        show (bool): Whether to return the list of words.

        returns: None
        """
        regex_patt = r""
        for i, char in enumerate(green):
            no_chars = gray[:]
            if char == "-":
                for ylist in yellow:
                    if ylist[i] != '-':
                        no_chars += ylist[i]
                regex_patt += r"[^" + re.escape(no_chars) + r"]"
            else:
                regex_patt += re.escape(char)
        matching_words = [w for w in self.word_list if re.search(regex_patt, w) is not None]

        nested_y_lett = [list(set(ylist)) for ylist in yellow]
        messy_y_lett = list(chain.from_iterable(nested_y_lett))
        yellow_letters = [y for y in messy_y_lett if y != '-']

        remaining_words = matching_words[:]
        for y in yellow_letters:
            remaining_words = [w for w in remaining_words if y in w]
        len(remaining_words)

        print(f"Number matching words: {len(remaining_words)}")
        if show:
            remaining_words.sort()
            print(remaining_words)

    def new_cheat(self, list_of_guesses, list_of_patterns, print_words=False):
        """Given guesses and resulting patterns, returns number of remaining words,
        and optionally, those words.
        
        list_of_guesses: list of words guessed
            Ex: ['POETS', 'TREAD'] or [['P','O','E','T','S']]
        lift_of_patterns: list of match patterns
            0 for gray, 1 for yellow, 2 for green
            Ex: [[0,0,2,1,0], [2,1,2,0,0]]
        """
        num_rows = len(list_of_guesses)
        rows = [list(zip(list_of_guesses[r], list_of_patterns[r])) for r in range(num_rows)]
        
        matching_words = self.word_list[:]
        for row in rows:
            # first pass: get gray & yellow letters
            gray_letters = []
            yellow_letters = []
            for i, (c, m) in enumerate(row):
                if m == 0:
                    gray_letters.append(c)
                elif m == 1:
                    yellow_letters.append(c)

            # second pass, derive green+gray regex    
            green_gray_regex = r""
            for i, (c, m) in enumerate(row):
                if m == 2:
                    green_gray_regex += re.escape(c)
                else:
                    no_chars = ''.join(gray_letters)
                    if m == 1:
                        # add yellow letter
                        no_chars += c
                    green_gray_regex += r"[^" + re.escape(no_chars) + r"]"


            # do initial regex select
            matching_words = [w for w in matching_words 
                            if re.search(green_gray_regex, w) is not None]
            
            # apply yellow letter constraints
            for y in yellow_letters:
                matching_words = [w for w in matching_words if y in w]
        
        print(f"Number matching words: {len(matching_words)}")
        if print_words:
            print(matching_words)
            return matching_words
        else:
            return len(matching_words)

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
    cheat green GREEN-PATTERN yellow YELLOW-ANTIPATTERN1,YELLOW-ANTIPATTERN2,...
        gray GRAY-LETTERS [show|print]: 
        Show words that match GREEN-PATTERN, match the YELLOW-ANTIPATTERNS but don't 
        contain GRAY-LETTERS. Ex: `cheat green t-e-- yellow -rr-- gray posad` means
        T in the first position, E in the third, R is in the word but not the second
        or third positions, and ADOPS are not in the word.
        For GREEN and YELLOW patterns, use '-' to denote non-color positions.
        For GREEN, enter the position you know the letter(s) to be in. 
        For YELLOW, enter the positions you know the letter(s) to *not* be in.
            Enter one anti-pattern string for each yellow letter. Use a comma to 
            separate letter pattners, *but no space*.
            e.g. if your first guess was STYLE, and L and the E were yellow, you 
            would enter: 'cheat yellow ---L-,----E grey STY'.
        Optionally show (print) these words.
        
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
        entry = entry.lower()

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
                wa.get_letter_freq(args[0])
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
                show =  False
                green = "-----"
                yellow = []
                gray = ""
                for i, arg in enumerate(args):
                    if arg == "green":
                        green = args[i+1]
                    if arg == "yellow":
                        yellow = args[i+1].split(',')
                    if (arg == "gray") or (arg == "grey"):
                        gray = args[i+1]
                    if arg in ['SHOW', 'show', 'PRINT', 'print']:
                        show = True

                wa.cheat(green, yellow, gray, show)
            else:
                error_msg()
        print()
