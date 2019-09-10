import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from html.parser import HTMLParser

from wisecreator.common import WiseException

@dataclass
class Gloss:
    offset: int
    word: str


class RawmlRarser(HTMLParser):
    def __init__(self, book_content, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bt = book_content
        self.result = []
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
            word_offset = self.getpos()[1] + match.start()
            word_byte_offset = self.last_token_bt_offset + len(
                self.bt[self.last_token_offset:word_offset].encode('utf-8'))
            self.last_token_offset = word_offset
            self.last_token_bt_offset = word_byte_offset
            self.result.append(Gloss(offset=word_byte_offset, word=word))


class Book:
    def __init__(self, path, mobitool_path):
        self.path = path
        self.mobitool_path = mobitool_path
        self.f_name, self.f_ext = os.path.splitext(os.path.basename(path))

    def get_rawml_content(self):
        command = [self.mobitool_path, '-d', self.path]
        try:
            proc = subprocess.Popen(command, stdout=subprocess.PIPE)
            out, err = proc.communicate()
        except Exception as e:
            command_str = " ".join(command)
            description = ["Failed to run command", command_str, e]
            raise WiseException("", description)

        try:
            rawml_name = "{}.rawml".format(self.f_name)
            path_to_rawml = os.path.join(os.path.dirname(self.path), rawml_name)
            with open(path_to_rawml, 'rt', encoding='utf-8') as f:
                book_content = f.read()
            os.remove(path_to_rawml)
            return book_content
        except UnicodeDecodeError as e:
            message = ["Failed to open {} - {}".format(path_to_rawml, e)]
            raise WiseException("", message)

    def get_glosses(self):
        print("[.] Getting rawml content of the book")
        try:
            book_content = self.get_rawml_content()
        except WiseException as e:
            print("  [-] Can't get rawml content:")
            print("    |", e)
            raise ValueError()

        print("[.] Collecting words")
        parser = RawmlRarser(book_content)
        words = parser.parse()
        return words

    def _get_book_asin(self):
        command = [self.mobitool_path, self.path]
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

    def get_or_create_asin(self):
        print("[.] Getting ASIN")
        book_asin = self._get_book_asin()
        if book_asin != None:
            return book_asin
        else:
            print("  [-] No ASIN found generating new one")

        print("[.] Converting mobi 2 mobi to generate ASIN")
        # Convert mobi to mobi by calibre and get ASIN that calibre assign to converted book
        try:
            converted_book_path = os.path.join(os.path.dirname(self.path),
                                               "tmp_book_{}{}".format(self.f_name, self.f_ext))

            cmd_str = "{} \"{}\" \"{}\"".format('ebook-convert', self.path, converted_book_path)
            out = subprocess.check_output(cmd_str, shell=True)

            shutil.move(converted_book_path, self.path)
        except Exception as e:
            print("  [-] Failed to convert mobi 2 mobi:")
            print("    |", e)
            raise ValueError()

        try:
            book_asin = self._get_book_asin()
        except WiseException as e:
            print("  [-] Can't get ASIN:")
            for item in e.desc:
                print("    |", item)
            raise ValueError()

        return book_asin