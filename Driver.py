import time

from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from GrouponScraper.TicketFactory import TicketFactory
from GrouponScraper.TicketManager import TicketManager
from GrouponScraper.stopPopup import Rating


def test():
    d = BaseDriver()
    d.init(True)


class BaseDriver:

    def __init__(self):
        # Startup Init
        self.see = None
        self.driver = None
        self.username = None
        self.password = None
        self.curPage = None

        # Add popup exceptions
        self.popUpsList = None

        # Cogs
        self.TicketManager = None
        self.TicketFactory = None
        return

    def init(self, see):
        # Startup Init
        chromeOptions = Options()
        if not see:
            chromeOptions.add_argument('--headless')
        self.driver = webdriver.Chrome(chrome_options=chromeOptions)
        self.driver.get('https://unifix.repairdesk.co/')
        """ 'no'  'no' """
        self.username = 'no'
        self.password = 'no'
        self.login()
        self.curPage = 'home'

        # Add popup exceptions
        self.popUpsList = [Rating()]

        # Cogs
        self.TicketManager = TicketManager(self)
        self.TicketFactory = TicketFactory()

    # Auto called during Init()
    def login(self):
        # Wait for the Page to load
        loginButton = '/html/body/div[2]/div/div[1]/div[1]/div/div[1]/div/div/form/div[5]/button'
        self.waitLoad(loginButton)

        # Input user login information
        usernamePath = '/html/body/div[2]/div/div[1]/div[1]/div/div[1]/div/div/form/div[3]/input'
        passwordPath = '/html/body/div[2]/div/div[1]/div[1]/div/div[1]/div/div/form/div[4]/input'

        self.driver.find_element_by_xpath(usernamePath).send_keys(self.username)
        self.driver.find_element_by_xpath(passwordPath).send_keys(self.password)
        self.driver.find_element_by_xpath(loginButton).click()

        # Check to make sure we were not rejected by the website
        time.sleep(4)
        try:
            errorText = self.driver.find_element_by_xpath(
                '/html/body/div[2]/div/div[1]/div/div/div[1]/div/div/form/div[2]/ul/li').text
            # Failure Div tells us why we can't log in
            if errorText != '':
                print("Login Failed as " + self.username + "\nReason:\n'" + errorText + "'")
                raise Exception(errorText)

            # Logged in
            print("Logged In Successfully as " + self.username)
            self.curPage = "home"
        except NoSuchElementException:
            # Logged in
            print("Logged In Successfully as " + self.username)
            self.curPage = "home"

    # Callable
    def goToTickets(self):
        ticketURL = 'https://unifix.repairdesk.co/index.php?r=ticket/index'
        self.driver.get(ticketURL)
        self.curPage = 'tickets'

        # We want to click ALL to view all the tickets that exists
        time.sleep(1)
        self.loadListTickets()

    # Callable
    def getMaxTickets(self):
        return self.TicketManager.getMaxTickets(self)

    # Callable - returns Array<Ticket>
    # Input: string for page number
    def getTickets(self, pageNum):
        return self.TicketManager.getTickets(pageNum)

    # Callable - Opens a ticket's URL
    def gotoTicket(self, ticket):
        url = ticket.link
        self.driver.get(url)
        self.curPage = 'ticket: ' + ticket.id

    # Callable
    def isGroupon(self):
        return self.TicketFactory.isGroupon(self.driver)

    # Callable
    def findGroupon(self, ticket):
        return self.TicketFactory.findGroupon(self.driver, ticket)

    # Callable
    def getCurPage(self):
        return self.TicketManager.TicketScraper.getCurPage()

    # Clicks the ALL button so we get the real list of tickets to check
    def loadListTickets(self, numPages='ALL'):
        self.waitForLoad()
        AllButton = '/html/body/div[4]/div[2]/div/div[3]/div/div[2]/div[1]/div/a[6]'
        self.trueClick(AllButton)
        self.waitForLoad()
        return

    # Insert anoyying pop up here from PopUps class - used by waitForLoad()
    def closePopups(self):
        for pop in self.popUpsList:
            pop.closePopUp(self.driver)

    # Called by waitForLoad()  - OUTDATED
    def __closePopups(self):
        # Dictionary {XMLofPath : ClickBoolean}
        itemsToCheck = {'/html/body/div[73]/div/div/button': True}  # Rating Pop Up
        for item, clickBool in itemsToCheck.items():
            try:
                div = self.driver.find_element_by_xpath(item)
                if clickBool:
                    div.click()
            except NoSuchElementException:
                continue

    # Call for things that need to be clicked
    # If not passed a string for XMLPath it assumes its a selenium driver object
    def trueClick(self, xmlPath):
        if isinstance(xmlPath, str):
            element = self.driver.find_element_by_xpath(xmlPath)
        else:
            element = xmlPath
        cords = element.location_once_scrolled_into_view
        self.scrollToCords(cords, element)

    # Called by TrueClick()
    def scrollToCords(self, cords, element):
        clicked = False
        while not clicked:
            try:
                element.click()
                clicked = True
            except ElementClickInterceptedException:
                # Scroll down to try and get the button in view
                self.driver.find_element_by_xpath("/html/body").send_keys(Keys.ARROW_DOWN)
                time.sleep(0.01)

    # Call to wait and see if we have the loading circles
    def waitForLoad(self):
        isLoaded = 'body-content-loading-overlay'
        curClassName = ''
        while curClassName != isLoaded:
            loadingDiv = self.driver.find_element_by_id('loader')
            curClassName = loadingDiv.get_attribute("class")
        self.closePopups()

    # Outdated method, requires div to check if a page has loaded
    def waitLoad(self, pathToDiv, textOfDiv=None):
        stopBool = False
        while not stopBool:
            try:
                div = self.driver.find_element_by_xpath(pathToDiv)
                if textOfDiv == div.text or textOfDiv is None:
                    stopBool = True
            except NoSuchElementException:
                continue
        return


