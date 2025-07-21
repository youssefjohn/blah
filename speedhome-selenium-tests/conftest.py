"""
Pytest configuration and fixtures for SpeedHome Selenium tests
"""
import pytest
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from utils.driver_factory import DriverFactory
from config.test_config import TestConfig

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
        default=True,
        help="Run tests in headless mode"
    )
    parser.addoption(
        "--base-url",
        action="store",
        default=TestConfig.BASE_URL,
        help="Base URL for the application"
    )

@pytest.fixture(scope="session")
def browser(request):
    """Get browser name from command line"""
    return request.config.getoption("--browser")

@pytest.fixture(scope="session")
def headless(request):
    """Get headless mode from command line"""
    return request.config.getoption("--headless")

@pytest.fixture(scope="session")
def base_url(request):
    """Get base URL from command line"""
    return request.config.getoption("--base-url")

@pytest.fixture(scope="function")
def driver(browser, headless):
    """Create and return a WebDriver instance"""
    print("Setting up test environment...")
    
    # Create driver using the factory
    driver = DriverFactory.create_driver(browser, headless)
    
    yield driver
    
    print("Cleaning up test environment...")
    driver.quit()

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
    
    # Try to import Application model, but handle if it doesn't exist
    try:
        from src.models.application import Application
        has_application_model = True
    except ImportError:
        print("INFO: Application model not found, skipping application cleanup")
        has_application_model = False
    
    from config.test_config import TestConfig

    # Use the app context to interact with the database
    with app.app_context():
        # Clear existing data to ensure a clean slate
        # We delete in this specific order to respect database relationships.
        print("Clearing old data...")
        if has_application_model:
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

        # Commit users first so we can get their IDs
        db.session.commit()

        # 4. Create test properties
        print("[Fixture] Creating properties...")
        property1 = Property(
            title='Modern Condo in KL City',
            location='Kuala Lumpur',
            price=2500,
            sqft=1200,
            bedrooms=2,
            bathrooms=2,
            parking=1,
            property_type='Condo',
            furnished='Fully Furnished',
            description='A beautiful modern condo in the heart of KL',
            owner_id=landlord.id,
            status='Active'
        )

        property2 = Property(
            title='Cozy Apartment in Petaling Jaya',
            location='Petaling Jaya',
            price=1800,
            sqft=900,
            bedrooms=1,
            bathrooms=1,
            parking=1,
            property_type='Apartment',
            furnished='Partially Furnished',
            description='A cozy apartment perfect for young professionals',
            owner_id=landlord.id,
            status='Active'
        )

        db.session.add(property1)
        db.session.add(property2)
        db.session.commit()

        # 5. Create a confirmed viewing request for testing reschedule functionality
        print("[Fixture] Injecting a confirmed viewing request...")
        from datetime import datetime, timedelta
        
        viewing_date = datetime.now() + timedelta(days=2)
        confirmed_booking = Booking(
            property_id=property1.id,
            user_id=tenant.id,
            appointment_date=viewing_date.date(),
            appointment_time=viewing_date.time(),
            status='confirmed',
            name=f"{tenant.first_name} {tenant.last_name}",
            email=tenant.email,
            phone='123-456-7890',
            message='Test viewing request for reschedule testing'
        )
        
        db.session.add(confirmed_booking)
        db.session.commit()
        
        print("✅ [Fixture] Confirmed viewing request created.")
        print("--- [Fixture] Database seeding complete! ---")

    # This fixture doesn't return anything; it just sets up the database state.
    # The yield allows the tests to run, and any cleanup code would go after the yield.
    yield
    
    # Optional: Clean up after all tests are done
    # with app.app_context():
    #     db.session.query(Booking).delete()
    #     db.session.query(Property).delete()
    #     db.session.query(User).delete()
    #     db.session.commit()

