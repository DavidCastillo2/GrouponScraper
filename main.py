"""
Author: David
Date: 1/27/2021

Open the front desk website for Unifix and gather all the tickets that have Groupons

TODO: When going to a page outside of immediate reach, the program needs to loop. It loads the closest page it can,
    but then it just returns before reaching the desired page. So that allows for global updates before clicking
    the next button it can.
"""


from GrouponScraper.Driver import BaseDriver
from GrouponScraper.ExcelMaker import ExcelMaker


def removeRepeats(array):
    retVal = []
    for a in array:
        if not retVal.__contains__(a):
            retVal.append(a)
    return retVal


def scan(ticket, d):
    # print("TICKET: " + str(ticket), end="\n")
    d.gotoTicket(ticket)

    retVal = d.findGroupon(ticket)
    grouponCodes = removeRepeats(retVal[0])
    if len(grouponCodes) == 0:
        return None

    # We have a ticket that looks like groupon
    grouponTicket = retVal[1]
    grouponTicket.addGroupons(grouponCodes)
    retVal = grouponTicket
    # print(retVal)
    return retVal


def scanTickets(tickets, driver):
    retVal = []
    for ticket in tickets:
        t = scan(ticket, driver)
        if t is not None:
            retVal.append(t)
    return retVal


def mainRun(directory, numPages):
    if directory is None or numPages == '':
        return None

    try:
        numPages = int(numPages)
    except ValueError:
        return None

    die = True  # Close the chrome window if we crash
    pages = numPages
    d = BaseDriver()
    d.init(True)  # Logs us in

    try:
        for p in range(1, pages+1):
            d.goToTickets()  # Go to tickets page
            print("Page: " + str(p))
            tickets = d.getTickets(int(p))
            grouponTickets = scanTickets(tickets, d)

            em = ExcelMaker(grouponTickets, directory)
            em.makeFile("test.xlsx")
            print("EXCEL CREATED\n\n")
    except:
        # We got an error chief, so we crash cleanly
        if die:
            d.driver.close()
        raise
    d.driver.close()


if __name__ == '__main__':
    print("started")
    mainRun('C:/Users/austi/Desktop/FukYE', 1)
    print("DONE")
