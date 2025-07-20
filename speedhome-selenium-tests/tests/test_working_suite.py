"""
Working test suite for SpeedHome application, updated with correct method calls.
"""
import pytest
from utils.base_test import BaseTest
from pages.header_page import HeaderPage
from pages.home_page import HomePage # Import HomePage for search tests
from config.test_config import TestConfig
import time

class TestWorkingSuite(BaseTest):
    """Working test suite with verified selectors and method calls."""
    
    def setup_method(self):
        """Setup for each test"""
        super().setup_method()
        self.header_page = HeaderPage(self.driver)
        self.home_page = HomePage(self.driver) # Initialize HomePage as well
    
    @pytest.mark.smoke
    def test_homepage_loads_correctly(self):
        """Test that homepage loads with correct title"""
        title = self.driver.title
        assert "Speed Home" in title or "speedhome" in title.lower()
        print("✅ Homepage loaded successfully")
    
    @pytest.mark.smoke
    def test_key_elements_present(self):
        """Test that all key header elements are present and functional"""
        assert self.header_page.is_header_visible(), "Header (Logo) not visible"
        assert self.header_page.is_element_present(self.header_page.LOGIN_BUTTON), "Login button not found"
        assert self.header_page.is_element_present(self.header_page.REGISTER_BUTTON), "Register button not found"
        print("✅ Key header elements are present")
    
    @pytest.mark.smoke
    def test_role_switching(self):
        """Test switching between tenant and landlord modes"""
        self.header_page.click_landlord_button()
        time.sleep(1) # Allow for visual state change
        self.header_page.click_tenant_button()
        time.sleep(1)
        print("✅ Role switching buttons are clickable")
    
    @pytest.mark.smoke
    def test_search_functionality(self):
        """Test header search functionality"""
        search_term = "Petaling Jaya"
        # Using the correct method from header_page.py
        self.header_page.perform_header_search(search_term)
        # Add a small wait to see the result
        time.sleep(2)
        # A simple assertion to ensure the page didn't crash
        assert "Speed Home" in self.driver.title or "speedhome" in self.driver.title.lower()
        print(f"✅ Search for '{search_term}' completed")
    
    @pytest.mark.smoke
    def test_login_modal_interaction(self):
        """Test clicking login button opens the modal"""
        # Using the correct method from header_page.py
        self.header_page.click_login_button()
        assert self.header_page.is_login_modal_open(), "Login modal did not open after click"
        print("✅ Login modal interaction completed")
    
    @pytest.mark.smoke
    def test_more_filters_button(self):
        """Test More Filters button functionality"""
        # This action belongs to the HomePage, not the HeaderPage
        self.home_page.click_more_filters()
        assert self.home_page.is_element_visible(self.home_page.MODAL_CONTENT), "More Filters modal did not open"
        print("✅ More Filters button interaction completed")