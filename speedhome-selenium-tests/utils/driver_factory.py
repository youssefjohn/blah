"""
WebDriver factory for creating and managing browser instances
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from config.test_config import TestConfig

class DriverFactory:
    """Factory class for creating WebDriver instances"""
    
    @staticmethod
    def create_driver(browser=None, headless=None):
        """
        Create a WebDriver instance based on browser type
        
        Args:
            browser (str): Browser type ('chrome', 'firefox', 'edge')
            headless (bool): Whether to run in headless mode
            
        Returns:
            WebDriver: Configured WebDriver instance
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
        """Create Chrome WebDriver instance"""
        options = ChromeOptions()
        
        if headless:
            options.add_argument('--headless')
        
        # Common Chrome options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_argument(f'--window-size={TestConfig.WINDOW_SIZE}')
        
        # Performance optimizations
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        # Security settings
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        # Additional options to avoid conflicts
        options.add_argument('--remote-debugging-port=0')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Use system ChromeDriver instead of webdriver-manager
        try:
            # Try to use system ChromeDriver first
            service = ChromeService('/usr/local/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=options)
        except Exception:
            # Fallback to webdriver-manager if system driver fails
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        
        return DriverFactory._configure_driver(driver)
    
    @staticmethod
    def _create_firefox_driver(headless):
        """Create Firefox WebDriver instance"""
        options = FirefoxOptions()
        
        if headless:
            options.add_argument('--headless')
        
        # Firefox specific options
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
        
        # Edge specific options
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
        
        # Maximize window if not headless
        if not TestConfig.HEADLESS:
            driver.maximize_window()
        
        return driver

