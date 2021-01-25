This program is for sorting image files by day, assuming images use
the naming format <text>yyyy.mm.dd.hh<text> ('.' can be any character)
It could be retooled to sort other data or into other categories
by changing how targetPath is created in the copy_folder method

Note that any type of file following that date format will be sorted. Any files
that it cannot parse in this way will be put in an "unsorted" folder. Note that
due to overwriting files, this "unsorted" folder should not be counted on to 
contain everything in the source folders.

As of V1.2, it now supports separating different files based on other contents of
the filename. Use any keyword or phrase present in all of the filenames you want
separated, and the tool will create a subfolder in the target folder with that name.
It will then copy those files as normal, but into that subfolder. These keywords
must be placed in the file "camera list.txt" in the program's folder, one keyword
per line. An unlimited number of keywords are supported. Note that if a file matches
multiple keywords, it will be linked to the first of the matches.

Copyright (C) 2018-2019 Gregory O'Hagan (GNU v3 licence)
Version 1.2

If any questions arise during use or modifications, feel free to contact the creator at:
	gregoryrohagan@gmail.com

In addition to the standard python libraries, this requires PyQt4:
• PyQt4 can be installed by following the instructions in the top answer here:
   • https://stackoverflow.com/questions/22640640/how-to-install-pyqt4-on-windows-using-pip

Usage notes:
• Run the program by running "start.py". No other file manipulation is necessary.
   • On Rasbian, run using "sudo Python start.py"
   • Note that you need to run it from its folder for the tool to find its config files
• Select the source and the destination path either by browsing or by typing
  in the path, then press "Start copy/sort"
• The source folder is searched recursively (i.e. subfolders too) for all files in it.
• If the program is closed/terminated for any reason, it can detect where it left
  off. Simply restart the program, set the same source destination, and it will resume
• For the above reason, never assume the program has finished a copy/sort until you
  explicitly see it tell you.
• The program will stop responding for a few minutes when it starts very big folders.
  This is normal - just let it run. After a while it should start giving update messages
• It will 


Other notes:
• Overwriting and PST correction can be toggled in the file menu.
   • "PST correction" is used when the files are in UTC time, but want to be
     sorted according to PST days.
   • "Automatic PST correction" is generally what should be used.
   • "Overwriting" determines whether it will auto-detect files in the target location
     • If enabled, it will copy everything, overwriting as necessary.
• This program is optimized for Python 2. It can run using Python 3, but will take
   about 3x as much time
• 

