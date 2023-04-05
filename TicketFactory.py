from selenium.common.exceptions import NoSuchElementException

from GrouponScraper.Devices import Devices
from GrouponScraper.CommentManager import CommentManager


class TicketFactory:
    def __init__(self):
        return

    def isGroupon(self, driver):
        # Check if the main body things its a groupon
        table = driver.find_element_by_id('repair_items')
        if table.text.lower().find('groupon') != -1:
            return True
        else:
            # Check the comments to see if the word groupon exists
            comments = driver.find_element_by_id('ticket_all-comments')
            if comments.text.lower().find('groupon') != -1:
                return True

        # No groupon word found
        return False

    def findGroupon(self, driver, ticket):
        t = TicketData(driver, ticket)
        return t.checkCommentsForGroupon(), t


def getPrice(string):
    point = string.find('$')
    if point == -1:
        return None
    else:
        return float(string[point:])


def getComments(div):
    comments = div.find_elements_by_tag_name('li')
    retVal = []
    for c in comments:
        retVal.append(c.text)
    return retVal


class TicketData:
    def __init__(self, driver, ticket):
        # Have groupon option to add from MainDriver
        self.groupons = []

        # Take Data from ticket
        self.id = ticket.id

        # Large body of the div with data
        self.summary = driver.find_element_by_class_name('span4')
        self.priceInfo = driver.find_element_by_class_name('span5')
        self.deviceInfoDiv = driver.find_element_by_id('repair_items')
        self.url = driver.current_url

        # Comments
        commentsDiv = driver.find_element_by_id('ticket_all-comments')
        self.containsGroupon = None
        self.comments = getComments(commentsDiv)

        # Summary info
        self.created = None
        self.modified = None
        self.location = None
        self.creator = None
        self.source = None

        # Price Info
        self.subTotal = None
        self.discount = None
        self.tax = None
        self.total = None
        self.totalPaid = None
        self.due = None

        # Davron request Information
        self.devices = Devices(self.deviceInfoDiv)
        self.technician = self.getTechnician()
        self.technician.replace('\n', '')  # Just cleaning up the string
        userDiv = driver.find_element_by_class_name('span8')
        self.user = User(userDiv)

        # Get all Available Rows of Data
        self.populateSummary()
        self.populatePrice()
        return

    def addGroupons(self, groupons):
        self.groupons = groupons

    def addGroupon(self, groupon):
        self.groupons.append(groupon)

    def removeGroupon(self, groupon):
        self.groupons.remove(groupon)

    def __str__(self):
        retVal = ''
        retVal += self.url + '\tPrice: ' + self.total
        return retVal

    def getTechnician(self):
        for c in self.comments:
            if c.find('Repaired & Collected') != -1:
                # Author of this message = person who marked it as repaired
                name = ""
                for char in c:
                    if char != ' ':
                        name += char
                    else:
                        self.technician = name
                        return name
        return "Ticket_Not_Marked_As_Repaired"

    def populateSummary(self):
        options = self.summary.find_elements_by_tag_name('tr')
        self.created = (options[1]).text[14:]
        self.modified = (options[2]).text[14:]
        self.location = (options[3]).text[9:]
        self.creator = (options[4]).text[9:]
        self.source = (options[5]).text[6:]

    def populatePrice(self):
        options = self.priceInfo.find_elements_by_tag_name('tr')
        self.subTotal = options[0].text
        self.discount = options[1].text
        self.tax = options[2].text
        self.total = options[4].text
        self.totalPaid = options[5].text
        self.due = options[6].text

    def checkCommentsForGroupon(self):
        CommentManager().scanComments(self.comments, self)
        return CommentManager()._scanComments(self.comments)


class User:
    def __init__(self, userDiv):
        self.name = userDiv.find_element_by_tag_name('h5').text
        self.number = ''
        self.email = ''
        self.getNumber(userDiv)
        self.getEmail(userDiv)
        return

    def getNumber(self, userDiv):
        try:
            rawText = userDiv.text
            index = rawText.find('Mobile: ')
            if index == -1:
                return "No_Phone_Number_Found"
            retVal = ''
            i = index+8
            while i < index+20:
                retVal = retVal + str(rawText[i])
                i += 1
            self.number = retVal
        except NoSuchElementException:
            self.number = "No_Phone_Number_Found"

    def getEmail(self, userDiv):
        try:
            rawText = userDiv.text
            index = rawText.find('Email: ')
            if index == -1:
                return "No_Email_Found"
            retVal = ''
            i = index+7
            while '\n' != rawText[i] != ' ':
                retVal += str(rawText[i])
                i += 1
                if i >= len(rawText):
                    return retVal
            self.email = retVal
        except NoSuchElementException:
            self.email = "No_Email_Found"
        if self.email == '':
            self.email = "No_Email_Found"
