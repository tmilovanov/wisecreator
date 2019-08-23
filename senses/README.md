# senses

Run `senses.py` can help you generate `senses.csv`.

Words in `all.csv` will show if you enable WordWise, and you can find the id in `WordWise.kll.en.en.db` like below.

```
#/data/data/com.amazon.kindle/databases/wordwise/WordWise.kll.en.en.db

#lemmas
id      lemma
10454	directive

#senses
id      term_lemma_id
170	    10454

#directive,170
```

## value

The value of words in `5.txt` is 5, and these words will show only when you select 'More Hints'. 

If a word exists in `5.txt` and `4.txt`, its value is 5. 

If a word only exists in `all.csv`, its value is 1.

You can edit `*.txt` as you like, links below may help you.

https://github.com/first20hours/google-10000-english

https://github.com/dolph/dictionary

https://github.com/jnoodle/English-Vocabulary-Word-List

https://github.com/jjzz/ZZ-WordFreq/

```
#5.txt -> oxford 3000
#4.txt -> cet6
#3.txt -> bnc15000
#2.txt -> popular.txt in https://github.com/dolph/dictionary
```
