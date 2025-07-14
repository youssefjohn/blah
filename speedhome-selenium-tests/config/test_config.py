"""
Test configuration settings for SpeedHome Selenium tests
"""
import os
from dotenv import load_dotenv

load_dotenv()

class TestConfig:
    # Application URLs
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5173')
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5001/api')
    
    # Browser settings
    BROWSER = os.getenv('BROWSER', 'chrome')  # chrome, firefox, edge
    HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
    WINDOW_SIZE = os.getenv('WINDOW_SIZE', '1920,1080')
    
    # Test timeouts (in seconds)
    DEFAULT_TIMEOUT = int(os.getenv('DEFAULT_TIMEOUT', '10'))
    IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '10'))
    EXPLICIT_WAIT = int(os.getenv('EXPLICIT_WAIT', '20'))
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
    
    # Test data
    TENANT_EMAIL = os.getenv('TENANT_EMAIL', 'tenant@test.com')
    TENANT_PASSWORD = os.getenv('TENANT_PASSWORD', 'password123')
    LANDLORD_EMAIL = os.getenv('LANDLORD_EMAIL', 'landlord@test.com')
    LANDLORD_PASSWORD = os.getenv('LANDLORD_PASSWORD', 'password123')
    
    # Test user data
    TEST_TENANT_DATA = {
        'email': 'test_tenant@example.com',
        'password': 'TestPassword123!',
        'first_name': 'John',
        'last_name': 'Doe',
        'phone': '+60123456789'
    }
    
    TEST_LANDLORD_DATA = {
        'email': 'test_landlord@example.com',
        'password': 'TestPassword123!',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'phone': '+60987654321'
    }
    
    # Test property data
    TEST_PROPERTY_DATA = {
        'title': 'Test Property - Luxury Condo',
        'location': 'Kuala Lumpur',
        'price': '2500',
        'sqft': '1200',
        'bedrooms': '3',
        'bathrooms': '2',
        'parking': '2',
        'property_type': 'Condominium',
        'furnished': 'Fully Furnished',
        'description': 'Beautiful luxury condominium with modern amenities and great city views.',
        'amenities': ['Swimming Pool', 'Gym', 'Security', 'Parking']
    }
    
    # Screenshot settings
    SCREENSHOT_ON_FAILURE = os.getenv('SCREENSHOT_ON_FAILURE', 'true').lower() == 'true'
    SCREENSHOT_DIR = os.getenv('SCREENSHOT_DIR', 'reports/screenshots')
    
    # Reporting
    REPORT_DIR = os.getenv('REPORT_DIR', 'reports')
    ALLURE_RESULTS_DIR = os.getenv('ALLURE_RESULTS_DIR', 'reports/allure-results')
    
    # Database cleanup (if needed)
    CLEANUP_TEST_DATA = os.getenv('CLEANUP_TEST_DATA', 'true').lower() == 'true'
    
    @classmethod
    def get_window_size(cls):
        """Get window size as tuple"""
        width, height = cls.WINDOW_SIZE.split(',')
        return int(width), int(height)

