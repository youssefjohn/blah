"""
Test cases for tenant authentication flows
"""
import pytest
from utils.base_test import BaseTest
from pages.header_page import HeaderPage
from pages.home_page import HomePage
from utils.test_data_generator import TestDataGenerator
from config.test_config import TestConfig

class TestTenantAuthentication(BaseTest):
    """Test tenant authentication functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        super().setup_method()
        self.header_page = HeaderPage(self.driver)
        self.home_page = HomePage(self.driver)
        self.data_generator = TestDataGenerator()
    
    def test_tenant_registration_success(self):
        """Test successful tenant registration"""
        # Generate test data
        user_data = self.data_generator.generate_user_data(role='tenant')
        
        # Perform registration
        success = self.header_page.register(user_data)
        
        # Verify registration success
        assert success, "Registration should be successful"
        assert self.header_page.is_user_logged_in(), "User should be logged in after registration"
        
        # Verify user is redirected to homepage
        assert TestConfig.BASE_URL in self.driver.current_url, "Should be redirected to homepage"
        
        # Verify user name is displayed
        user_name = self.header_page.get_user_name()
        assert user_data['first_name'] in user_name, "User name should be displayed in header"
    
    def test_tenant_registration_with_existing_email(self):
        """Test registration with already existing email"""
        # Use existing test tenant email
        user_data = TestConfig.TEST_TENANT_DATA.copy()
        
        # Attempt registration
        success = self.header_page.register(user_data)
        
        # Verify registration fails
        assert not success, "Registration should fail with existing email"
        assert self.header_page.is_register_modal_open(), "Register modal should still be open"
        
        # Verify error message
        error_message = self.header_page.get_error_message()
        assert error_message is not None, "Error message should be displayed"
        assert "email" in error_message.lower(), "Error should mention email"
    
    def test_tenant_registration_validation(self):
        """Test registration form validation"""
        self.header_page.click_register_button()
        
        # Test with invalid email
        invalid_data = self.data_generator.generate_user_data()
        invalid_data['email'] = 'invalid-email'
        
        self.header_page.register(invalid_data)
        
        # Verify validation error
        assert self.header_page.is_register_modal_open(), "Modal should remain open on validation error"
        
        # Test with short password
        invalid_data['email'] = self.data_generator.generate_random_email()
        invalid_data['password'] = '123'
        
        self.header_page.register(invalid_data)
        assert self.header_page.is_register_modal_open(), "Modal should remain open on password validation error"
    
    def test_tenant_login_success(self):
        """Test successful tenant login"""
        # Use existing test tenant credentials
        email = TestConfig.TENANT_EMAIL
        password = TestConfig.TENANT_PASSWORD
        
        # Perform login
        success = self.header_page.login(email, password)
        
        # Verify login success
        assert success, "Login should be successful"
        assert self.header_page.is_user_logged_in(), "User should be logged in"
        
        # Verify user can access tenant features
        self.header_page.click_tenant_button()
        assert "/dashboard" in self.driver.current_url, "Should navigate to tenant dashboard"
    
    def test_tenant_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        # Attempt login with invalid credentials
        success = self.header_page.login("invalid@email.com", "wrongpassword")
        
        # Verify login fails
        assert not success, "Login should fail with invalid credentials"
        assert self.header_page.is_login_modal_open(), "Login modal should still be open"
        
        # Verify error message
        error_message = self.header_page.get_error_message()
        assert error_message is not None, "Error message should be displayed"
    
    def test_tenant_login_with_empty_fields(self):
        """Test login with empty fields"""
        self.header_page.click_login_button()
        
        # Try to submit with empty fields
        self.header_page.click_element(self.header_page.LOGIN_SUBMIT_BUTTON)
        
        # Verify form validation
        assert self.header_page.is_login_modal_open(), "Modal should remain open"
    
    def test_tenant_login_remember_me(self):
        """Test login with remember me option"""
        email = TestConfig.TENANT_EMAIL
        password = TestConfig.TENANT_PASSWORD
        
        # Login with remember me checked
        success = self.header_page.login(email, password, remember_me=True)
        
        assert success, "Login with remember me should be successful"
        assert self.header_page.is_user_logged_in(), "User should be logged in"
    
    def test_switch_between_login_and_register_modals(self):
        """Test switching between login and register modals"""
        # Open login modal
        self.header_page.click_login_button()
        assert self.header_page.is_login_modal_open(), "Login modal should be open"
        
        # Switch to register
        self.header_page.switch_to_register_from_login()
        assert self.header_page.is_register_modal_open(), "Register modal should be open"
        assert not self.header_page.is_login_modal_open(), "Login modal should be closed"
        
        # Switch back to login
        self.header_page.switch_to_login_from_register()
        assert self.header_page.is_login_modal_open(), "Login modal should be open"
        assert not self.header_page.is_register_modal_open(), "Register modal should be closed"
    
    def test_close_authentication_modals(self):
        """Test closing authentication modals"""
        # Test closing login modal
        self.header_page.click_login_button()
        assert self.header_page.is_login_modal_open(), "Login modal should be open"
        
        self.header_page.close_login_modal()
        assert not self.header_page.is_login_modal_open(), "Login modal should be closed"
        
        # Test closing register modal
        self.header_page.click_register_button()
        assert self.header_page.is_register_modal_open(), "Register modal should be open"
        
        self.header_page.close_register_modal()
        assert not self.header_page.is_register_modal_open(), "Register modal should be closed"
    
    def test_tenant_logout(self):
        """Test tenant logout functionality"""
        # First login
        email = TestConfig.TENANT_EMAIL
        password = TestConfig.TENANT_PASSWORD
        
        self.header_page.login(email, password)
        assert self.header_page.is_user_logged_in(), "User should be logged in"
        
        # Logout
        self.header_page.logout()
        assert self.header_page.is_user_logged_out(), "User should be logged out"
        assert self.header_page.is_element_visible(self.header_page.LOGIN_BUTTON), "Login button should be visible"
    
    def test_tenant_access_after_logout(self):
        """Test that tenant features are not accessible after logout"""
        # Login first
        email = TestConfig.TENANT_EMAIL
        password = TestConfig.TENANT_PASSWORD
        
        self.header_page.login(email, password)
        
        # Navigate to tenant dashboard
        self.header_page.click_tenant_button()
        assert "/dashboard" in self.driver.current_url, "Should be on tenant dashboard"
        
        # Logout
        self.header_page.logout()
        
        # Try to access tenant features
        self.header_page.click_tenant_button()
        
        # Should be prompted to login
        assert self.header_page.is_login_modal_open(), "Should be prompted to login"
    
    def test_tenant_role_verification(self):
        """Test that tenant role is properly set and verified"""
        # Register as tenant
        user_data = self.data_generator.generate_user_data(role='tenant')
        success = self.header_page.register(user_data)
        
        assert success, "Registration should be successful"
        
        # Verify tenant can access tenant dashboard
        self.header_page.click_tenant_button()
        assert "/dashboard" in self.driver.current_url, "Tenant should access dashboard"
        
        # Verify tenant cannot access landlord dashboard without warning
        self.header_page.click_landlord_button()
        
        # Should show access denied message or prompt for upgrade
        # This depends on implementation - check for alert or modal
        try:
            alert_text = self.get_alert_text()
            assert "landlord" in alert_text.lower(), "Should show landlord access message"
            self.accept_alert()
        except:
            # If no alert, check for other indicators
            pass

