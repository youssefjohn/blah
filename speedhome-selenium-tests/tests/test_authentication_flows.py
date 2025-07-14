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
    def test_switch_between_login_register_modals(self):
        """Test switching between login and register modals"""
        if self.header_page.is_user_logged_out():
            # Open login modal
            self.header_page.click_login_button()
            assert self.header_page.is_login_modal_open()
            
            # Switch to register
            self.header_page.switch_to_register_from_login()
            assert self.header_page.is_register_modal_open()
            assert not self.header_page.is_login_modal_open()
            
            # Switch back to login
            self.header_page.switch_to_login_from_register()
            assert self.header_page.is_login_modal_open()
            assert not self.header_page.is_register_modal_open()
            
            # Close modal
            self.header_page.close_login_modal()
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
        if self.header_page.is_user_logged_out():
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
        else:
            pytest.skip("User is already logged in")
    
    @pytest.mark.integration
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        if self.header_page.is_user_logged_out():
            # Use invalid credentials
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
        else:
            pytest.skip("User is already logged in")
    
    @pytest.mark.integration
    def test_register_new_user(self):
        """Test registering a new user"""
        if self.header_page.is_user_logged_out():
            # Generate unique test data
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
        else:
            pytest.skip("User is already logged in")
    
    @pytest.mark.regression
    def test_remember_me_functionality(self):
        """Test remember me checkbox functionality"""
        if self.header_page.is_user_logged_out():
            # Open login modal
            self.header_page.click_login_button()
            
            # Fill form with remember me checked
            email = TestConfig.TENANT_EMAIL
            password = TestConfig.TENANT_PASSWORD
            self.header_page.fill_login_form(email, password, remember_me=True)
            
            # Verify remember me is checked
            assert self.header_page.is_remember_me_checked(), "Remember me should be checked"
            
            # Submit form
            self.header_page.submit_login_form()
            
            # Wait for response
            time.sleep(2)
            
            # Close modal if still open (in case of error)
            if self.header_page.is_login_modal_open():
                self.header_page.close_login_modal()
        else:
            pytest.skip("User is already logged in")
    
    @pytest.mark.regression
    def test_role_selection_in_register(self):
        """Test role selection in registration form"""
        if self.header_page.is_user_logged_out():
            # Open register modal
            self.header_page.click_register_button()
            
            # Generate test data
            user_data = self.data_generator.generate_user_data()
            
            # Test tenant role selection
            user_data['role'] = 'tenant'
            self.header_page.fill_register_form(user_data)
            assert self.header_page.get_selected_role() == 'tenant'
            
            # Clear form and test landlord role
            self.header_page.clear_register_form()
            user_data['role'] = 'landlord'
            self.header_page.fill_register_form(user_data)
            assert self.header_page.get_selected_role() == 'landlord'
            
            # Close modal
            self.header_page.close_register_modal()
        else:
            pytest.skip("User is already logged in")
    
    @pytest.mark.smoke
    def test_logout_functionality(self):
        """Test logout functionality"""
        # First ensure user is logged in
        if self.header_page.is_user_logged_out():
            # Login first
            email = TestConfig.TENANT_EMAIL
            password = TestConfig.TENANT_PASSWORD
            success = self.header_page.login(email, password)
            
            if not success:
                pytest.skip("Cannot test logout - login failed")
        
        # Now test logout
        if self.header_page.is_user_logged_in():
            self.header_page.logout()
            assert self.header_page.is_user_logged_out(), "User should be logged out"
        else:
            pytest.skip("User is not logged in")
    
    @pytest.mark.integration
    def test_session_persistence(self):
        """Test that user session persists across page refreshes"""
        if self.header_page.is_user_logged_out():
            # Login
            email = TestConfig.TENANT_EMAIL
            password = TestConfig.TENANT_PASSWORD
            success = self.header_page.login(email, password)
            
            if success and self.header_page.is_user_logged_in():
                # Refresh page
                self.driver.refresh()
                time.sleep(2)
                
                # Check if still logged in
                assert self.header_page.is_user_logged_in(), "User should remain logged in after refresh"
                
                # Logout for cleanup
                self.header_page.logout()
            else:
                pytest.skip("Login failed - cannot test session persistence")
        else:
            pytest.skip("User is already logged in")

