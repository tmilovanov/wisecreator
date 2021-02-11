@echo off

echo [.] Building
rem --clean   Clean PyInstaller cache and remove temporary files before building.
rem --onefile Create a one-file bundled executable
rem --name    Name of the executable
rem --add-data Add data to executable. Format:
rem 		--add-data="SRC;DST" on Windows
rem 		--add-data="SRC:DST" on Linux
rem 		DST is a path relative to executable file, when running. Data will be unpacked to this path
pyinstaller --log-level=WARN --clean ^
	--onefile --noupx --name wisecreator ^
	--add-data="wisecreator/data;./data/" ^
	--add-data="wisecreator/third_party;./third_party" ^
	./wisecreator/main.py
echo [.] Done
