from selenium.common.exceptions import NoSuchElementException


class PopUp:

    def __init__(self):
        return

    def closePopUp(self, driver):
        return


class Rating(PopUp):
    def __init__(self):
        super().__init__()
        return

    def closePopUp(self, driver):
        try:
            # Grab the Minimize Button
            minimizeButton = driver.find_element_by_class_name('_hj-OO1S1__styles__openStateToggle')
            parent = minimizeButton.find_element_by_xpath('..')

            # Check to see if it is already minimized, click if it is not
            if parent.get_attribute('class').find("minimized") == -1:
                minimizeButton.click()

        except NoSuchElementException:
            pass
        return


