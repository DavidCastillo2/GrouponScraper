import threading
from tkinter import *
from tkinter import messagebox

from GrouponScraper.passiveScan.passiveManager import PassiveManager


class PassiveUI:
    def __init__(self, root, fd, numEntry, q, threadList, guiManager):
        # Root's queue for async functionality
        self.guiMan = guiManager  # Allows us to stop this class when STOP button pushed
        self.queue = q  # Allows us to pass data to Main Tkinter window
        self.threads = threadList
        self.thread = None
        self.running = True  # Allows us to stop from Main Tkinter window

        # Member vars
        self.passiveLabel = None
        self.passiveStatus = "Not Scanning"
        self.gTickets = []  # Probably not going to be needed
        self.root = root
        self.pm = None
        self.fd = fd
        self.numEntry = numEntry
        self.lastSize = None

        # UI setup
        #  bg="#c7c7ad", fg='#c7c7ad'
        endPassive = Button(root, text="Stop", command=self.stopScan)
        endPassive.pack(side=RIGHT, padx=5, pady=5, anchor='ne')  # Stop button
        passive = Button(root, text="Passive Scan", command=self.scan)
        passive.pack(side=RIGHT, padx=5, pady=5, anchor='ne')  # Passive Scan Start button
        self.passiveLabel = Label(root, text=self.passiveStatus, fg="blue")
        self.passiveLabel.pack(side=RIGHT, padx=5, pady=5, anchor='ne')  # Label we use to show USER stuff

        # Add widgets to GUI manager list
        self.guiMan.widgets.append(self.passiveLabel)

    def scan(self):
        # Get user Save_Path
        if not self.checkUserInfo():
            return

        # If we have no other threads
        if len(self.threads) != 0:
            messagebox.showerror("Already Running", "You already have an instance of a scraper running.")
            return

        # Get user's information
        dirPath = self.fd.path
        numPages = self.numEntry.get()

        # Change Status to Scanning
        self.running = True
        self.passiveStatus = "Scanning"
        self.passiveLabel.configure(text=self.passiveStatus, fg="red")

        # Set it all up
        self.pm = PassiveManager(self.root, dirPath, numPages, self.queue, self.threads)
        self.pm.init()

        # Multithreading time
        self.thread = threading.Thread(target=self.update)
        self.thread.start()
        self.threads.append(self.thread)
        return

    # Tics everytime we run a loop
    def update(self):
        if self.running:
            self.pm.update()
            self.handleData()
            # self.root.after(200, self.update)

            # Thread it
            self.threads.remove(self.thread)
            self.thread = threading.Thread(target=self.update)
            self.root.after(200, self.thread.start)
            self.threads.append(self.thread)
            # self.thread.start()
        else:
            self.handleData()
            self.stopScan()

    # This is here in case we want to update the Screen when we find a new redeemed groupon
    def handleData(self):
        for i in range(len(self.queue)):
            item = self.queue[i]
            if item != self.lastSize:
                self.passiveStatus = "Scanning - %d found" % item
                self.passiveLabel.configure(text=self.passiveStatus, fg="red")
                self.lastSize = item
        # print("Length: " + str(len(self.queue)) + " -> Values: " + str(self.queue))
        [self.queue.remove(i) for i in self.queue]
        # print("Length: " + str(len(self.queue)) + " -> Values: " + str(self.queue), end='\n\n')

    def stopScan(self):
        self.running = False
        self.passiveStatus = "Not Scanning"
        self.passiveLabel.configure(text=self.passiveStatus, fg="blue")

        # Just empty our threads so we can run again
        self.thread = None
        [self.threads.pop() for i in range(len(self.threads))]

        if self.pm is not None:
            self.pm.exit()
            self.gTickets = self.pm.gTickets
            self.pm = None
            self.threads.remove(self.thread)
            self.thread = None

        self.guiMan.stopScan()
        return

    # Method copied over from GuiManager
    def checkUserInfo(self):
        baseWarningMessage = 'Can not begin. The following is required to continue:\n\n\n'
        warning = None
        if self.fd.path is None:
            warning = "~ Excel Directory  -  Click the Browse Button.\n"

        # User needs to fill out more stuff
        if warning is not None:
            messagebox.showerror("Failed to Start", baseWarningMessage + warning)
            return False
        return True
