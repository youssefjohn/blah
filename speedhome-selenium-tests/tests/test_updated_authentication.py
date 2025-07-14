"""
Updated authentication tests using the corrected HeaderPage selectors
"""
import pytest
from utils.base_test import BaseTest
from pages.header_page_updated import HeaderPage
from utils.test_data_generator import TestDataGenerator
import time

class TestUpdatedAuthentication(BaseTest):
    """Updated authentication tests with correct selectors"""
    
    def setup_method(self):
        """Setup for each test"""
        super().setup_method()
        self.header_page = HeaderPage(self.driver)
        self.data_generator = TestDataGenerator()
    
    @pytest.mark.smoke
    def test_user_icon_interaction(self):
        """Test clicking the user icon to access auth options"""
        print("🔍 Testing user icon interaction...")
        
        # Click user icon
        success = self.header_page.click_user_icon()
        print(f"👤 User icon click result: {success}")
        
        # Wait a moment for any dropdown/modal to appear
        time.sleep(2)
        
        # Take screenshot for debugging
        self.header_page.take_screenshot("user_icon_clicked")
        
        print("✅ User icon interaction test completed")
    
    @pytest.mark.smoke
    def test_find_auth_elements(self):
        """Test finding authentication elements"""
        print("🔍 Looking for authentication elements...")
        
        # First click user icon
        self.header_page.click_user_icon()
        time.sleep(2)
        
        # Look for login elements
        login_found = self.header_page.is_element_present(self.header_page.LOGIN_LINK)
        print(f"🔑 Login link found: {login_found}")
        
        # Look for register elements  
        register_found = self.header_page.is_element_present(self.header_page.REGISTER_LINK)
        print(f"📝 Register link found: {register_found}")
        
        # Take screenshot
        self.header_page.take_screenshot("auth_elements_search")
        
        print("✅ Authentication elements search completed")
    
    def test_registration_attempt(self):
        """Attempt registration with updated selectors"""
        print("🔍 Testing registration process...")
        
        # Generate test data
        user_data = self.data_generator.generate_user_data(role='tenant')
        print(f"👤 Generated test user: {user_data['email']}")
        
        try:
            # Attempt registration
            success = self.header_page.register(user_data)
            print(f"📝 Registration attempt result: {success}")
            
            # Take screenshot regardless of result
            self.header_page.take_screenshot("registration_attempt")
            
        except Exception as e:
            print(f"⚠️ Registration attempt error: {e}")
            self.header_page.take_screenshot("registration_error")
        
        print("✅ Registration test completed")
    
    def test_login_attempt(self):
        """Attempt login with updated selectors"""
        print("🔍 Testing login process...")
        
        try:
            # Attempt login with test credentials
            success = self.header_page.login("test@example.com", "password123")
            print(f"🔑 Login attempt result: {success}")
            
            # Take screenshot
            self.header_page.take_screenshot("login_attempt")
            
        except Exception as e:
            print(f"⚠️ Login attempt error: {e}")
            self.header_page.take_screenshot("login_error")
        
        print("✅ Login test completed")
    
    def test_modal_detection(self):
        """Test detection of modals/dropdowns"""
        print("🔍 Testing modal/dropdown detection...")
        
        # Click user icon
        self.header_page.click_user_icon()
        time.sleep(2)
        
        # Check for modals
        login_modal_open = self.header_page.is_login_modal_open()
        register_modal_open = self.header_page.is_register_modal_open()
        
        print(f"🎭 Login modal detected: {login_modal_open}")
        print(f"🎭 Register modal detected: {register_modal_open}")
        
        # Look for any modal-like elements
        modals = self.driver.find_elements("css selector", ".modal, [role='dialog'], [class*='modal'], [class*='dropdown']")
        print(f"🎭 Found {len(modals)} modal-like elements")
        
        # Take screenshot
        self.header_page.take_screenshot("modal_detection")
        
        print("✅ Modal detection test completed")

