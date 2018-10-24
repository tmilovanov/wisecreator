#WiseCreator

You can create wordwise enabled .mobi files by using
- either [standalone executables](#standalone) or
- [pure python script](#script) (runs faster)

---

##standalone

1. You need to have [calibre](https://calibre-ebook.com/) on your device.
2. If you are on windows, download [executables/wisecreator.exe](https://github.com/tmilovanov/wisecreator/blob/master/executables/wisecreator.exe)
3. If you are on linux, download [executables/wisecreator](https://github.com/tmilovanov/wisecreator/blob/master/executables/wisecreator)
4. Finally run the below commands in a shell  
    Windows: `wisecreator.exe PATH_TO_YOUR_MOBI_BOOK`   
    Linux &nbsp; &nbsp; &nbsp;: `./wisecreator PATH_TO_YOUR_MOBI_BOOK`

*You can move standalone wisecreator file anywhere you like on your computer, but if you are using calibre portable simply copy that to /Calibre folder and run above command from that location*  

##script

1.  You need to have [calibre](https://calibre-ebook.com/) on your device.  
2.	To run the script you need to have [Python3](https://www.python.org/downloads/)  
3. 	Make sure you have these Python libs:  
	[NLTK](http://www.nltk.org/)  
	sqlite3 - included in standard library, or if your python has been built from source, use `pip install pysqlite3`
4. 	Run wisecreator:  
    `./main.py PATH_TO_YOUR_MOBI_BOOK`

*calibre console utility "ebook-convert" is used inside the script*

---

To develop:

You need pyinstaller to pack executables. You can install it with pip.
