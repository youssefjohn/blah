"""
Base page class for Page Object Model implementation
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.test_config import TestConfig
import time

class BasePage:
    """Base page class with common page functionality"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, TestConfig.EXPLICIT_WAIT)
    
    def find_element(self, locator):
        """Find element with explicit wait"""
        return self.wait.until(EC.presence_of_element_located(locator))
    
    def find_elements(self, locator):
        """Find multiple elements"""
        return self.driver.find_elements(*locator)
    
    def click_element(self, locator):
        """Click element with wait"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        self.scroll_to_element(element)
        element.click()
        return element
    
    def send_keys_to_element(self, locator, text):
        """Send keys to element with wait"""
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)
        return element
    
    def get_element_text(self, locator):
        """Get text from element"""
        element = self.wait.until(EC.visibility_of_element_located(locator))
        return element.text
    
    def get_element_attribute(self, locator, attribute):
        """Get attribute value from element"""
        element = self.find_element(locator)
        return element.get_attribute(attribute)
    
    def is_element_visible(self, locator, timeout=5):
        """Check if element is visible"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False
    
    def is_element_present(self, locator):
        """Check if element is present in DOM"""
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False
    
    def wait_for_element_to_disappear(self, locator, timeout=10):
        """Wait for element to disappear"""
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.invisibility_of_element_located(locator))
    
    def scroll_to_element(self, element):
        """Scroll to element"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)
    
    def scroll_to_top(self):
        """Scroll to top of page"""
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)
    
    def scroll_to_bottom(self):
        """Scroll to bottom of page"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
    
    def wait_for_page_load(self):
        """Wait for page to load completely"""
        self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
    
    def get_current_url(self):
        """Get current page URL"""
        return self.driver.current_url
    
    def get_page_title(self):
        """Get page title"""
        return self.driver.title
    
    def refresh_page(self):
        """Refresh current page"""
        self.driver.refresh()
        self.wait_for_page_load()
    
    def switch_to_alert(self):
        """Switch to alert and return alert object"""
        return self.wait.until(EC.alert_is_present())
    
    def accept_alert(self):
        """Accept alert"""
        alert = self.switch_to_alert()
        alert.accept()
    
    def dismiss_alert(self):
        """Dismiss alert"""
        alert = self.switch_to_alert()
        alert.dismiss()
    
    def get_alert_text(self):
        """Get alert text"""
        alert = self.switch_to_alert()
        return alert.text
    
    def select_dropdown_by_text(self, locator, text):
        """Select dropdown option by visible text"""
        from selenium.webdriver.support.ui import Select
        element = self.find_element(locator)
        select = Select(element)
        select.select_by_visible_text(text)
    
    def select_dropdown_by_value(self, locator, value):
        """Select dropdown option by value"""
        from selenium.webdriver.support.ui import Select
        element = self.find_element(locator)
        select = Select(element)
        select.select_by_value(value)
    
    def hover_over_element(self, locator):
        """Hover over element"""
        from selenium.webdriver.common.action_chains import ActionChains
        element = self.find_element(locator)
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
    
    def double_click_element(self, locator):
        """Double click element"""
        from selenium.webdriver.common.action_chains import ActionChains
        element = self.find_element(locator)
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
    
    def right_click_element(self, locator):
        """Right click element"""
        from selenium.webdriver.common.action_chains import ActionChains
        element = self.find_element(locator)
        actions = ActionChains(self.driver)
        actions.context_click(element).perform()
    
    def drag_and_drop(self, source_locator, target_locator):
        """Drag and drop element"""
        from selenium.webdriver.common.action_chains import ActionChains
        source = self.find_element(source_locator)
        target = self.find_element(target_locator)
        actions = ActionChains(self.driver)
        actions.drag_and_drop(source, target).perform()
    
    def upload_file(self, locator, file_path):
        """Upload file to input element"""
        element = self.find_element(locator)
        element.send_keys(file_path)
    
    def switch_to_frame(self, locator):
        """Switch to iframe"""
        frame = self.find_element(locator)
        self.driver.switch_to.frame(frame)
    
    def switch_to_default_content(self):
        """Switch back to default content from iframe"""
        self.driver.switch_to.default_content()
    
    def open_new_tab(self, url):
        """Open new tab with URL"""
        self.driver.execute_script(f"window.open('{url}', '_blank');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
    
    def close_current_tab(self):
        """Close current tab"""
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])
    
    def get_window_handles(self):
        """Get all window handles"""
        return self.driver.window_handles
    
    def switch_to_window(self, handle):
        """Switch to specific window"""
        self.driver.switch_to.window(handle)

