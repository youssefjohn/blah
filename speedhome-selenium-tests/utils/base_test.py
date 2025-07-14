"""
Base test class with common setup, teardown, and utility methods
"""
import pytest
import os
import time
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.driver_factory import DriverFactory
from config.test_config import TestConfig

class BaseTest:
    """Base test class with common functionality"""
    
    driver = None
    wait = None
    
    def setup_method(self):
        """Setup method run before each test"""
        print("Setting up test environment...")
        self.driver = DriverFactory.create_driver()
        self.wait = WebDriverWait(self.driver, TestConfig.EXPLICIT_WAIT)
        self.driver.get(TestConfig.BASE_URL)
    
    def teardown_method(self):
        """Teardown method run after each test"""
        print("Cleaning up test environment...")
        if self.driver:
            self.driver.quit()
    
    def take_screenshot(self, name=None):
        """Take a screenshot and save it"""
        if not TestConfig.SCREENSHOT_ON_FAILURE:
            return
        
        # Create screenshot directory if it doesn't exist
        os.makedirs(TestConfig.SCREENSHOT_DIR, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if name:
            filename = f"{name}_{timestamp}.png"
        else:
            filename = f"screenshot_{timestamp}.png"
        
        filepath = os.path.join(TestConfig.SCREENSHOT_DIR, filename)
        self.driver.save_screenshot(filepath)
        return filepath
    
    def wait_for_element(self, locator, timeout=None):
        """Wait for element to be present and visible"""
        timeout = timeout or TestConfig.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located(locator))
    
    def wait_for_element_clickable(self, locator, timeout=None):
        """Wait for element to be clickable"""
        timeout = timeout or TestConfig.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.element_to_be_clickable(locator))
    
    def wait_for_text_in_element(self, locator, text, timeout=None):
        """Wait for specific text to appear in element"""
        timeout = timeout or TestConfig.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.text_to_be_present_in_element(locator, text))
    
    def wait_for_url_contains(self, url_part, timeout=None):
        """Wait for URL to contain specific text"""
        timeout = timeout or TestConfig.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.url_contains(url_part))
    
    def scroll_to_element(self, element):
        """Scroll to make element visible"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # Small delay for smooth scrolling
    
    def scroll_to_top(self):
        """Scroll to top of page"""
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)
    
    def scroll_to_bottom(self):
        """Scroll to bottom of page"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
    
    def is_element_present(self, locator):
        """Check if element is present on page"""
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False
    
    def is_element_visible(self, locator):
        """Check if element is visible on page"""
        try:
            element = self.driver.find_element(*locator)
            return element.is_displayed()
        except NoSuchElementException:
            return False
    
    def wait_for_page_load(self, timeout=None):
        """Wait for page to fully load"""
        timeout = timeout or TestConfig.PAGE_LOAD_TIMEOUT
        wait = WebDriverWait(self.driver, timeout)
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
    
    def clear_and_send_keys(self, element, text):
        """Clear element and send keys"""
        element.clear()
        element.send_keys(text)
    
    def safe_click(self, locator, timeout=None):
        """Safely click element with wait"""
        element = self.wait_for_element_clickable(locator, timeout)
        self.scroll_to_element(element)
        element.click()
        return element
    
    def get_current_url(self):
        """Get current page URL"""
        return self.driver.current_url
    
    def get_page_title(self):
        """Get current page title"""
        return self.driver.title
    
    def refresh_page(self):
        """Refresh current page"""
        self.driver.refresh()
        self.wait_for_page_load()
    
    def navigate_back(self):
        """Navigate back in browser history"""
        self.driver.back()
        self.wait_for_page_load()
    
    def switch_to_new_tab(self):
        """Switch to newly opened tab"""
        self.driver.switch_to.window(self.driver.window_handles[-1])
    
    def close_current_tab(self):
        """Close current tab and switch to previous"""
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])
    
    def accept_alert(self):
        """Accept browser alert"""
        alert = self.driver.switch_to.alert
        alert.accept()
    
    def dismiss_alert(self):
        """Dismiss browser alert"""
        alert = self.driver.switch_to.alert
        alert.dismiss()
    
    def get_alert_text(self):
        """Get text from browser alert"""
        alert = self.driver.switch_to.alert
        return alert.text

