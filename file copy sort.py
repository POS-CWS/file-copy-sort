import re
import sys
import os
import time
from datetime import date, timedelta
import shutil

from functools import partial

osWin = False
if "win" in sys.platform:
	import ctypes
	from ctypes import wintypes
	osWin = True


# Used in the copy_file method. This (and copy_file method) is based on code by Michael Burns:
# https://stackoverflow.com/questions/22078621/python-how-to-copy-files-fast
try:
	O_BINARY = os.O_BINARY
except:
	O_BINARY = 0

READ_FLAGS = os.O_RDONLY | O_BINARY
WRITE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY
BUFFER_SIZE = 128 * 1024

# Determine which version of python we are working with, for the copy method.
py2 = True
if sys.version_info > (3, 0):
	py2 = False
	from PyQt5 import QtGui, QtCore, uic, QtWidgets
	from PyQt5.QtWidgets import *
	from PyQt5.QtCore import *
	from PyQt5.QtGui import *
else:
	from PyQt4 import QtCore
	from PyQt4.QtGui import *


app = None


def main():
	global app
	app = QApplication(sys.argv)
	ex = Program()
	sys.exit(app.exec_())


# Copies a single file. Optimized for python 2
# Based on code by Michael Burns:
# https://stackoverflow.com/questions/22078621/python-how-to-copy-files-fast
def copyfile(src, dst):
	global py2, osWin
	if py2 and osWin:
		try:
			fin = os.open(src, READ_FLAGS)
			stat = os.fstat(fin)
			fout = os.open(dst, WRITE_FLAGS, stat.st_mode)
			for x in iter(lambda: os.read(fin, BUFFER_SIZE), ""):
				os.write(fout, x)
		finally:
			try:
				os.close(fin)
			except:
				pass
			try:
				os.close(fout)
			except:
				pass
	else:
		shutil.copy2(src, dst)


# Primary program. Sorts files, provides GUI
class Program(QMainWindow):
	def __init__(self):
		super(Program, self).__init__()

		# Set a few program-scope variables for later
		self.working = False
		self.filesCopied = 0
		self.filesNotParsed = 0
		self.filesSkipped = 0
		self.correctForZulu = 1
		self.allowOverwrite = False
		self.months = {'1': "January", '2': 'February', '3': 'March', '4': 'April', '5': 'May', '6': 'June',
				  '7': 'July', '8': 'August', '9': 'September', '10': 'October', '11': 'November', '12': 'December'}
		self.cameraList = []

		# set central layout and some default window options
		self.mainWidget = QWidget()
		self.setCentralWidget(self.mainWidget)
		self.setGeometry(400, 250, 800, 200)
		self.setWindowTitle('Image Copy/Sort tool')

		self.mainLayout = QVBoxLayout()
		self.mainWidget.setLayout(self.mainLayout)

		self.locWidget = QWidget()
		self.locLayout = QGridLayout()
		self.locWidget.setLayout(self.locLayout)
		self.mainLayout.addWidget(self.locWidget)

		# Add text lines and buttons for selecting the folders
		# Also link the functions to keep them in sync, and to verify that the paths exist
		self.inpathBox = QLineEdit("")
		self.locLayout.addWidget(self.inpathBox, 1, 0)
		self.inpathBtn = QPushButton("  Select source folder  ")
		self.inpathBtn.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
		self.inpathBtn.clicked.connect(partial(self.select_path, self.inpathBox))
		self.inpathBox.textChanged.connect(self.verify_paths)
		self.locLayout.addWidget(self.inpathBtn, 0, 0)

		self.outpathBox = QLineEdit("")
		self.locLayout.addWidget(self.outpathBox, 1, 1)
		self.inpathBtn = QPushButton("  Select destination folder  ")
		self.inpathBtn.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
		self.inpathBtn.clicked.connect(partial(self.select_path, self.outpathBox))
		self.outpathBox.textChanged.connect(self.verify_paths)
		self.locLayout.addWidget(self.inpathBtn, 0, 1)

		# Add bar for bottom buttons
		self.controlsWidget = QWidget()
		self.controlsLayout = QHBoxLayout()
		self.controlsWidget.setLayout(self.controlsLayout)
		self.mainLayout.addWidget(self.controlsWidget)

		# Add the button to transfer the files
		# Initially, this is inactive since we need the user to select inpath/outpath first
		self.sortBtn = QPushButton("  Start copy/sort  ")
		self.sortBtn.setEnabled(False)
		self.sortBtn.clicked.connect(self.start_copy_sort)
		self.controlsLayout.addSpacerItem(build_horiz_spacer())
		self.controlsLayout.addWidget(self.sortBtn)
		self.controlsLayout.addSpacerItem(build_horiz_spacer())

		# Create "options" menu. Provide options for zulu correction and forced overwrite
		self.statusBar()
		self.mainMenu = self.menuBar()
		self.optionsMenu = self.mainMenu.addMenu('&Options')

		self.toggleZuluAction = QAction("toggle zulu", self)
		self.toggleZuluAction.triggered.connect(self.toggle_zulu)
		self.optionsMenu.addAction(self.toggleZuluAction)

		self.toggleOverwriteAction = QAction("toggle overwrite", self)
		self.toggleOverwriteAction.triggered.connect(self.toggle_overwrite)
		self.optionsMenu.addAction(self.toggleOverwriteAction)

		# Properly sets text and status tips
		self.update_options_menu_text()

		self.load_camera_list()
		self.show()

	# Toggles forced overwrite mode, and updates the text in the options menu
	def toggle_overwrite(self):
		self.allowOverwrite = not self.allowOverwrite
		self.update_options_menu_text()

	# Toggles the zulu to pst correction, and updates the text in the options menu
	def toggle_zulu(self):
		self.correctForZulu = (self.correctForZulu + 1) % 3
		self.update_options_menu_text()

	# Sets the text and tool tips for the options menu based on current settings
	def update_options_menu_text(self):
		if self.correctForZulu == 2:
			self.toggleZuluAction.setText("toggle zulu to pst (currently enabled)")
			self.toggleZuluAction.setStatusTip("Toggles zulu to pst time correction.\nCurrently enabled")
		elif self.correctForZulu == 1:
			self.toggleZuluAction.setText("toggle zulu to pst (currently automatic)")
			self.toggleZuluAction.setStatusTip("Toggles zulu to pst time correction.\nCurrently automatic")
		else:
			self.toggleZuluAction.setText("toggle zulu to pst (currently disabled)")
			self.toggleZuluAction.setStatusTip("Toggles zulu to pst time correction.\nCurrently disabled")
		if self.allowOverwrite:
			self.toggleOverwriteAction.setText("toggle file overwrite (currently enabled)")
			self.toggleOverwriteAction.setStatusTip("Toggle to only overwrite potentially corrupted files."
													+ " This allows resuming partially completed sorts, and is the recommended mode")
		else:
			self.toggleOverwriteAction.setText("toggle file overwrite (currently disabled)")
			self.toggleOverwriteAction.setStatusTip("Toggle to overwrite ALL pre-existing files when copying. Not recommended")

	# Method for combining lineEdit and fileSelect methods of getting the path
	def select_path(self, lineEdit):
		folder = QFileDialog.getExistingDirectory(self, "Select Directory")
		if folder:
			lineEdit.setText(str(folder))

	# Checks whether the inpath and outpath exists.
	# Enables and disables the sort button based on this, and places feedback on it
	def verify_paths(self):
		inExists = os.path.exists(str(self.inpathBox.text()))
		outExists = os.path.exists(str(self.outpathBox.text()))
		if not inExists and not outExists:
			self.sortBtn.setEnabled(False)
			self.sortBtn.setText("Need inpath and outpath")
		elif not inExists:
			self.sortBtn.setEnabled(False)
			self.sortBtn.setText("Need inpath")
		elif not outExists:
			self.sortBtn.setEnabled(False)
			self.sortBtn.setText("Need outpath")
		else:
			if not self.working:
				self.sortBtn.setEnabled(True)
			self.sortBtn.setText("Start copy/sort")

	def load_camera_list(self):
		try:
			with open("camera list.txt", 'r') as infile:
				for line in infile:
					if len(line) > 0:
						self.cameraList.append(line.strip())
			self.statusBar().showMessage("Loaded {} camera(s) to separate from main sort".format(len(self.cameraList)))

		except:
			self.statusBar().showMessage("Error loading camera list")

	# A wrapper for copy_sort below, but with surrounding functionality:
	# reads inpath/outpath from gui, resets counts
	def start_copy_sort(self):
		self.working = True
		self.sortBtn.setEnabled(False)
		# Get paths
		inpath = str(self.inpathBox.text())
		outpath = str(self.outpathBox.text())
		# Reset counts
		self.filesCopied = 0
		self.filesNotParsed = 0
		self.filesSkipped = 0

		self.statusBar().showMessage("Starting copy...")

		# Start the sort
		self.copy_folder(inpath, outpath)

		message = "Finished. " + str(self.filesCopied) + " files copied, " + \
									str(self.filesSkipped) + " files skipped, " + str(self.filesNotParsed) + \
									" files " + "not parsed and placed in unsorted foler."
		self.statusBar().showMessage(message)
		print(message)
		self.working = False
		self.verify_paths()

	# Copies every file in a folder. Handles subfolders as well if recurse is set to True
	def copy_folder(self, inpath, outpathBase, recurse=True):
		# Get our list of files to copy. Sort alphabetically for consistency
		fileList = os.listdir(inpath)
		fileList.sort()

		# These let us resume if needed. Overwriting the last file in a list overwrites a potentially corrupted file.
		resuming = True
		lastFileTarget = ''
		lastFileSrc = ''
		for filename in fileList:
			# update the gui each iteration
			app.processEvents()

			# If the target is a folder, recurse into it (if we are sorting recursively)
			if os.path.isdir(os.path.join(inpath, filename)):  # if not re.match("^.+\..+$", filename):
				if recurse:
					self.copy_folder(os.path.join(inpath, filename), outpathBase)
			# The filename is a file
			else:
				m = re.search("(\d\d\d\d).(\d\d).(\d\d).(\d\d).(\d\d)", filename)
				targetPath = ""
				if m:
					fileDate = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
					# Convert from zulu to pst (if needed)
					if self.correctForZulu > 0 and int(m.group(4)) < 8:
						if self.correctForZulu == 2 or (fileDate.year > 2017 or (fileDate.year == 2017 and fileDate.month > 5) or (fileDate.year == 2017 and fileDate.month == 5 and fileDate.day >= 22)):
							fileDate = fileDate - timedelta(days=1)

					# check if the file belongs to a camera being sorted out
					subfolder = None
					for c in self.cameraList:
						if c in filename:
							subfolder = c
							break

					# Build path
					if subfolder:
						targetPath = os.path.join(outpathBase, subfolder, str(fileDate.year),
											  str(fileDate.month) + "_" + self.months[str(fileDate.month)], str(fileDate.day))
					else:
						targetPath = os.path.join(outpathBase, str(fileDate.year),
											  str(fileDate.month) + "_" + self.months[str(fileDate.month)], str(fileDate.day))
				# If the file name cannot be parsed, place it in a generic folder
				else:
					targetPath = os.path.join(outpathBase, "unsorted")
					self.filesNotParsed += 1
				if not os.path.exists(targetPath):
					os.makedirs(targetPath)

				# IF we find the file and aren't in overwriting mode, skip it.
				if os.path.exists(os.path.join(targetPath, filename)) and not self.allowOverwrite:
					self.filesSkipped += 1

					# If the last copy was cancelled part way through, the final file that was
					# attempted to copy may be corrupted. Because of this and that we know we
					# are using the same order, we want to replace the last file that appears
					# to have been copied
					if resuming:
						lastFileSrc = os.path.join(inpath, filename)
						lastFileTarget = os.path.join(targetPath, filename)
					continue

				# If this seems to be an incomplete copy, replace the possibly corrupted file
				if resuming and len(lastFileSrc) > 1:
					# Continue trying until we've successfully copied the file
					copied = False
					firstTry = True
					print(lastFileSrc, lastFileTarget)
					while not copied:
						try:
							copyfile(lastFileSrc, lastFileTarget)
							# Correct our counters for the previous file
							self.filesCopied += 1
							self.filesSkipped -= 1
							copied = True
						except:
							# Update user on status
							if firstTry:
								self.statusBar().showMessage("Retrying: " + str(self.filesCopied) + " files copied, " +
														 str(self.filesSkipped) + "files skipped. Network error on " +
														 filename)
								print("error message:\n", sys.exc_info()[0])
							firstTry = False
							time.sleep(1)
				# There will only ever be one file that we replace per folder when resuming
				resuming = False

				# Copy the file and update display
				sys.stdout.flush()
				self.statusBar().showMessage("Working: " + str(self.filesCopied) + " files copied, " +
											 str(self.filesSkipped) + " files skipped. Currently copying " + filename)

				# Continue trying until we successfully copy the file
				copied = False
				firstTry = True
				while not copied:
					try:
						copyfile(os.path.join(inpath, filename), os.path.join(targetPath, filename))
						self.filesCopied += 1
						copied = True
					except:
						if firstTry:
							self.statusBar().showMessage("Retrying: " + str(self.filesCopied) + " files copied, " +
													 str(self.filesSkipped) + "files skipped. Error (likely a network failure) on " +
													 filename)
							print("error message:\n", sys.exc_info())
						firstTry = False
						time.sleep(1)


def build_horiz_spacer():
	if py2:
		return QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
	return QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)


def build_vert_spacer():
	if py2:
		return QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
	return QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)


# --------------------------------------------------


# Run the program
if __name__ == '__main__':
	main()
