class Ticket:

    def __init__(self, ticketDiv):
        self.ticketDiv = ticketDiv
        self.link = None
        self.id = None
        self.init()
        return

    def init(self):
        # Populate the fields we want to
        idDiv = self.ticketDiv.find_element_by_class_name('segment-view')
        self.id = idDiv.text
        self.link = idDiv.find_element_by_tag_name('a').get_attribute('href')

    def ticketNum(self):
        return int(self.id.replace('# ', '').replace(' ', '').replace('-', '').replace('T', '').replace('\n', ''))

    def __str__(self):
        retVal = ''
        retVal += self.id + ":\t" + self.link
        return retVal


class GrouponTicket(Ticket):

    def __init__(self, ticketDiv):
        super().__init__(ticketDiv)

