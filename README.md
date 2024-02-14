# wordle-analysis
Analysis of Wordle words 


This was created with the intention of helping me play [Worlde](https://www.nytimes.com/games/wordle/index.html)
This is not a wordle clone, nor a [wordle-bot](https://www.nytimes.com/interactive/2022/upshot/wordle-bot.html) clone. It addresses these kinds of questions:
- what are the letter frequencies observed in "common" English words? 
    - *Should I prioritize a word with a 'P' or a 'C'?*
- calculate word "scores" based on said letter frequencies. 
    - *I need mathematical proof that my guesses are better than my partners.*
- show number of and optionally the list of words with given letter patterns, including options to restrict to words that start or end with the letter pattern
    - *How much brain power should I give to words that contain 'uo' or 'dn'?*

**WARNING: BORDERLINE CHEATING AHEAD**
- show number of and optionally the list of words that match the information I've gained from my Wordle game so far
    - *I give up and I want this to be over, but I'm too principled to actually cheat*


## Setup
- clone this repo
- create virtual environment and install packages in `requirements.txt`
    - `pip install -r requirements.txt`

- For web app, you will also need to install `tesseract` to your system. 

Here are some simple instrutions. You could also Google "how to install tesseract" and follow those; they are probably better. You may need to do this before you install the python library (`pytesseract`). I can't remember.

**On MacOS**
- `brew install tesseract`
    - note the tesseract directory using: `brew info tesseract` 
      (should be ~4th line)
        - you will need append `/bin/tesseract` to this to get the full "TESSERACT_PATH"
        - For example:

        ```bash
        $ brew info tesseract
        ==> tesseract: stable 5.3.1 (bottled), HEAD
        OCR (Optical Character Recognition) engine
        https://github.com/tesseract-ocr/
        /usr/local/Cellar/tesseract/5.3.1 (73 files, 32.2MB) *
        ...
        ```

        - TESSERACT_PATH = "/usr/local/Cellar/tesseract/5.3.1/bin/tesseract"

      - you may need to `chown` some folders

- create a  `.env` file at the root of this project, and paste:
    `export TESSERACT_PATH=<path from above>`
    - Note that we use this env var as follows in `src/cv.py`:
    `pytesseract.pytesseract.tesseract_cmd=TESSERACT_PATH`



## To use CLI tool:

- `cd src`
- `python worlde_analysis.py`
- type `help` to see a current list of commands and their arguments. Or see below if you trust that I've remember to update the README:
    ```
    Available commands:
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
    ```

## To use the webapp
- from the root of this project, run `python app.py`
- In your web browser, go to http://127.0.0.1:5000/
- Upload a screen shot, then click 'Analyze'!


## Development notes

### word list inputs
The first step in creating this Wordle aid was finding a list of Wordle words. While you can guess any 5-letter word in the English language, only a subset of "common" ones can be the solution. There is purportedly the "original" list of Wordle words, back when Josh Wardle ran it, and the "new" list which is curated by the NY Times. 

- `words_alpha.txt`: from https://github.com/dwyl/english-words.com
- `unigram_freq.csv`: word frequency list. https://www.kaggle.com/datasets/rtatman/english-word-frequency
- `words.txt`: So-called wordle world list. https://github.com/tabatkins/wordle-list
    - but is actually 14,000+ 5-letter words
- `words_solutions.py`: claims to be the wordle list from the original site. https://github.com/coolbutuseless/wordle/
- `wordle.31c3cb8f197aa9ad1b27e65327e43a0e621f3eb0.js`: NYT source file
    - needs to be parsed to get "actual" word list
    - first part of list appears to be all (or nearly all) 5-letter words. Then, second part of list (starting at 'cigar'), seems to be more "reasonable" words.
- `nyt_worlde_list.txt`: extracted word list from above


## Future ideas
- use information theory to suggest best next guess
- incorporate knowledge of past answers into this tool's advice
    - https://www.rockpapershotgun.com/wordle-past-answers