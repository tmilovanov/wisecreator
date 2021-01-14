@echo off

echo [.] Building
pyinstaller --log-level=WARN --clean ^
	--onefile --noupx --name wisecreator ^
	--add-data="wisecreator/data;./data/" ^
	--add-data="wisecreator/third_party;./third_party" ^
	./wisecreator/main.py
echo [.] Done
