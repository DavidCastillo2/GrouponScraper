import functools
import datetime as dt

from GrouponScraper.Driver import BaseDriver
from GrouponScraper.ExcelMaker import ExcelMaker
from GrouponScraper.main import scan
from GrouponScraper.tKinter.DataManager import DataManager, ticketNum
from GrouponScraper.tKinter.pageManager import PageManager


class ScrapeManager:
    def __init__(self, root, dirPath, numPages, queue, threadList):
        # MultiThreading Vars
        self.events = []
        self.ticketsToScan = []
        self.gTickets = []
        self.queue = queue
        self.threads = threadList

        # Class Members
        self.root = root
        self.dirPath = dirPath
        self.numPages = numPages
        self.d = None  # Driver object
        self.excelMade = False
        self.gData = None  # Groupon Tickets <DataManager>
        self.tData = None  # Ticket <DataManager>
        self.curMinTicket = None
        self.minTicket = None
        self.MaxTicket = None
        self.startPage = None
        self.endPage = None
        self.pagesToScrape = []
        return

    # Return None if invalid inputs - Starts everything
    def init(self):
        if self.dirPath is None or self.numPages == '':
            return None
        try:
            self.numPages = int(self.numPages)
        except ValueError:
            return None

        # Start it all
        self.gData = DataManager('groupons')
        self.tData = DataManager('tickets')
        gTickets = self.gData.getTickets()
        if len(gTickets) != 0:
            for g in gTickets:
                self.gTickets.append(g)
        self.d = BaseDriver()
        self.scrapePages()

    # First method called
    def scrapePages(self):
        self.login()  # Adds Login Call
        self._goToTickets()  # Adds a goToTickets() call
        self.events.append(functools.partial(self.confirmPage, 1))  # Confirm we are on page 1
        self.events.append(functools.partial(self._findMinTicket))  # Find newest Ticket in System
        self.events.append(functools.partial(self.checkOldOpenTickets))  # Check in progress tickets
        self.events.append(functools.partial(self._listPagesToSearch))  # Adds search calls

    # Populates Min and Max tickets
    def _findMinTicket(self):
        # Current Tickets
        tickets = self.d.getTickets(1)
        self.curMinTicket = tickets[0].ticketNum()

    # Checks tickets stored in memory that are marked as IN PROGRESS
    def checkOldOpenTickets(self):
        tickets = self.tData.getTickets()
        for t in tickets:
            try:
                for d in t.devices.devices:
                    if d.status == 'IN PROGRESS':
                        self.events.append(functools.partial(self._OverrideScan, t))
                        break
            except AttributeError:
                pass

    # Adds a search call for each page
    def _listPagesToSearch(self):
        p = PageManager(self.tData, self.curMinTicket)
        self.pagesToScrape = p.pagesToScrape(1, self.numPages)  # Start page, End page
        # print("Pages to search: " + str(self.pagesToScrape))
        for p in self.pagesToScrape:
            self._goToTickets()  # Append a goToTickets call
            self.events.append(functools.partial(self.confirmPage, p))  # Confirm
            self.events.append(functools.partial(self._scrapePage, p))  # Scrape Page

    # DEPRECIATED
    def _scrapePages(self):
        self.login()  # Login

        # navigate to each ticket page
        for i in range(1, self.numPages+1):
            self._goToTickets()  # Adds a goToTickets() call

            # Confirm we're on the correct page that we want to be scraping
            self.events.append(functools.partial(self.confirmPage, i))

            # Scrape Page
            sp  = functools.partial(self._scrapePage, i)
            self.events.append(sp)

    def getEvents(self):
        return self.events

    # Checks to see if we're on the correct page, if not append a goToPage command
    def confirmPage(self, page):
        try:
            # Tell our queue we are at this page
            self.queue.append(page)

            # We are already at the correct page
            if self.d.getCurPage() == page:
                return True

            # We need to navigate to the correct page
            else:
                # Add another confirmPage call
                self.events.insert(0, functools.partial(self.confirmPage, page))

                # We are not at the correct page, insert this command into the Queue
                goTo = functools.partial(self.d.TicketManager.getTickets, page)
                self.events.insert(0, goTo)
                return False

        # This just means that no tickets have even been looked at yet
        except AttributeError:
            return False

    def nextEvent(self):
        if len(self.events) != 0:
            return self.events.pop()
        return None

    def login(self):
        login = functools.partial(self.d.init, True)  # Logs us in
        self.events.append(login)
        return

    def _goToTickets(self):
        goToTickets = functools.partial(self.d.goToTickets)  # Go to tickets page
        self.events.append(goToTickets)
        return

    def _scrapePage(self, pageNum):
        # Assumes _goToTickets() has already been called
        tickets = self.d.getTickets(pageNum)
        for t in tickets:
            self.events.insert(0, functools.partial(self._scanTicket, t))
        return

    # Main method to scan our tickets and store the data if needed
    def _scanTicket(self, ticket):
        self.tData.replaceTicket(ticket)
        ticket = scan(ticket, self.d)
        if ticket is not None:
            self.gData.replaceTicket(ticket)
            self.gTickets.append(ticket)
        return

    def _OverrideScan(self, ticket):
        self.tData.replaceTicket(ticket)
        t = scan(ticket, self.d)

        # replace ticket in gTickets
        if t is not None:
            self.gData.replaceTicket(t)
            new = True
            for i in range(0, len(self.gTickets)):
                if ticketNum(self.gTickets[i]) == ticketNum(t):
                    self.gTickets[i] = t
                    new = False
                    break
            # Should always be False
            if new:
                self.gTickets.append(t)  # Add if it doesnt exists already

    def makeExcel(self):
        if len(self.gTickets) != 0:
            em = ExcelMaker(self.gData.getTickets(), self.dirPath)
            d = dt.datetime.now()
            fileName = d.strftime('%c').replace(':', '-')
            em.makeFile(fileName + ".xlsx")
        return

    # True = Something done        False = Nothing done
    def update(self):
        if len(self.events) != 0:
            # Grab the Latest thing to do and execute it
            e = self.events.pop(0)
            e()
            return True
        # Make our Excel once we finish our queue
        elif not self.excelMade:
            self.makeExcel()
            print("Excel Created!")
            self.d.driver.quit()
            self.excelMade = True
            return True
        # Nothing to do so we complete!
        return False

    def exit(self):
        self.makeExcel()
        self.d.driver.quit()
