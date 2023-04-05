class Devices:
    def __init__(self, driver):

        # Attributes
        self.name = None
        self.issues = []
        self.status = None
        self.devices = []

        # We are passed the ID = repair_items  div
        # Gather the correct Divs
        self.mainDiv = driver.find_element_by_tag_name('tbody')
        self.devicesDiv = self.mainDiv.find_elements_by_tag_name('tr')

        # Gather Data on each device
        for d in self.devicesDiv:

            # Get the table of data and split into rows
            dataDivs = d.find_elements_by_tag_name('td')

            # Populate Data
            device = Device()
            self.populateServiceInfo(dataDivs[0], device)
            self.populateStatus(dataDivs[2], device)

            # Add device
            self.devices.append(device)
        return

    def populateServiceInfo(self, div, device):
        strongText = div.find_elements_by_tag_name("strong")
        device.name = strongText[0].text
        device.issues = strongText[2].text.split(',')

    def populateStatus(self, div, device):
        device.status = div.find_element_by_id('allowStatusChange').text


class Device:
    def __init__(self):
        self.name = ''
        self.issues = []
        self.status = None
        return

    def __repr__(self):
        retVal = self.name
        retVal += " - " + self.status
        retVal += "\nIssues: "
        for i in self.issues:
            retVal += i
        retVal += '\n'
        return retVal
