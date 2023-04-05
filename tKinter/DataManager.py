"""
This will be a pickle file
Just an array of all the Ticket Objects
"""
import pickle


def ticketNum(ticket):
    return int(ticket.id.replace('# ', '').replace(' ', '').replace('-', '').replace('T', '').replace('\n', ''))


class DataManager:
    def __init__(self, name):
        self.tickets = []
        self.minTicket = None
        self.maxTicket = None
        self.filename = name + '.pkle'
        self.loadData()
        return

    def loadData(self):
        minT = None
        maxT = None
        self.createFile()
        with open(self.filename, "rb") as f:
            while True:
                try:
                    ticket = pickle.load(f)
                    num = ticketNum(ticket)
                    if minT is None:
                        minT = num
                        maxT = num
                    elif minT > num:
                        minT = num
                    elif maxT < num:
                        maxT = num
                    self.tickets.append(ticket)
                except EOFError:
                    break
        if len(self.tickets) < 3:
            self.minTicket = -1
            self.maxTicket = -1
        elif len(self.tickets) == 0:
            self.minTicket = None
            self.maxTicket = None
        else:
            self.minTicket = minT
            self.maxTicket = maxT

    # Creates file if it does not exist
    def createFile(self):
        try:
            f = open(self.filename, 'rb')
            f.close()
        except FileNotFoundError:
            f = open(self.filename, 'w')
            f.close()

    def getTickets(self):
        return self.tickets

    # Checks to see if we already have this object before adding to list
    def addTickets(self, tickets):
        [self.tickets.append(t) for t in tickets]
        with open(self.filename, 'wb') as f:
            for t in tickets:
                removeChrome(t)
                if not self._validate(t):
                    pickle.dump(t, f)

    def addTicket(self, t):
        self.tickets.append(t)
        with open(self.filename, 'ab') as f:
            removeChrome(t)
            pickle.dump(t, f)

    def replaceTicket(self, t):
        for i in range(0, len(self.tickets)):
            if ticketNum(self.tickets[i]) == ticketNum(t):
                self.tickets[i] = t
                return True
        self.addTicket(t)
        return False

    # New ticket = True, alreadyExists = False
    def _validate(self, t):
        for tic in self.tickets:
            if ticketNum(tic) == ticketNum(t):
                return False
        return True


def removeChrome(t):
    t.ticketDiv = None
    t.summary = None
    t.priceInfo = None
    t.deviceInfoDiv = None
    t.comments = None
    try:
        t.devices.devicesDiv = None
        t.devices.mainDiv = None

        for d in t.devices.devices:
            d.mainDiv = None
            d.devicesDiv = None
    except AttributeError:
        pass
    return t
