import re


class CommentManager:
    def __init__(self):
        self.min = 6
        self.max = 10
        self.whiteList = set('0123456789')
        return

    # Method currently being used
    def scanComments(self, comments, TicketData):
        numbers = []

        # find all the numbers inside of the comments
        for comment in comments:
            # comment is a raw string
            if comment.__contains__("added a"):
                # Since there is a newLine we find that, the rest of the text is a Technician's test
                numbers.extend(re.findall('[0-9]+', comment[comment.find("\n"):]))

        # Check that none of these numbers are the phone number, email, etc.
        retVal = []
        for number in numbers:
            if not self.tDataContainsNum(number, TicketData):
                if len(number) > 2:
                    retVal.append(number)
        print()
        print(retVal)
        print(TicketData.url)
        return retVal

    # Returns true if the base TicketData already contains this number, aka phone number etc.
    def tDataContainsNum(self, num, tData):
        if tData.id.__contains__(num):
            return True
        if tData.id.__contains__(num):
            return True
        if tData.created.__contains__(num):
            return True
        if tData.modified.__contains__(num):
            return True
        if tData.location.__contains__(num):
            return True
        if tData.creator.__contains__(num):
            return True
        if tData.source.__contains__(num):
            return True
        if tData.subTotal.__contains__(num):
            return True
        if tData.discount.__contains__(num):
            return True
        if tData.tax.__contains__(num):
            return True
        if tData.total.__contains__(num):
            return True
        if tData.totalPaid.__contains__(num):
            return True
        if tData.due.__contains__(num):
            return True
        if tData.url.__contains__(num):
            return True
        if tData.user.email.__contains__(num):
            return True
        if tData.user.number.__contains__(num):
            return True

    # DEPRECATED
    # Takes an array of Strings
    # Returns an array of ints for possible groupons
    def _scanComments(self, comments):
        retVal = []
        count = 0
        curNum = ''
        for c in comments:
            # Iterate over every character
            for char in c:
                if char in self.whiteList:
                    count += 1
                    curNum = curNum + char
                else:
                    try:
                        if self.min <= count <= self.max:
                            # Only add the groupon if there is a space after the number
                            if char == ' ' or ord(char) == 10:
                                retVal.append(int(curNum))
                                count = 0
                                curNum = ''
                        else:
                            count = 0
                            curNum = ''
                    except ValueError:
                        count = 0
                        curNum = ''
        return retVal

'''
TODO
repeat numbers are allowed but should not be
The comment system is not being noted
'''


