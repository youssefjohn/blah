"""
Pytest configuration file for SpeedHome Selenium tests
"""
import pytest
import os
from selenium import webdriver
from utils.driver_factory import DriverFactory
from config.test_config import TestConfig

def pytest_addoption(parser):
    """Add command line options for pytest"""
    parser.addoption(
        "--browser", 
        action="store", 
        default="chrome",
        help="Browser to run tests on: chrome, firefox, edge"
    )
    parser.addoption(
        "--headless", 
        action="store_true", 
        default=False,
        help="Run tests in headless mode"
    )
    parser.addoption(
        "--base-url", 
        action="store", 
        default=TestConfig.BASE_URL,
        help="Base URL for the application"
    )
    parser.addoption(
        "--timeout", 
        action="store", 
        default=TestConfig.DEFAULT_TIMEOUT,
        help="Default timeout for element waits"
    )

@pytest.fixture(scope="session")
def browser(request):
    """Browser fixture for session scope"""
    return request.config.getoption("--browser")

@pytest.fixture(scope="session")
def headless(request):
    """Headless fixture for session scope"""
    return request.config.getoption("--headless")

@pytest.fixture(scope="session")
def base_url(request):
    """Base URL fixture for session scope"""
    return request.config.getoption("--base-url")

@pytest.fixture(scope="session")
def timeout(request):
    """Timeout fixture for session scope"""
    return int(request.config.getoption("--timeout"))

@pytest.fixture(scope="function")
def driver(browser, headless, base_url, timeout):
    """WebDriver fixture for function scope"""
    # Create driver instance
    driver_instance = DriverFactory.create_driver(browser, headless)
    
    # Set implicit wait
    driver_instance.implicitly_wait(timeout)
    
    # Maximize window
    driver_instance.maximize_window()
    
    # Navigate to base URL
    driver_instance.get(base_url)
    
    yield driver_instance
    
    # Cleanup
    driver_instance.quit()

@pytest.fixture(scope="function")
def authenticated_tenant_driver(driver):
    """WebDriver fixture with authenticated tenant session"""
    from pages.header_page import HeaderPage
    
    header_page = HeaderPage(driver)
    header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
    
    yield driver
    
    # Logout after test
    try:
        header_page.logout()
    except:
        pass

@pytest.fixture(scope="function")
def authenticated_landlord_driver(driver):
    """WebDriver fixture with authenticated landlord session"""
    from pages.header_page import HeaderPage
    
    header_page = HeaderPage(driver)
    header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
    
    yield driver
    
    # Logout after test
    try:
        header_page.logout()
    except:
        pass

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests"""
    # Create reports directory
    os.makedirs("reports", exist_ok=True)
    
    # Setup any other test environment requirements
    print("Setting up test environment...")
    
    yield
    
    # Cleanup after all tests
    print("Cleaning up test environment...")

@pytest.fixture(scope="function")
def test_data():
    """Fixture to provide test data"""
    from utils.test_data_generator import TestDataGenerator
    return TestDataGenerator()

# Pytest hooks
def pytest_configure(config):
    """Configure pytest"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as regression test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "tenant: mark test as tenant-specific test"
    )
    config.addinivalue_line(
        "markers", "landlord: mark test as landlord-specific test"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Add markers based on test file names
    for item in items:
        if "tenant" in item.nodeid:
            item.add_marker(pytest.mark.tenant)
        elif "landlord" in item.nodeid:
            item.add_marker(pytest.mark.landlord)
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)

def pytest_html_report_title(report):
    """Customize HTML report title"""
    report.title = "SpeedHome Selenium Test Report"

def pytest_html_results_summary(prefix, summary, postfix):
    """Customize HTML report summary"""
    prefix.extend([
        "<h2>SpeedHome Application Test Results</h2>",
        f"<p>Test Environment: {TestConfig.BASE_URL}</p>"
    ])

@pytest.fixture(scope="function", autouse=True)
def screenshot_on_failure(request, driver):
    """Take screenshot on test failure"""
    yield
    
    if request.node.rep_call.failed:
        # Create screenshots directory
        os.makedirs("reports/screenshots", exist_ok=True)
        
        # Generate screenshot filename
        test_name = request.node.name
        timestamp = pytest.current_timestamp if hasattr(pytest, 'current_timestamp') else "unknown"
        screenshot_name = f"{test_name}_{timestamp}.png"
        screenshot_path = os.path.join("reports/screenshots", screenshot_name)
        
        # Take screenshot
        try:
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            print(f"Failed to take screenshot: {e}")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results for screenshot functionality"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

# Custom pytest markers for test categorization
pytestmark = [
    pytest.mark.selenium,
    pytest.mark.ui
]

