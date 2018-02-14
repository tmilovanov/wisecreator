#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import subprocess
import sys
import os
import shutil
import re
import nltk
from html.parser import HTMLParser

#TODO:
#0.Do not require mobitool and calibre binaries
#1.Deside how to hande difficulty of word
#2.Get metadata of kll.en.en.klld for initalization of LanguageLayerDB

# Got it from https://gist.github.com/aubricus/f91fb55dc6ba5557fbab06119420dd6a
# Print iterations progress
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return nltk.corpus.wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return nltk.corpus.wordnet.VERB
    elif treebank_tag.startswith('N'):
        return nltk.corpus.wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return nltk.corpus.wordnet.ADV
    else:
        return nltk.corpus.wordnet.NOUN

def usage():
    print("./main.py input_book")

class WordFilter():
    def __init__(self):
        script_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))
        filter_path = os.path.join(script_dir, "filter.txt")
        with open(filter_path, 'rt') as f:
            self.do_not_take = []
            for line in f:
                if line.strip()[0] == '#':
                    continue
                word = line.strip()
                self.do_not_take.append(word)

    def is_take_word(self, word):
        lword = word.lower()

        if word in self.do_not_take:
            return False

        #Do not take words with contractions
        #like "tree's", "he'll", "we've", e.t.c
        if word.find('\'') != -1:
            return False

        return True

class LanguageLayerDB():
    def __init__(self, path_to_dir, book_asin):
        self.asin = book_asin
        self.conn = None
        self.cursor = None
        self.path_to_dir = path_to_dir
        self.open_db()
        try:
            query = "CREATE TABLE glosses (start INTEGER PRIMARY KEY, end INTEGER, difficulty INTEGER, sense_id INTEGER, low_confidence BOOLEAN)"
            r = self.cursor.execute(query)
            query = "CREATE TABLE metadata (key TEXT, value TEXT)"
            r = self.cursor.execute(query)
        except sqlite3.Error as e:
            print(e)

        en_dictionary_version = "2016-09-14"
        en_dictionary_revision = '57'
        en_dictionary_id = 'kll.en.en'

        metadata = {
            'acr': 'CR!W0W520HKPX6X12GRQ87AQC3XW3BV',
            'targetLanguages' : 'en',
            'sidecarRevision' : '45',
            'ftuxMarketplaces' : 'ATVPDKIKX0DER,A1F83G8C2ARO7P,A39IBJ37TRP1C6,A2EUQ1WTGCTBG2',
            'bookRevision' : 'b5320927',
            'sourceLanguage' : 'en',
            'enDictionaryVersion' : en_dictionary_version,
            'enDictionaryRevision' : en_dictionary_revision,
            'enDictionaryId' : en_dictionary_id,
            'sidecarFormat' : '1.0',
        }

        try:
            for key, value in metadata.items():
                query = "INSERT INTO metadata VALUES (?, ?)"
                r = self.cursor.execute(query, (key, value))
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    def open_db(self):
        if self.conn == None:
            db_name = "LanguageLayer.en.{}.kll".format(self.asin)
            path_to_db = os.path.join(self.path_to_dir, db_name)
            self.conn = sqlite3.connect(path_to_db)
            self.cursor = self.conn.cursor()

    def close_db(self):
        self.conn.close()
        self.conn = None

    def start_transaction(self):
        self.cursor.execute("BEGIN TRANSACTION")
    
    def end_transaction(self):
        self.conn.commit()

    def add_gloss(self, start, sense_id):
        self.open_db()
        try:
            query = "INSERT INTO glosses VALUES (?,?,?,?,?)"
            new_gloss = (start, None, 1, sense_id, 0)
            self.cursor.execute(query, new_gloss)
        except sqlite3.Error as e:
            print(e)


class RawmlRarser(HTMLParser):
    def __init__(self, book_content, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bt = book_content
        self.result = []
        self.wf = WordFilter()
        self.last_token_offset = 0
        self.last_token_bt_offset = 0

    def parse(self):
        self.feed(self.bt)
        return self.result

    def handle_starttag(self, tag, attrs):
        self.tag_content_start = self.getpos()[1] + len(self.get_starttag_text())

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        paragraph_text = data
        for match in re.finditer(r'[A-Za-z\']+', paragraph_text):
            word = paragraph_text[match.start():match.end()]
            if self.wf.is_take_word(word):
                word_offset = self.tag_content_start + match.start()
                word_byte_offset = self.last_token_bt_offset + len(self.bt[self.last_token_offset:word_offset].encode('utf-8'))
                self.last_token_offset = word_offset
                self.last_token_bt_offset = word_byte_offset
                self.result.append((word_byte_offset, word))

def get_book_asin(path_to_book):
    path_to_mobitool = os.path.join(os.path.dirname(os.path.realpath(__file__)), "mobitool/mobitool-linux-i386")
    proc = subprocess.Popen([path_to_mobitool, path_to_book], stdout=subprocess.PIPE)
    out, err = proc.communicate()
    book_metadata = out.decode("utf-8")
    match = re.search("ASIN: (\S+)", book_metadata)
    if match:
        book_asin = match.group(1)
        return book_asin
    else:
        return None

def main():
    if len(sys.argv) < 2:
        return usage()
    
    path_to_book = sys.argv[1]
    if os.path.exists(sys.argv[1]):
        path_to_book = os.path.abspath(sys.argv[1])
    else:
        print("Cannot find " + sys.argv[1])
        sys.exit()

    book_name = os.path.basename(path_to_book)
    book_name_without_ex = os.path.splitext(book_name)[0]
    result_dir_name = "{}-WordWised".format(book_name_without_ex)
    result_dir_path = os.path.join(os.path.dirname(path_to_book), result_dir_name)
    new_book_path = os.path.join(result_dir_path, book_name)

    if not os.path.exists(result_dir_path):
        os.makedirs(result_dir_path)

    print("Getting ASIN of the book")
    book_asin = get_book_asin(path_to_book)
    if book_asin != None:
        shutil.copy(path_to_book, new_book_path)
    else:
        print("There isn't ASIN, converting mobi 2 mobi...")
        #Convert mobi to mobi by calibre and get ASIN that calibre assign to converted book
        proc = subprocess.Popen(['ebook-convert', path_to_book, new_book_path], stdout=subprocess.PIPE)
        out, err = proc.communicate()
        book_asin = get_book_asin(new_book_path)
    path_to_book = new_book_path

    path_to_mobitool = os.path.join(os.path.dirname(os.path.realpath(__file__)), "mobitool/mobitool-linux-i386")
    proc = subprocess.Popen([path_to_mobitool, '-d', path_to_book], stdout=subprocess.PIPE)
    out, err = proc.communicate()

    rawml_name = "{}.rawml".format(book_name_without_ex)
    path_to_rawml = os.path.join(os.path.dirname(path_to_book), rawml_name)
    with open(path_to_rawml, 'rt') as f:
        book_content = f.read()

    sdr_dir_name = "{}.sdr".format(book_name_without_ex)
    sdr_dir_path = os.path.join(result_dir_path, sdr_dir_name)
    if not os.path.exists(sdr_dir_path):
        os.makedirs(sdr_dir_path)

    LangLayerDb = LanguageLayerDB(sdr_dir_path, book_asin)

    print("Collecting words...")
    parser = RawmlRarser(book_content)
    words = parser.parse()
    count = len(words)
    if count == 0:
        print("There are no suitable words in the book")
        return
    else:
        print("Count of words: {}".format(count))

    lookup = {}
    script_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    senses_path = os.path.join(script_dir, "senses.csv")
    with open(senses_path, 'rt') as f:
        for line in f:
            l = line.strip()
            if l[0] == '"':
                continue
            word, sense_id = l.split(',')
            lookup[word] = sense_id


    lemmatizer = nltk.WordNetLemmatizer()
    print_progress(0, count, prefix='Processing words:', suffix='Complete')
    LangLayerDb.start_transaction()
    for i, gloss in enumerate(words):
        word_offset = gloss[0]
        word = gloss[1]
        word = word.lower()
        pos_tag = nltk.pos_tag([word])[0][1]
        pos_tag_wordnet = get_wordnet_pos(pos_tag)
        word = lemmatizer.lemmatize(word, pos=pos_tag_wordnet)
        if word in lookup:
            sense_id = lookup[word]
            LangLayerDb.add_gloss(word_offset, sense_id)
        print_progress(i+1, count, prefix='Processing words:', suffix='Complete')

    LangLayerDb.end_transaction()
    LangLayerDb.close_db()
    os.remove(path_to_rawml)
    print("Now copy this folder: \"{}\" to your Kindle".format(result_dir_path))

def test_parser():
    text = """<p height="0pt" width="2em" align="justify"><font color="#000000">And, if you aren't from my school, which I assume everybody who isn't a fourteen to eighteen year old in Talket County, Wisconsin isn't, then to inform you: a blue slip of paper is your only ticket </font><i><font color="#000000">out</font></i><font color="#000000"> during the seven hour period of in-service time we spend here every week from Monday to Friday. Unless, of course, there's an unintentional fire, or an active shooter roaming the hallways, or something of that kind of sort. I say unintentional fires only, though, because all eight hundred teenaged students that go here can recall the 'Great Blaze of Valentine's Day', which occurred a little over a year ago when some nerdy kid in chemistry class set sparks to Kelsey Gordon's ponytail with a flaming flask of acetone. </font></p>"""
    parser = RawmlRarser(text)
    words = parser.parse()
    for offset, word in words:
        print(word)


if __name__ == "__main__":
    main()
