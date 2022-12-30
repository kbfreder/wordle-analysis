# wordle-analysis
Analysis of 5-letter words in the English language


## input
- `words_alpha.txt`: from https://github.com/dwyl/english-words.
- `unigram_freq.csv`: word frequency list. https://www.kaggle.com/datasets/rtatman/english-word-frequency
- `words.txt`: So-called wordle world list. https://github.com/tabatkins/wordle-list
    - but is actually 14,000+ 5-letter words
- `words_solutions.py`: claims to be the wordle list from the original site. https://github.com/coolbutuseless/wordle/
- `wordle.31c3cb8f197aa9ad1b27e65327e43a0e621f3eb0.js`: NYT source file
    - needs to be parsed to get word list
    - appears to have list of words in the middle. first part of list appears to be all (or nearly all) 5-letter words. Then, second part of list (starting at 'cigar'), seems to be more "reasonable" words.
- `nyt_worlde_list.txt`: extracted word list from above