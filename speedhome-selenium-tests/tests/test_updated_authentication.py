"""
Updated authentication tests using the corrected HeaderPage methods.
"""
import pytest
from utils.base_test import BaseTest
from pages.header_page import HeaderPage
from config.test_config import TestConfig
import time

class TestUpdatedAuthentication(BaseTest):
    """Updated authentication tests with correct method calls."""
    
    def setup_method(self):
        """Setup for each test"""
        super().setup_method()
        self.header_page = HeaderPage(self.driver)
    
    @pytest.mark.smoke
    def test_login_button_in_account_icon_opens_login_modal(self):
        """Test that the login modal opens via the user icon and can be closed."""
        print("🔍 Testing login modal flow...")
        
        # Step 1: Click the user icon to reveal the dropdown
        assert self.header_page.click_user_icon(), "Failed to click user icon."
        print("✅ User icon clicked.")
        
        # Step 2: Click the login link from the dropdown
        assert self.header_page.click_login_link(), "Failed to click login link in dropdown."
        print("✅ Login link clicked.")
        
        # Step 3: Assert that the modal is now visible
        assert self.header_page.is_login_modal_open(), "Login modal did not open."
        print("✅ Login modal opened successfully.")
        
        # Step 4: Close the modal
        self.header_page.close_login_modal()
        print("✅ Close button clicked.")
        
        # Step 5: Assert that the modal is now gone
        assert not self.header_page.is_login_modal_open(), "Login modal did not close."
        print("✅ Login modal closed successfully.")

    @pytest.mark.smoke
    def test_register_button_in_account_icon_opens_register_modal(self):
        """Test that the register modal opens via the user icon and can be closed."""
        print("🔍 Testing register modal...")
        
        # Step 1: Click the user icon to reveal the dropdown
        assert self.header_page.click_user_icon(), "Failed to click user icon."
        print("✅ User icon clicked.")

        # Step 2: Click the register link from the dropdown
        assert self.header_page.click_register_link(), "Failed to click register link in dropdown."
        print("✅ Register link clicked.")
        
        # Step 3: Assert that the modal is now visible
        assert self.header_page.is_register_modal_open(), "Register modal did not open."
        print("✅ Register modal opened successfully.")
        
        # Step 4: Close the modal
        self.header_page.close_register_modal()
        print("✅ Close button clicked.")
        
        # Step 5: Assert that the modal is now gone
        assert not self.header_page.is_register_modal_open(), "Register modal did not close."
        print("✅ Register modal closed successfully.")

    def test_successful_login_and_logout(self):
        """Test a full login and logout cycle for a tenant."""
        print("🔍 Testing full login and logout cycle...")

        # Perform login using the full flow
        login_success = self.header_page.login(
            TestConfig.TENANT_EMAIL, 
            TestConfig.TENANT_PASSWORD
        )
        assert login_success, "Login failed."
        
        # Verify user is logged in
        assert self.header_page.is_user_logged_in(), "User should be logged in after successful login."
        print(f"✅ Logged in successfully as {TestConfig.TENANT_EMAIL}")

        time.sleep(2) # Pause to observe

        # Perform logout
        self.header_page.logout()
        
        # Verify user is logged out
        assert self.header_page.is_user_logged_out(), "User should be logged out after clicking logout."
        print("✅ Logged out successfully.")

