from tkinter import *
from tkinter import filedialog


class FileDir:
    def __init__(self, root, GUIManagerWidgetsList):
        self.path = None  # Global variable to store path from user
        self.readSettings()
        row = Frame(root)

        # File Path Button
        lab = Label(row, width=20, text="Excel Directory", anchor='w')
        userPath = Button(row, text='Browse', command=self.getPath)
        row.pack(side=TOP, fill=X, padx=5, pady=5)
        lab.pack(side=LEFT)

        # User Path Text
        userPath.pack(side=LEFT, expand=NO, fill=X)
        self.userPath = Label(row, width=30, text=str(self.path), anchor='w')
        self.userPath.pack(side=LEFT)

        GUIManagerWidgetsList.extend((row, lab, self.userPath))
        return

    def getPath(self):
        self.path = filedialog.askdirectory()
        if self.path == '':
            self.path = None
            self.userPath.config(text=str(self.path))
            self.writeSettings('')
        else:
            self.writeSettings(str(self.path))
            self.userPath.config(text=str(self.path))
        return

    def readSettings(self):
        try:
            f = open('dir.txt', 'r')
            self.path = f.read().replace('\n', '')
            if self.path == '':
                self.path = None
            f.close()
        except FileNotFoundError:
            f = open('dir.txt', 'w')
            f.close()
        return

    def writeSettings(self, userPath):
        if userPath == '\n':
            f = open('dir.txt', 'w')
            f.write('')
            f.close()
            self.path = None
        f = open('dir.txt', 'w')
        f.write(userPath)
        f.close()
        return
