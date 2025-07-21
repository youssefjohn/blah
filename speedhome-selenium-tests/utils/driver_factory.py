"""
WebDriver factory for creating and managing browser instances
(Updated to use Selenium's built-in Selenium Manager)
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

# We no longer need webdriver-manager for Chrome, but we'll keep it for Firefox/Edge
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from config.test_config import TestConfig

class DriverFactory:
    """Factory class for creating WebDriver instances"""

    @staticmethod
    def create_driver(browser=None, headless=None):
        """
        Create a WebDriver instance based on browser type
        """
        browser = browser or TestConfig.BROWSER
        headless = headless if headless is not None else TestConfig.HEADLESS

        if browser.lower() == 'chrome':
            return DriverFactory._create_chrome_driver(headless)
        elif browser.lower() == 'firefox':
            return DriverFactory._create_firefox_driver(headless)
        elif browser.lower() == 'edge':
            return DriverFactory._create_edge_driver(headless)
        else:
            raise ValueError(f"Unsupported browser: {browser}")

    @staticmethod
    def _create_chrome_driver(headless):
        """Create a clean and robust Chrome WebDriver instance using Selenium Manager."""
        options = ChromeOptions()

        if headless:
            options.add_argument("--headless")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={TestConfig.WINDOW_SIZE}")
        
        # Additional options to prevent conflicts
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("--remote-debugging-port=0")  # Use random port
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")

        # By NOT passing a service object, Selenium will automatically use its
        # own Selenium Manager to download and manage the correct chromedriver.
        # This is the most modern and reliable method and avoids webdriver-manager bugs.
        driver = webdriver.Chrome(options=options)

        return DriverFactory._configure_driver(driver)

    @staticmethod
    def _create_firefox_driver(headless):
        """Create Firefox WebDriver instance"""
        options = FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument(f'--width={TestConfig.get_window_size()[0]}')
        options.add_argument(f'--height={TestConfig.get_window_size()[1]}')
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        return DriverFactory._configure_driver(driver)

    @staticmethod
    def _create_edge_driver(headless):
        """Create Edge WebDriver instance"""
        options = EdgeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--window-size={TestConfig.WINDOW_SIZE}')
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        return DriverFactory._configure_driver(driver)

    @staticmethod
    def _configure_driver(driver):
        """Configure common driver settings"""
        driver.implicitly_wait(TestConfig.IMPLICIT_WAIT)
        driver.set_page_load_timeout(TestConfig.PAGE_LOAD_TIMEOUT)

        if not TestConfig.HEADLESS:
            driver.maximize_window()

        return driver
