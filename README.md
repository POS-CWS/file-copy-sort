# file copy sort tool

This program is for sorting image files by day, assuming images use the naming format <text>yyyy.mm.dd.hh<text> ('.' can be any character). It could be retooled to sort other data or into other categories by changing how targetPath is created in the copy_folder method

Note that any type of file following that date format will be sorted. Any files that it cannot parse in this way will be put in an "unsorted" folder. Note that due to potential for same-named files to overwrite each other, this "unsorted" folder should not be counted on to contain everything in the source folders.

As of V1.2, this tool now supports separating different files based on other contents of the filename. Use any keyword or phrase present in all of the filenames you want separated, and the tool will create a subfolder in the target folder with that name. It will then copy and sort those files as normal, but separated into that subfolder. These keywords must be placed in the file "camera list.txt" in the program's folder, one keyword per line. An unlimited number of keywords are supported. Note that if a file matches multiple keywords, it will be linked to the first of the matches.

In addition to the standard python 3 libraries, this tool requires PyQt5. Installation instructions can be found in the Welcome repository on Github. Also note that using a version of python >= 3.8 is highly recommended, as this update significantly optimized file transfer times. Using older versions is likely to take 3 or 4 times as long to copy files.

Copyright (C) 2018-2021 Gregory O'Hagan (GNU v3 licence).

Version 1.3

### Usage notes:
* Run the program by running "file copy sort.py". No other file manipulation is necessary.
   * On Rasbian, run using "sudo Python 'file copy sort.py'"
   * Note that if you are running using the terminal, the current terminal path needs to be in this program's folder for the tool to find its config files
* Select the source and the destination path either by browsing or by typing in the path, then press "Start copy/sort"
* The source folder is searched recursively (i.e. subfolders too) for all files in it.
* If the program is closed/terminated for any reason, it can detect where it left off on its own. Simply restart the program, set the same source destination, and it will resume.
* For the above reason, never assume the program has finished a copy/sort until you explicitly the message that it has finished.
* The program will often stop responding for a few minutes when it starts very big folders. This is normal - just let it run. After a while it should start giving update messages


### Other notes:
* Overwriting and PST correction can be toggled in the file menu.
   * "PST correction" is used when the files are in UTC time, but want to be sorted according to PST days.
   * "Automatic PST correction" is generally what should be used. This mode accounts for when our camera standard changed from PST to UTC.
   * "Overwriting" determines whether it will auto-detect files in the target location
     * If enabled, it will copy everything found, overwriting as necessary. If disabled, it will skip files if it detects these already in the target folder.

