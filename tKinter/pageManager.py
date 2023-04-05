import math


class PageManager:
    def __init__(self, tData, curMinTicket):
        # Vars
        self.explored = []
        self.seenPages = {}

        self.tData = tData
        self.curMinTicket = curMinTicket
        self.data = tData.getTickets()
        if len(self.data) != 0:
            self.setData()
        return

    # Called on  __init__()
    def setData(self):
        for t in self.data:
            p = self.getPageNum(t)
            self.addPage(p)
        for key, val in self.seenPages.items():
            if val == 25:
                if not self.explored.__contains__(int(key)):
                    self.explored.append(int(key))
        # print("Explored:\t" + str(self.explored))

    # Main method that we will call from this class
    def pagesToScrape(self, startPage, endPage):
        retVal = []
        for i in range(startPage, endPage+1):
            if not self.explored.__contains__(i):
                retVal.append(i)

        if not retVal.__contains__(1):
            retVal.append(1)
        if not retVal.__contains__(endPage):
            retVal.append(endPage)
        return retVal

    def getPageNum(self, ticket):
        diff = self.curMinTicket - self.tNum(ticket)
        numPage = math.ceil(diff / 25)
        return int(numPage)

    def addPage(self, page):
        try:
            self.seenPages[str(page)] = self.seenPages[str(page)] + 1
        except KeyError:
            self.seenPages[str(page)] = 1

    def tNum(self, ticket):
        return int(ticket.id.replace('# ', '').replace(' ', '').replace('-', '').replace('T', '').replace('\n', ''))
