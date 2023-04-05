import threading
from tkinter import *

from GrouponScraper.passiveScan.PassiveUI import PassiveUI
from GrouponScraper.tKinter.ScrapeManager import ScrapeManager
from GrouponScraper.tKinter.fileDir import FileDir
import tkinter.messagebox as messagebox


def callback(P):
    if str.isdigit(P) or P == "":
        return True
    else:
        return False


class GuiManager:

    def __init__(self, root):
        # Class vars
        self.fd = None  # File Directory - User Submitted
        self.numEntry = None  # User Submitted
        self.root = root
        self.sm = None
        self.widgets = []

        # Multi threading vars
        self.queue = []
        self.threads = []
        self.thread = None
        self.running = True
        self.lastPage = -1

        # Build UI
        self.build(root)
        self.passiveUI = PassiveUI(root, self.fd, self.numEntry, self.queue, self.threads, self)

    # True = All is good, False = All is fucked don't continue
    def checkUserInfo(self):
        baseWarningMessage = 'Can not begin. The following is required to continue:\n\n\n'
        warning = None
        if self.fd.path == "None":
            warning = "~ Excel Directory  -  Click the Browse Button.\n"
        if self.numEntry.get() == "":
            if warning is None:
                warning = "~ Number of Pages To Scan  -  Input a single number.\n"
            else:
                warning += "~ Number of Pages To Scan  -  Input a single number.\n"

        # User needs to fill out more stuff
        if warning is not None:
            messagebox.showerror("Failed to Start", baseWarningMessage + warning)
            return False
        return True

    def beginScrape(self):
        # If userInfo is false then we don't continue
        if not self.checkUserInfo():
            return

        # If we have no other threads
        if len(self.threads) != 0:
            messagebox.showerror("Already Running", "You already have an instance of a scraper running.")
            return

        # Let our Manager do the job
        self.sm = ScrapeManager(self.root, self.fd.path, self.numEntry.get(), self.queue, self.threads)
        self.sm.init()
        self.running = True

        # Multithreading time
        self.thread = threading.Thread(target=self.update)
        self.thread.start()
        self.threads.append(self.thread)

        # Set text to Scanning
        self.passiveUI.passiveStatus = "Scanning"
        self.passiveUI.passiveLabel.configure(text=self.passiveUI.passiveStatus, fg="red")

    def update(self):
        try:
            # Do a step
            more = self.sm.update()
            self.handleData()

            if more:
                # Thread it
                self.threads.remove(self.thread)
                self.thread = threading.Thread(target=self.update)
                self.root.after(200, self.thread.start)
                self.threads.append(self.thread)
            else:
                # We are done, clean exit
                self.running = False
                self.sm = None
                self.passiveUI.passiveStatus = "Not Scanning"
                self.passiveUI.passiveLabel.configure(text=self.passiveUI.passiveStatus, fg="blue")

        except Exception as e:
            print(e)
            if e == "Sorry! Login Access Denied":
                print("WE MADE IT")
            raise e

    # Just lets us read data from Scrape Manager that it passes into queue
    def handleData(self):
        if len(self.queue) != 0:
            e = self.queue.pop(0)
            if e != self.lastPage:
                print("Handle Data - GUI Manager FROM ScrapeManager:\t", end='')
                print(e)
                self.passiveUI.passiveLabel.configure(text="Scanning Page - %d" % e, fg="red")
                self.lastPage = e

    def build(self, root):
        # User Path For Excel Files
        self.fd = FileDir(root, self.widgets)
        self.root = root

        # Number of pages to check label
        row = Frame(root)
        numPages = Label(row, width=20, text="Number of Pages to Scan:", anchor='w')

        # Number og pages to check BOX
        onlyNums = (self.root.register(callback))
        self.numEntry = Entry(row,  width=20, validate='all', validatecommand=(onlyNums, '%P'), bg="#e8e8e8")
        row.pack(side=TOP, padx=5, pady=5, anchor='nw')
        numPages.pack(side=LEFT)
        self.numEntry.pack(side=RIGHT, expand=YES, fill=X)

        # Submit button and Quit button
        submit = Button(root, text="Begin", command=self.beginScrape)
        submit.pack(side=LEFT, padx=5, pady=5, anchor='ne')
        b2 = Button(root, text='Quit', command=self.quit, fg="red")
        b2.pack(side=LEFT, padx=5, pady=5, anchor='ne')

        self.widgets.extend((numPages, row))

    def quit(self):
        # Just make sure its not scanning
        self.passiveUI.passiveStatus = "Not Scanning"
        self.passiveUI.passiveLabel.configure(text=self.passiveUI.passiveStatus, fg="blue")

        # Clean close Scrape Manager
        if self.sm is not None:
            self.sm.exit()
            self.sm = None

        # Clean close Passive Manager
        if not self.passiveUI.running:
            self.passiveUI.stopScan()
        self.root.quit()

    # Just a method to stop the scanning process
    def stopScan(self):
        if self.sm is not None:
            self.sm.exit()
            self.sm = None
            self.threads = []
            self.thread = None

