import functools

from GrouponScraper.Driver import BaseDriver
from GrouponScraper.main import scan
from GrouponScraper.tKinter.DataManager import ticketNum, DataManager
from GrouponScraper.tKinter.ScrapeManager import ScrapeManager


# TODO! The Tickets loaded in my DataManager are not being added
#         to our KeepChecking list of groupons that are still IN_PROGRESS

# Pulls heavily from ScrapeManager
def compareTicket(a, b):
    if ticketNum(a) == ticketNum(b):
        return True
    return False


class PassiveManager(ScrapeManager):

    def __init__(self, root, dirPath, numPages, queue, threadList):
        super().__init__(root, dirPath, numPages, queue, threadList)
        self.done = False
        self.doneGroupons = []
        self.printedGroupons = []  # Temp Variable

    # First Method Called - Start it all
    def init(self):
        self.gData = DataManager('groupons')
        self.tData = DataManager('tickets')

        gTickets = self.gData.getTickets()
        if len(gTickets) != 0:
            for g in gTickets:
                self.gTickets.append(g)
        self.d = BaseDriver()
        self.scrapePages()

    # Second method called - Overwritten here
    def scrapePages(self):
        self.login()  # Adds Login Call
        self._goToTickets()  # Adds a goToTickets() call
        self.events.append(functools.partial(self.confirmPage, 1))  # Confirm we are on page 1
        self.events.append(functools.partial(self.checkOldOpenTickets))  # Check in progress tickets
        self.events.append(functools.partial(self.mainWatch))  # Opens page one and looks for new tickets

    def mainWatch(self):
        # Goto page 1
        self.confirmPage(1)
        tickets = self.d.getTickets(1)
        toScan = []

        # Check page for new tickets not in our data
        for ticket in tickets:
            add = True
            for t in self.tData.getTickets():
                if ticketNum(t) == ticketNum(ticket):
                    add = False
                    break
            if add:
                toScan.append(ticket)

        # Scan new tickets
        for ticket in toScan:
            self.events.append(functools.partial(self._scanTicket, ticket))

        # ~ TEMP ~
        self.events.append(functools.partial(self.listGroupons))

        # Check in progress tickets
        self.events.append(functools.partial(self.checkOldOpenTickets))

        # Queue up GoToTickets page
        self._goToTickets()  # Adds a goToTickets() call

        # Queue up Main Watch again
        self.events.append(functools.partial(self.mainWatch))
        return

    # TEMP method that just prints to console
    def listGroupons(self):
        for g in self.gData.getTickets():
            new = True
            for t in self.printedGroupons:
                if compareTicket(g, t):
                    new = False
                    break
            if new:
                # print(len(g.devices.devices), end=" - ")
                for d in g.devices.devices:
                    # print(d.status)
                    if d.status == "REPAIRED & COLLECTED":
                        self.printedGroupons.append(g)
                        print("%d)\t" % len(self.printedGroupons), end='')
                        print(g, end='\tGroupons: ')
                        print(g.groupons)
                        print()
        # Append our current scanned list so user can see.
        self.queue.append(len(self.printedGroupons))

    # True = Something done False = Nothing done
    def update(self):
        if len(self.events) != 0:
            # Grab the Latest thing to do and execute it
            e = self.events.pop(0)
            e()
            return True
        # Our queue is empty, so we queue up a quit
        elif not self.done:
            self.d.driver.quit()
            self.done = True
            return True
        # Nothing to do so we complete!
        return False

    def exit(self):
        self.listGroupons()
        self.d.driver.quit()

    # Main method to scan our tickets and store the data if needed
    def _scanTicket(self, ticket):
        self.tData.replaceTicket(ticket)
        ticket = scan(ticket, self.d)
        if ticket is not None:
            self.gData.replaceTicket(ticket)
            self.gTickets = self.gData.getTickets()
        return

    # Checks tickets stored in memory that are marked as IN PROGRESS
    def checkOldOpenTickets(self):
        tickets = self.gData.getTickets()
        for t in tickets:
            try:
                for d in t.devices.devices:
                    if d.status == 'IN PROGRESS':
                        t.link = t.url  # fixes some legacy code
                        # print("GOT ONE BOI")
                        self.events.append(functools.partial(self._OverrideScan, t))
                        break
            except AttributeError:
                pass
