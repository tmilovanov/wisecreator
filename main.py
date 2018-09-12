#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import subprocess
import sys
import shutil
import os
import shutil
import re
import nltk
import platform
import cursor
import time
from html.parser import HTMLParser

DEBUG = False

class WiseException(Exception):
    def __init__(self, message, desc):
        super().__init__(message)

        self.desc = desc

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(base_path, relative_path)

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
    if iteration == 0:
        cursor.hide()

    bar_length = shutil.get_terminal_size()[0] // 2

    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '+' * filled_length + '-' * (bar_length - filled_length)

    progress_bar = "\r%s |%s| %s%s %s" % (prefix, bar, percents, '%', suffix)

    print(progress_bar, end='', flush=True)

    if iteration == total:
        print("")
        cursor.show()

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


class WordFilter:
    def __init__(self):
        filter_path = get_resource_path("filter.txt")
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

    def add_gloss(self, start, sense_id, difficulty):
        self.open_db()
        try:
            query = "INSERT INTO glosses VALUES (?,?,?,?,?)"
            new_gloss = (start, None, difficulty, sense_id, 0)
            self.cursor.execute(query, new_gloss)
        except sqlite3.Error as e:
            pass


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
        pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        paragraph_text = data
        for match in re.finditer(r'[A-Za-z\']+', paragraph_text):
            word = paragraph_text[match.start():match.end()]
            if self.wf.is_take_word(word):
                word_offset = self.getpos()[1] + match.start()
                word_byte_offset = self.last_token_bt_offset + len(self.bt[self.last_token_offset:word_offset].encode('utf-8'))
                self.last_token_offset = word_offset
                self.last_token_bt_offset = word_byte_offset
                self.result.append((word_byte_offset, word))

def get_path_to_mobitool():
    path_to_third_party = get_resource_path("third_party")

    if platform.system() == "Linux":
        path_to_mobitool = os.path.join(path_to_third_party, "mobitool-linux-i386")
    if platform.system() == "Windows":
        path_to_mobitool = os.path.join(path_to_third_party, "mobitool-win32.exe")
    if platform.system() == "Darwin":
        path_to_mobitool = os.path.join(path_to_third_party, "mobitool-osx-x86_64")

    return path_to_mobitool

def get_book_asin(path_to_book):
    path_to_mobitool = get_path_to_mobitool()

    command = [path_to_mobitool, path_to_book]
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        out, err = proc.communicate()
    except Exception as e:
        command_str = " ".join(command)
        description = ["Failed to run command", command_str, e]
        raise WiseException("", description)

    try:
        book_metadata = out.decode("utf-8")
        match = re.search("ASIN: (\S+)", book_metadata)
        if match:
            book_asin = match.group(1)
            return book_asin
        else:
            return None
    except Exception as e:
        message = ["Failed to decode mobitool output"]
        raise WiseException("", message)

def get_rawml_content(path_to_book):
    path_to_mobitool = get_path_to_mobitool()

    command = [path_to_mobitool, '-d', path_to_book]
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        out, err = proc.communicate()
    except Exception as e:
        command_str = " ".join(command)
        description = ["Failed to run command", command_str, e]
        raise WiseException("", description)

    try:
        book_name = os.path.basename(path_to_book)
        book_name_without_ex = os.path.splitext(book_name)[0]
        rawml_name = "{}.rawml".format(book_name_without_ex)
        path_to_rawml = os.path.join(os.path.dirname(path_to_book), rawml_name)
        with open(path_to_rawml, 'rt', encoding='utf-8') as f:
            book_content = f.read()
        os.remove(path_to_rawml)
        return book_content
    except UnicodeDecodeError as e:
        message = ["Failed to open {} - {}".format(path_to_rawml, e)]
        raise WiseException("", message)

def check_dependencies():
    try:
        subprocess.check_output('ebook-convert --version', shell=True)
    except FileNotFoundError as e:
        raise ValueError("Calibre not found")

    path_to_nltk = get_resource_path("nltk_data")
    if os.path.exists(path_to_nltk) == False:
        raise ValueError(path_to_nltk + " not found")

    path_to_mobitool = get_path_to_mobitool()
    if os.path.exists(path_to_mobitool) == False:
        raise ValueError(path_to_mobitool + " not found")


def main():
    if len(sys.argv) < 2:
        return usage()
    print("[.] Checking dependenices")
    try:
        check_dependencies()
    except ValueError as e:
        print("  [-] Checking failed:")
        print("    |", e)
        return

    path_to_script = os.path.dirname(os.path.realpath(__file__))
    path_to_nltk = os.path.join(path_to_script, "nltk_data")
    nltk.data.path = [ path_to_nltk ] + nltk.data.path

    path_to_book = os.path.abspath(sys.argv[1])
    if os.path.exists(sys.argv[1]) == False:
        print("[-] Wrong path to book: {}".format(path_to_book))
        sys.exit()

    book_name = os.path.basename(path_to_book)
    book_name_without_ex = os.path.splitext(book_name)[0]
    result_dir_name = "{}-WordWised".format(book_name_without_ex)
    result_dir_path = os.path.join(os.path.dirname(path_to_book), result_dir_name)
    new_book_path = os.path.join(result_dir_path, book_name)

    if os.path.exists(result_dir_path):
        shutil.rmtree(result_dir_path)

    if not os.path.exists(result_dir_path):
        os.makedirs(result_dir_path)

    print("[.] Converting mobi 2 mobi to generate ASIN")
    #Convert mobi to mobi by calibre and get ASIN that calibre assign to converted book
    try:
        cmd_str = "{} \"{}\" \"{}\"".format('ebook-convert', path_to_book, new_book_path)
        out = subprocess.check_output(cmd_str, shell=True)
    except Exception as e:
        print("  [-] Failed to convert mobi 2 mobi:")
        print("    |", e)
        return
    path_to_book = new_book_path

    print("[.] Getting ASIN")
    try:
        book_asin = get_book_asin(new_book_path)
    except WiseException as e:
        print("  [-] Can't get ASIN:")
        for item in e.desc:
            print("    |", item)
        return

    print("[.] Getting rawml content of the book")
    try:
        book_content = get_rawml_content(path_to_book)
    except WiseException as e:
        print("  [-] Can't get rawml content:")
        print("    |", e)
        return


    sdr_dir_name = "{}.sdr".format(book_name_without_ex)
    sdr_dir_path = os.path.join(result_dir_path, sdr_dir_name)
    if not os.path.exists(sdr_dir_path):
        os.makedirs(sdr_dir_path)

    LangLayerDb = LanguageLayerDB(sdr_dir_path, book_asin)

    print("[.] Collecting words")
    parser = RawmlRarser(book_content)
    words = parser.parse()
    count = len(words)
    if count == 0:
        print("[.] There are no suitable words in the book")
        return
    else:
        print("[.] Count of words: {}".format(count))

    lookup = {}
    senses_path = get_resource_path("senses.csv")
    with open(senses_path, 'rb') as f:
        f = f.read().decode('utf-8')
        for line in f.splitlines():
            l = line.strip()
            if l[0] == '"':
                continue
            word, sense_id = l.split(',')
            lookup[word] = sense_id

    difficulty_dict = {}
    ngsl_path = get_resource_path("ngsl.csv")
    with open(senses_path, 'rb') as f:
        f = f.read().decode('utf-8')
        for line in f.splitlines():
            l = line.strip()
            if l[0] == '"':
                continue
            word, coverage = l.split(',')
            difficulty_dict[word] = float(coverage)

    lemmatizer = nltk.WordNetLemmatizer()
    prfx = "[.] Processing words: "
    print_progress(0, count, prefix=prfx, suffix='')
    LangLayerDb.start_transaction()
    if DEBUG == True:
        f = open('log.txt', 'a')
    for i, gloss in enumerate(words):
        word_offset = gloss[0]
        word = gloss[1]
        word = word.lower()
        pos_tag = nltk.pos_tag([word])[0][1]
        pos_tag_wordnet = get_wordnet_pos(pos_tag)
        word = lemmatizer.lemmatize(word, pos=pos_tag_wordnet)
        if word in lookup:
            sense_id = lookup[word]
            if DEBUG == True:
                f.write("{} - {} - {}\n".format(word_offset, word, sense_id))
            difficulty = 1
            if word in difficulty_dict:
                coverage = difficulty_dict[word]
                if (coverage < 0.96):
                    difficulty = 4
                elif coverage < 0.992:
                    difficulty = 3
                elif coverage < 0.9984:
                    difficulty = 2
            LangLayerDb.add_gloss(word_offset, sense_id, difficulty)
        print_progress(i+1, count, prefix=prfx, suffix='')

    if DEBUG == True:
        f.close()
    LangLayerDb.end_transaction()
    LangLayerDb.close_db()

    print("[.] Success!")
    print("Now copy this folder: \"{}\" to your Kindle".format(result_dir_path))

if __name__ == "__main__":
    main()
