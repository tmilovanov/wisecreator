#!/bin/bash

echo [.] Building
# --clean   Clean PyInstaller cache and remove temporary files before building.
# --onefile Create a one-file bundled executable
# --name    Name of the executable
# --add-data Add data to executable. Format:
# 		--add-data="SRC;DST" on Windows
# 		--add-data="SRC:DST" on Linux
# 		DST is a path relative to executable file, when running. Data will be unpacked to this path
pyinstaller --log-level=WARN --clean \
	--onefile --noupx --name wisecreator \
	--add-data="wisecreator/data:./data/" \
	--add-data="wisecreator/third_party:./third_party" \
	./wisecreator/main.py
echo [.] Done