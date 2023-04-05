import os

from GrouponScraper.TickerScraper import TicketScraper


class TicketManager:

    def __init__(self, baseDriver):
        self.baseDriver = baseDriver
        self.driver = None
        self.curPage = None
        self.TicketScraper = TicketScraper(self.baseDriver)
        return

    def getTickets(self, pageNum):
        return self.TicketScraper.scrapePage(pageNum)

    def getMaxTickets(self, baseDriver):
        # Init what we need
        self.baseDriver = baseDriver
        self.driver = baseDriver.driver

        # Get max number of pages
        self.baseDriver.waitForLoad()
        fastForward = '/html/body/div[4]/div[2]/div/div[3]/div/div[2]/div[2]/div[2]/div[1]/div/div/ul/li[9]/a'
        self.baseDriver.trueClick(fastForward)
        self.baseDriver.waitForLoad()

        # Find the largest page number
        pagesList = self.driver.find_element_by_id('yw0')
        pages = pagesList.find_elements_by_tag_name('li')
        maxNum = int(pages[6].text)
        return int(maxNum)

    # Deprecated
    def checkIfNewPages(self):
        exists = os.path.exists('PagesFile.txt')
        if not exists:
            file = open('PagesFile.txt', 'w')
        return



