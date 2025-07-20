"""
Comprehensive authentication tests for SpeedHome application
Tests login, registration, and user session management
"""
import pytest
import time
from utils.base_test import BaseTest
from pages.header_page import HeaderPage
from utils.test_data_generator import TestDataGenerator
from config.test_config import TestConfig

class TestAuthentication(BaseTest):
    """Test authentication flows for both tenants and landlords"""
    
    def setup_method(self):
        """Setup for each test"""
        super().setup_method()
        self.header_page = HeaderPage(self.driver)
        self.data_generator = TestDataGenerator()
    
    @pytest.mark.smoke
    def test_login_modal_opens(self):
        """Test that login modal opens when login button is clicked"""
        # Check if login button is visible (user not logged in)
        if self.header_page.is_user_logged_out():
            # Click login button
            self.header_page.click_login_button()
            
            # Verify modal opens
            assert self.header_page.is_login_modal_open(), "Login modal should be open"
            
            # Close modal
            self.header_page.close_login_modal()
            assert not self.header_page.is_login_modal_open(), "Login modal should be closed"
        else:
            pytest.skip("User is already logged in")
    
    @pytest.mark.smoke
    def test_register_modal_opens(self):
        """Test that register modal opens when register button is clicked"""
        # Check if register button is visible (user not logged in)
        if self.header_page.is_user_logged_out():
            # Click register button
            self.header_page.click_register_button()
            
            # Verify modal opens
            assert self.header_page.is_register_modal_open(), "Register modal should be open"
            
            # Close modal
            self.header_page.close_register_modal()
            assert not self.header_page.is_register_modal_open(), "Register modal should be closed"
        else:
            pytest.skip("User is already logged in")
    
    @pytest.mark.regression
    def test_login_form_validation(self):
        """Test login form validation with empty fields"""
        if self.header_page.is_user_logged_out():
            # Open login modal
            self.header_page.click_login_button()
            
            # Try to submit empty form
            self.header_page.submit_login_form()
            
            # Check if form validation prevents submission
            # Modal should still be open if validation failed
            assert self.header_page.is_login_modal_open(), "Modal should remain open for validation errors"
            
            # Close modal
            self.header_page.close_login_modal()
        else:
            pytest.skip("User is already logged in")
    
    @pytest.mark.regression
    def test_register_form_validation(self):
        """Test register form validation with empty fields"""
        if self.header_page.is_user_logged_out():
            # Open register modal
            self.header_page.click_register_button()
            
            # Try to submit empty form
            self.header_page.submit_register_form()
            
            # Check if form validation prevents submission
            assert self.header_page.is_register_modal_open(), "Modal should remain open for validation errors"
            
            # Close modal
            self.header_page.close_register_modal()
        else:
            pytest.skip("User is already logged in")
    
    @pytest.mark.integration
    def test_login_with_valid_credentials(self):
        """Test login with valid tenant credentials"""

        # Use test credentials from config
        email = TestConfig.TENANT_EMAIL
        password = TestConfig.TENANT_PASSWORD

        # Perform login
        success = self.header_page.login(email, password)

        if success:
            # Verify user is logged in
            assert self.header_page.is_user_logged_in(), "User should be logged in"

            # Logout for cleanup
            self.header_page.logout()
            assert self.header_page.is_user_logged_out(), "User should be logged out"
        else:
            # Check for error message
            error_msg = self.header_page.get_error_message()
            if error_msg:
                pytest.fail(f"Login failed with error: {error_msg}")
            else:
                pytest.fail("Login failed without error message")

    @pytest.mark.integration
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""

        email = "invalid@example.com"
        password = "wrongpassword"

        # Attempt login
        success = self.header_page.login(email, password)

        # Should fail
        assert not success, "Login should fail with invalid credentials"

        # Should still be logged out
        assert self.header_page.is_user_logged_out(), "User should remain logged out"

        # Check for error message
        error_msg = self.header_page.get_error_message()
        if error_msg:
            assert "invalid" in error_msg.lower() or "incorrect" in error_msg.lower()
    
    @pytest.mark.integration
    def test_register_new_tenant(self):
        """Test registering a new user"""
        user_data = self.data_generator.generate_user_data()
        user_data['role'] = 'tenant'

        # Attempt registration
        success = self.header_page.register(user_data)

        if success:
            # Check if registration was successful
            # This might redirect or show success message
            time.sleep(2)  # Wait for any redirects

            # Check if user is now logged in or if success message is shown
            if self.header_page.is_user_logged_in():
                # Registration successful and auto-logged in

                self.header_page.logout()
            else:
                # Check for success message
                success_msg = self.header_page.get_success_message()
                assert success_msg is not None, "Should show success message after registration"
        else:
            # Check for error message
            error_msg = self.header_page.get_error_message()
            if error_msg and "already exists" in error_msg.lower():
                pytest.skip("User already exists - this is expected in test environment")
            elif error_msg:
                pytest.fail(f"Registration failed with error: {error_msg}")
            else:
                pytest.fail("Registration failed without error message")
    
    @pytest.mark.integration
    def test_register_new_landlord(self):
        """Test registering a new user"""
        user_data = self.data_generator.generate_user_data()
        user_data['role'] = 'landlord'

        # Attempt registration
        success = self.header_page.register(user_data)

        if success:
            # Check if registration was successful
            # This might redirect or show success message
            time.sleep(2)  # Wait for any redirects

            # Check if user is now logged in or if success message is shown
            if self.header_page.is_user_logged_in():
                # Registration successful and auto-logged in

                self.header_page.logout()
            else:
                # Check for success message
                success_msg = self.header_page.get_success_message()
                assert success_msg is not None, "Should show success message after registration"
        else:
            # Check for error message
            error_msg = self.header_page.get_error_message()
            if error_msg and "already exists" in error_msg.lower():
                pytest.skip("User already exists - this is expected in test environment")
            elif error_msg:
                pytest.fail(f"Registration failed with error: {error_msg}")
            else:
                pytest.fail("Registration failed without error message")
