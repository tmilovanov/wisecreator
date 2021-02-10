import unittest
from wisecreator import rawml
from wisecreator.common import Gloss

class RawmlParserTester(unittest.TestCase):
    def test_without_line_breaks(self):
        content = "<html><head><title>Simple Title</title></head><body><p>Simple paragraph</p></body></html>"
        r = rawml.RawmlRarser(content)
        words = r.parse()
        expected = [
            Gloss(offset=19, word='Simple'),
            Gloss(offset=26, word='Title'),
            Gloss(offset=55, word='Simple'),
            Gloss(offset=62, word='paragraph'),
        ]
        self.assertEqual(expected, words)

    def test_with_line_breaks(self):
        content = "<html>\n<head>\n<title>Simple Title</title>\n</head>\n<body>\n<p>Simple paragraph</p>\n</body>\n</html>"
        r = rawml.RawmlRarser(content)
        words = r.parse()
        expected = [
            Gloss(offset=21, word='Simple'),
            Gloss(offset=28, word='Title'),
            Gloss(offset=60, word='Simple'),
            Gloss(offset=67, word='paragraph'),
        ]
        self.assertEqual(expected, words)

    def test_with_line_breaks2(self):
        content = "<html><head><title>Simple Title\n</title>\n</head>\n<body>\n<p>\nSimple\nparagraph</p>\n</body>\n</html>"
        r = rawml.RawmlRarser(content)
        words = r.parse()
        expected = [
            Gloss(offset=19, word='Simple'),
            Gloss(offset=26, word='Title'),
            Gloss(offset=60, word='Simple'),
            Gloss(offset=67, word='paragraph'),
        ]
        self.assertEqual(expected, words)

    def test_several_paragraphs_in_line(self):
        content = "<html><body><p>ParagraphOne</p><p>ParagraphTwo</p>\r\n<p>ParagraphThree</p><p>ParagraphFour</p>"
        r = rawml.RawmlRarser(content)
        words = r.parse()
        expected = [
            Gloss(offset=15, word='ParagraphOne'),
            Gloss(offset=34, word='ParagraphTwo'),
            Gloss(offset=55, word='ParagraphThree'),
            Gloss(offset=76, word='ParagraphFour'),
        ]
        self.assertEqual(expected, words)

    def test_unicode_content(self):
        content = "<p>Hello," + b"\xc2\xa0".decode("utf-8") + "world</p>"
        r = rawml.RawmlRarser(content)
        words = r.parse()
        expected = [
            Gloss(offset=3, word='Hello'),
            Gloss(offset=11, word='world'),
        ]
        self.assertEqual(expected, words)