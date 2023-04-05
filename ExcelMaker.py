"""
Date-Opened | Date-Closed | Ticket# | Repair Type | Device | Customer name |
Email Address | Tickets Status | Groupon # |
"""
import xlsxwriter


def setWidth(ws, text_format):  # Input: Worksheet object
    ws.set_column(0, 1, 20, cell_format=text_format)
    ws.set_column(2, 2, 15, cell_format=text_format)
    ws.set_column(3, 3, 40, cell_format=text_format)
    ws.set_column(4, 4, 15, cell_format=text_format)
    ws.set_column(5, 5, 20, cell_format=text_format)
    ws.set_column(6, 6, 30, cell_format=text_format)
    ws.set_column(7, 7, 25, cell_format=text_format)
    ws.set_column(8, 8, 15, cell_format=text_format)
    ws.set_column(9, 9, 35, cell_format=text_format)


def headers(cls):
    retVal = []
    for h in cls.__dict__.keys():
        if h[:1] != '_':
            retVal.append({'header': h})
    return retVal


def _validate(ticket):
    groupons = ticket.groupons
    for g in groupons:
        if ticket.user.email.find(str(g)) != -1:
            ticket.removeGroupon(g)
    return True


class ExcelMaker:
    def __init__(self, tickets, directory):
        self.tickets = tickets
        self.directory = directory
        return

    def makeFile(self, fileName):
        workbook = xlsxwriter.Workbook(self.directory + "/" + fileName)
        worksheet = workbook.add_worksheet("Groupons")
        worksheet.set_column('A:J', 12)
        worksheet.write("B1", "WTF")
        text_format = workbook.add_format({'text_wrap': True})

        # Iterate over the data and write it out row by row.
        data = self.getData()

        excelData = []
        for row in data:
            excelData.append(row.getArray())

        heads = headers(data[0])

        tableString = 'A1:J' + str(len(excelData)+1)
        worksheet.add_table(tableString, {'data': excelData,
                                          'columns': heads})
        setWidth(worksheet, text_format)
        workbook.close()

    def getData(self):
        retVal = []
        for t in self.tickets:
            _validate(t)
            for device in t.devices.devices:
                do = t.created
                dc = t.modified
                tn = t.id
                rt = str(device.issues).replace('[', '').replace(']', '')
                d = device.name
                cn = t.user.name
                em = t.user.email
                st = device.status
                tech = t.technician
                gn = str(t.groupons).replace('[', '').replace(']', '')
                if gn == '':
                    gn = "No Groupon Found"
                row = Row(do, dc, tn, rt, d, cn, em, st, tech, gn)
                retVal.append(row)
        return retVal


class Row:
    def __init__(self, do, dc, tn, rt, d, cn, em, st, tech, gn):
        self.dateOpened = do
        self.dateClosed = dc
        self.ticketNumber = tn
        self.repairType = rt
        self.device = d
        self.customerName = cn
        self.email = em
        self.status = st
        self.technician = tech
        self.GrouponNumber = gn

    def getArray(self):
        return [self.dateOpened, self.dateClosed, self.ticketNumber, self.repairType, self.device, self.customerName,
                self.email, self.status, self.technician, self.GrouponNumber]
