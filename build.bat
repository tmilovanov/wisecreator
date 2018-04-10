@echo off

echo [.] Building
pyinstaller --onefile --noupx --log-level=WARN --clean ^
	-n wisecreator ^
	--add-data="nltk_data;./nltk_data" ^
	--add-data="filter.txt;." ^
	--add-data="senses.csv;." ^
	--add-data="third_party;./third_party" ^
	./main.py
