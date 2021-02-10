import os
import re
import sys
import shutil
import subprocess
from pathlib import Path

from wisecreator.common import WiseException
from wisecreator.rawml import RawmlRarser
from wisecreator.utils import (run_process, prepare_empty_folder, block_print, enable_print,
                               get_path_to_kindle_unpack, get_path_to_py_interpreter)
from wisecreator.third_party.KindleUnpack.lib.kindleunpack import unpackBook


class Book:
    def __init__(self, path, mobitool_path):
        self.path = Path(path)
        self.f_name = self.path.stem
        self.f_ext = self.path.suffix
        self.mobitool_path = Path(mobitool_path)

    def get_glosses(self):
        print("[.] Getting rawml content of the book")
        try:
            book_content = self._get_rawml_content()
        except WiseException as e:
            print("  [-] Can't get rawml content:")
            print("    |", e)
            raise

        print("[.] Collecting words")
        parser = RawmlRarser(book_content)
        words = parser.parse()

        return words

    def get_or_create_asin(self):
        print("[.] Getting ASIN")
        book_asin = self._get_book_asin()
        if book_asin is not None:
            return book_asin
        else:
            print("  [-] No ASIN found generating new one")

        print("[.] Converting book to generate ASIN")
        # Convert mobi to mobi by calibre and get ASIN that calibre assign to converted book
        try:
            converted_book_path = self.path.parent / f"tmp_book_{self.f_name}{self.f_ext}"
            cmd_str = "{} \"{}\" \"{}\"".format('ebook-convert', self.path, converted_book_path)
            out = subprocess.check_output(cmd_str, shell=True)
            shutil.move(converted_book_path, self.path)
        except Exception as e:
            print("  [-] Failed to convert mobi to mobi:")
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

    def _book_type(self) -> str:
        # ".azw3" -> "azw3"
        # ".mobi" -> "mobi"
        # ...
        return self.f_ext[1:]

    def _unpack_book(self) -> Path:
        unpack_path = self.path.parent / "unpacked"
        prepare_empty_folder(unpack_path)

        block_print()
        try:
            unpackBook(str(self.path), str(unpack_path), None, '2', False, True)
        except Exception as e:
            description = ["Failed to unpack book", e]
            raise WiseException("", description)
        finally:
            enable_print()

        return unpack_path

    def _get_rawml_content(self):
        unpack_path = self._unpack_book()

        if self._book_type() == "azw3":
            path_to_rawml = unpack_path / "mobi8" / "assembled_text.dat"
        elif self._book_type() == "mobi":
            path_to_rawml = unpack_path / "mobi7" / f"{self.f_name}.rawml"

        try:
            with open(path_to_rawml, 'rt', encoding='utf-8') as f:
                book_content = f.read()
            return book_content
        except UnicodeDecodeError as e:
            message = ["Failed to open {} - {}".format(path_to_rawml, e)]
            raise WiseException("", message)
        finally:
            shutil.rmtree(unpack_path)

    def _get_book_asin(self):
        command = [self.mobitool_path, self.path]
        command = map(str, command)
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
        except Exception:
            message = ["Failed to decode mobitool output"]
            raise WiseException("", message)
