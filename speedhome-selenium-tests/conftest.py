"""
Pytest configuration file for SpeedHome Selenium tests (Corrected Version)
"""
import sys

import pytest
import os
from datetime import datetime, timedelta
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

@pytest.fixture(scope="session")
def seed_database():
    """
    A session-scoped, autouse fixture that clears and seeds the database
    with test data before any tests are run.
    """
    print("\n--- [Fixture] Starting database seed ---")

    # Add backend project to the Python path to allow imports
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'speedhome-backend'))
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)

    # Import all necessary components from your Flask app
    from src.main import app, db
    from src.models.user import User
    from src.models.property import Property
    from src.models.booking import Booking
    from src.models.application import Application
    from config.test_config import TestConfig

    # Use the app context to interact with the database
    with app.app_context():
        # 1. Clear existing data
        print("[Fixture] Clearing old data...")
        db.session.query(Application).delete()
        db.session.query(Booking).delete()
        db.session.query(Property).delete()
        db.session.query(User).delete()
        db.session.commit()

        # 2. Create the standard test landlord
        print(f"[Fixture] Creating landlord: {TestConfig.LANDLORD_EMAIL}")
        landlord = User(username='testlandlord', email=TestConfig.LANDLORD_EMAIL, first_name='Test',
                        last_name='Landlord', role='landlord', is_verified=True)
        landlord.set_password(TestConfig.LANDLORD_PASSWORD)
        db.session.add(landlord)

        # 3. Create the standard test tenant
        print(f"[Fixture] Creating tenant: {TestConfig.TENANT_EMAIL}")
        tenant = User(username='testtenant', email=TestConfig.TENANT_EMAIL, first_name='Test', last_name='Tenant',
                      role='tenant', is_verified=True)
        tenant.set_password(TestConfig.TENANT_PASSWORD)
        db.session.add(tenant)
        db.session.commit()
        print("[Fixture] Users created successfully.")

        # 4. Create properties for the landlord
        print("[Fixture] Creating properties...")
        property1 = Property(title="Modern Condo in KL City", location="Kuala Lumpur", price=2500, sqft=1100,
                             bedrooms=3, bathrooms=2, parking=2, property_type="Condominium",
                             furnished="Fully Furnished", description="A beautiful condo.", owner_id=landlord.id,
                             status="Active")
        property2 = Property(title="Cozy Apartment in Petaling Jaya", location="Petaling Jaya", price=1800, sqft=850,
                             bedrooms=2, bathrooms=2, parking=1, property_type="Apartment",
                             furnished="Partially Furnished", description="A great place.", owner_id=landlord.id,
                             status="Active")
        db.session.add_all([property1, property2])
        db.session.commit()
        print(f"[Fixture] Created {Property.query.count()} properties.")

        # 5. Inject a pre-confirmed viewing request
        print("[Fixture] Injecting a confirmed viewing request...")
        confirmed_booking = Booking(
            user_id=tenant.id,
            property_id=property1.id,
            name=tenant.get_full_name(),
            email=tenant.email,
            phone="0123456789",
            appointment_date=datetime.now().date() + timedelta(days=7),
            appointment_time=datetime.strptime("11:00", "%H:%M").time(),
            status='confirmed',
            is_seen_by_landlord=True
        )
        db.session.add(confirmed_booking)
        db.session.commit()
        print("✅ [Fixture] Confirmed viewing request created.")

        print("--- [Fixture] Database seeding complete! ---")

    # The setup is now complete. Pytest will now proceed to run the tests.
    yield
    # No cleanup is needed here, as the seeder will clear the DB on the next run.

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