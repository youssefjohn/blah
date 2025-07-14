"""
Pytest configuration file for SpeedHome Selenium tests (Corrected Version)
"""
import pytest
import os
from datetime import datetime
from utils.driver_factory import DriverFactory
from config.test_config import TestConfig
import pytest_html

# This hook adds command-line options like --browser, --headless, etc.
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
        default=10, # Using a simple default here
        help="Default timeout for element waits"
    )

# These fixtures make the command-line options available to your tests.
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

# This is the most important fixture. It runs for every single test function.
@pytest.fixture(scope="function")
def driver(browser, headless, base_url, timeout):
    """
    WebDriver fixture. Creates a new browser instance for each test function.
    """
    print("Creating new driver instance...")
    driver_instance = DriverFactory.create_driver(browser, headless)
    driver_instance.implicitly_wait(timeout)
    if not headless:
        driver_instance.maximize_window()
    
    driver_instance.get(base_url)
    
    # 'yield' passes the driver to the test function.
    yield driver_instance
    
    # This code runs AFTER the test is finished.
    print("Quitting driver instance...")
    driver_instance.quit()

# These fixtures log in as specific users.
@pytest.fixture(scope="function")
def authenticated_tenant_driver(driver):
    """WebDriver fixture with authenticated tenant session"""
    from pages.header_page import HeaderPage
    header_page = HeaderPage(driver)
    header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
    yield driver
    # The main 'driver' fixture handles logout via driver.quit()

@pytest.fixture(scope="function")
def authenticated_landlord_driver(driver):
    """WebDriver fixture with authenticated landlord session"""
    from pages.header_page import HeaderPage
    header_page = HeaderPage(driver)
    header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
    yield driver
    # The main 'driver' fixture handles logout via driver.quit()

# This hook runs once at the beginning of the entire test session.
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests"""
    print("Setting up test environment...")
    yield
    print("Cleaning up test environment...")

# This provides test data to any test that needs it.
@pytest.fixture(scope="function")
def test_data():
    """Fixture to provide test data"""
    from utils.test_data_generator import TestDataGenerator
    return TestDataGenerator()

# ==================================================================
# THE MAIN FIX: Corrected Screenshot and Reporting Hook
# The old screenshot fixture and makereport hook are replaced by this.
# ==================================================================
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook to capture test results and take screenshot on failure.
    """
    outcome = yield
    report = outcome.get_result()
    
    # Set a report attribute for each phase so we can check it later
    setattr(item, "rep_" + report.when, report)

    # We only want to take a screenshot when the test 'call' itself fails
    if report.when == "call" and report.failed:
        if "driver" in item.fixturenames:
            driver = item.funcargs["driver"]
            
            # Create screenshots directory if it doesn't exist
            screenshot_dir = os.path.join("reports", "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # Generate a unique filename
            test_name = item.name.replace(" ", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"{test_name}_{timestamp}.png"
            screenshot_path = os.path.join(screenshot_dir, screenshot_name)
            
            try:
                driver.save_screenshot(screenshot_path)
                # Add the screenshot to the HTML report
                extra = getattr(report, "extra", [])
                relative_path = os.path.join("screenshots", screenshot_name)
                extra.append(pytest_html.extras.image(relative_path))
                report.extra = extra
            except Exception as e:
                print(f"Failed to take screenshot: {e}")

# These hooks configure pytest and add custom markers.
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "regression: mark test as regression test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "tenant: mark test as tenant-specific test")
    config.addinivalue_line("markers", "landlord: mark test as landlord-specific test")

# These hooks customize the HTML report.
def pytest_html_report_title(report):
    """Customize HTML report title"""
    report.title = "SpeedHome Selenium Test Report"

def pytest_html_results_summary(prefix, summary, postfix):
    """Customize HTML report summary"""
    prefix.extend([f"<h2>Test Environment: {TestConfig.BASE_URL}</h2>"])