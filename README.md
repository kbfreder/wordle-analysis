# wordle-analysis
Analysis of Wordle words 


This was created with the intention of helping me play [Worlde](https://www.nytimes.com/games/wordle/index.html)
This is not a wordle clone, nor a [wordle-bot](https://www.nytimes.com/interactive/2022/upshot/wordle-bot.html) clone. It addresses these kinds of questions:
- what are the letter frequencies observed in "common" English words? 
    - *Should I prioritize a word with a 'P' or a 'C'?*
- calculate word "scores" based on said letter frequencies. 
    - *I need mathematical proof that my guesses are better than my partners.*

**WARNING: BORDERLINE CHEATING AHEAD**
- show words with given letter patterns
    - *How much brain power should I give to words that contain 'uo' or 'dn'?*
- show words that contain certain letters but not others
    - *I give up and I want this to be over, but I'm too principled to actually cheat*

FUTURE FEATURES 
(i.e. I have them in a Jupyter noteboo, but I haven't added them to the script yet)
- show words that start with one or more letters
- show words that end with one or more letter

FUTURE FUTURE FEATURES
- incorporate positional information into letter knowledge
    - *I'm lazy and I want the answer handed to me on a python platter*


## To use `world-analysis`:
- clone this repo
- install necessary requirements
    - `pip install -r requirements.txt`
- `cd src`
- `python worlde_analysis.py`
- type `help` to see a current list of commands and their arguments. Or see below if you trust that I've remember to update the README:
    ```
    Available commands:
    help: Print list of commands
    random: Print 10 random number of words from word list
    letter-frequency LETTER: Show letter frequency. 
        Sumbit 'all' to show frequency for all letters. 
    letter-pattern PATTERN [show|print]: Show statistics for words that
        contain PATTERN. Optionally, show (print) these words.
    word-score WORD: Show word score for that word
    cheat YES-LETTERS NO-LETTERS: Show words that contain YES-LETTERS
        but don't container NO-LETTERS. Does not currently take 
        letter positions into account
    exit: Exit the program.
    ```

## Development notes

### word list inputs
The first step in creating this Wordle aid was finding a list of Wordle words. While you can guess any word in the English language, only a subset of "common" ones can be the solution. There is purportedly the "original" list of Wordle words, back when Josh Wardle ran it, and the "new" list which is curated by the NY Times. 

- `words_alpha.txt`: from https://github.com/dwyl/english-words.
- `unigram_freq.csv`: word frequency list. https://www.kaggle.com/datasets/rtatman/english-word-frequency
- `words.txt`: So-called wordle world list. https://github.com/tabatkins/wordle-list
    - but is actually 14,000+ 5-letter words
- `words_solutions.py`: claims to be the wordle list from the original site. https://github.com/coolbutuseless/wordle/
- `wordle.31c3cb8f197aa9ad1b27e65327e43a0e621f3eb0.js`: NYT source file
    - needs to be parsed to get word list
    - appears to have list of words in the middle. first part of list appears to be all (or nearly all) 5-letter words. Then, second part of list (starting at 'cigar'), seems to be more "reasonable" words.
- `nyt_worlde_list.txt`: extracted word list from above

## Future ideas
- incorporate knowledge of past answers into this tool's advice
    - https://www.rockpapershotgun.com/wordle-past-answers