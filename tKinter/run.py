from tkinter import *
from GrouponScraper.tKinter.GuiManager import GuiManager

from GrouponScraper.tKinter.Coloring.mainColor import *

# Basic startup
root = Tk()

# Let our Manager do stuff
gm = GuiManager(root)

# Color the stuff?
applyBasic(root, gm)

# LOOP
root.mainloop()

# TODO bug where ScanPages ERRORS when no Excel Dir is specified by user

# Compile Command
# pyinstaller --onefile --noconsole tKinter/run.py

