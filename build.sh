#!/bin/bash

pyinstaller --onefile --noupx --log-level=WARN --clean \
	-n wisecreator \
    --add-data="filter.txt:."\
    --add-data="senses.csv:."\
    --add-data="third_party:./third_party"\
    --add-data="nltk_data:./nltk_data"\
    ./main.py

