import re
from html.parser import HTMLParser

from wisecreator.common import Gloss

class RawmlRarser(HTMLParser):
    """
    RawmlParser extracts (word_byte_offset; word) pairs from UTF-8 text
    rawml is an xml-based format
    """

    def __init__(self, content: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = []
        self.content = content
        self.lines = content.splitlines(keepends=True)

        # self.lines_length[i] is a number of bytes in all lines before i-th line
        self.lines_length = []
        self.lines_length.append(0)
        for i in range(1, len(self.lines)):
            self.lines_length.append(self.lines_length[i-1] + len(self.lines[i-1].encode("utf-8")))

    def parse(self):
        self.feed(self.content)
        return self.result

    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def get_word_byte_offset(self, tag_content: str, offset_inside_tag_content):
        """
        Get word byte offset in a text

        offset_inside_tag_content is an offset in UTF-8 characters, not in bytes
        """

        line_number, tag_content_offset = self.getpos()
        line_number = line_number - 1 # Line numbers in HTMLParser enumerated starting from 1, not from 0
        bytes_before_line = self.lines_length[line_number]
        bytes_before_tag_content = len(self.lines[line_number][:tag_content_offset].encode("utf-8"))
        bytes_before_word = len(tag_content[:offset_inside_tag_content].encode("utf-8"))
        result = 0
        result += bytes_before_line
        result += bytes_before_tag_content
        result += bytes_before_word
        return result

    def handle_data(self, tag_content):
        line_number, tag_content_offset = self.getpos()
        line_number = line_number - 1  # Line numbers in HTMLParser enumerated starting from 1, not from 0
        bytes_before_line = self.lines_length[line_number]
        bytes_before_tag_content = len(self.lines[line_number][:tag_content_offset].encode("utf-8"))
        last_token_end = 0

        for start, end in iter_english_words(tag_content):
            bytes_before_word = len(tag_content[:start].encode("utf-8"))
            result = 0
            result += bytes_before_line
            result += bytes_before_tag_content
            result += bytes_before_word

            self.result.append(Gloss(offset=result, word=tag_content[start:end]))


def iter_english_words(text):
    for match in re.finditer(r'[A-Za-z\'-]+', text):
        yield match.start(), match.end()
