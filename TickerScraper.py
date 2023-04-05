from GrouponScraper.Ticket import Ticket


class TicketScraper:
    def __init__(self, baseDriver):
        self.bigDivID = 'ticket-grid'
        self.baseDriver = baseDriver
        self.driver = baseDriver.driver
        self.PageManager = PageManager(baseDriver)
        return

    def gotoPage(self, num):
        self.PageManager.loadPageNum(num)

    def scrapePage(self, num):
        # This if statement is a bad idea
        if self.baseDriver.getCurPage() != num:
            self.gotoPage(num)
        bigDiv = self.driver.find_element_by_id(self.bigDivID)
        table = bigDiv.find_element_by_tag_name('tbody')
        rows = table.find_elements_by_tag_name('tr')
        tickets = []
        for r in rows:
            tickets.append(Ticket(r))
        return tickets

    def getCurPage(self):
        return self.PageManager.curPage


def checkIfValid(div):
    if div.get_attribute('class') == 'disabled':
        return False
    return True


class PageManager:
    def __init__(self, baseDriver):
        self.curPage = None
        self.pageListID = 'yw0'
        self.baseDriver = baseDriver
        self.driver = baseDriver.driver

    def getCurPage(self):
        pagesDivs = self.driver.find_element_by_id(self.pageListID)
        curPageDiv = pagesDivs.find_element_by_class_name('active')
        self.curPage = int(curPageDiv.text)
        return self.curPage

    # Tries to load a page number, returns false if it cannot
    def loadPageNum(self, num):
        if num == self.getCurPage():
            return
        while True:
            # Behind the real page
            if self.curPage < num:
                nextButton = self.getNextButton(num)
                if nextButton is None:
                    return False

                # Click the next Button
                self.baseDriver.trueClick(nextButton)
                self.baseDriver.waitForLoad()
                self.getCurPage()
                return True
            # Ahead of the real page
            elif self.curPage > num:
                nextButton = self.getPrevButton(num)
                if nextButton is None:
                    return False

                # Click the next Button
                self.baseDriver.trueClick(nextButton)
                self.baseDriver.waitForLoad()
                self.getCurPage()
                return True
            # At the correct Page
            else:
                self.baseDriver.waitForLoad()
                return True

    # Returns next button if clickable, returns None if it's not
    # Also Tries to get as close to the goal number as possible
    def getNextButton(self, num=None):
        pagesDivs = self.driver.find_element_by_id(self.pageListID)
        allDivs = pagesDivs.find_elements_by_tag_name('li')
        if num is None:
            return allDivs[8]  # This is the next page button
        else:
            # Check the numbered buttons for our number
            numDivs = allDivs[2:7]
            for div in numDivs:
                # We found our number, click it if possible
                if int(div.text) == num:
                    if checkIfValid(div):
                        return div.find_element_by_tag_name('a')
                    else:
                        return None
            # None of the divs had the number we wanted, click the last option if possible
            if checkIfValid(numDivs[4]):
                return numDivs[4].find_element_by_tag_name('a')
        # No available buttons to push
        return None

    # Returns previous button if clickable, returns None if it's not
    # Does same logic as above
    def getPrevButton(self, num=None):
        pagesDivs = self.driver.find_element_by_id(self.pageListID)
        allDivs = pagesDivs.find_elements_by_tag_name('li')
        if num is None:
            return allDivs[2]  # This is the Previous page button
        else:
            numDivs = allDivs[2:6]
            for div in numDivs:
                if int(div.text) == num:
                    if checkIfValid(div):
                        return div.find_element_by_tag_name('a')
                    else:
                        return None
                if checkIfValid(numDivs[0]):
                    return numDivs[0].find_element_by_tag_name('a')
                else:
                    return None

