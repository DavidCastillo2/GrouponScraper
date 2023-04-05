class PageManager:
    def __init__(self, tData, curMinTicket):
        # Vars
        self.exploredMin = None
        self.exploredMax = None

        self.tData = tData
        self.curMinTicket = curMinTicket
        self.data = tData.getTickets()
        if len(self.data) != 0:
            self.setData()
        return

    # Called on  __init__()
    def setData(self):
        savedFirst = self.tData.minTicket

        # Find max page explored
        pagesExplored = len(self.data) // 25
        if savedFirst == self.curMinTicket:
            self.exploredMin = 1
            self.exploredMax = pagesExplored
        else:
            numMissing = self.curMinTicket - savedFirst
            print("curMin: %d\tsavedFirst: %d\t\t%d" % (self.curMinTicket, savedFirst, numMissing))
            if numMissing // 25 == 0:  # Missing less than a page
                self.exploredMin = 2  # 1 + 1
                self.exploredMax = pagesExplored
            else:
                pages = numMissing // 25
                self.exploredMin = pages + 1
                self.exploredMax = self.exploredMin + pagesExplored
        print("Min: %d\tMax: %d" % (self.exploredMin, self.exploredMax))

    # Main method that we will call from this class
    def pagesToScrape(self, startPage, endPage):
        retVal = []
        realEnd   = -1
        realStart = -1
        if self.exploredMin is None:
            for i in range(startPage, endPage+1):
                retVal.append(i)
            return retVal

        # We've already explored this far back
        if endPage <= self.exploredMax:
            if startPage >= self.exploredMin:
                return retVal  # we've explored all the requested pages
            else:
                realEnd = self.exploredMin
                realStart = startPage
                for i in range(realStart, realEnd + 1):
                    retVal.append(i)
                return retVal  # Just space on the Left to explore

        # Pages on the right to explore or more
        else:
            realEnd = endPage
            if self.exploredMax <= startPage:
                realStart = startPage
                for i in range(realStart, realEnd + 1):
                    retVal.append(i)
                return retVal  # Far right chunk we have not explored at all
            elif self.exploredMin <= startPage:
                realStart = self.exploredMax
                for i in range(realStart, realEnd + 1):
                    retVal.append(i)
                return retVal  # Far right chunk we have partly explored
            else:
                # Now we have to do the one where we've explored a middle chunk but have
                #   Tails on the left and right that need to be explored
                for i in range(startPage, self.exploredMin + 1):
                    retVal.append(i)
                for i in range(self.exploredMax, endPage + 1):
                    retVal.append(i)
                return retVal  # Tails on left and Right to Explore

