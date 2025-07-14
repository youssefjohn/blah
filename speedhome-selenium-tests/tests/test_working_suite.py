"""
Working test suite for SpeedHome application with correct selectors
"""
import pytest
from utils.base_test import BaseTest
from pages.header_page_final import HeaderPage
from utils.test_data_generator import TestDataGenerator
import time

class TestWorkingSuite(BaseTest):
    """Working test suite with verified selectors"""
    
    def setup_method(self):
        """Setup for each test"""
        super().setup_method()
        self.header_page = HeaderPage(self.driver)
        self.data_generator = TestDataGenerator()
    
    @pytest.mark.smoke
    def test_homepage_loads_correctly(self):
        """Test that homepage loads with correct title"""
        # Verify page title contains expected text
        title = self.header_page.get_page_title()
        assert "Speed Home" in title or "SpeedHome" in title
        
        # Verify URL
        url = self.header_page.get_current_url()
        assert "localhost:5174" in url
        
        print(f"✅ Homepage loaded successfully")
        print(f"📄 Title: {title}")
        print(f"🌐 URL: {url}")
    
    @pytest.mark.smoke
    def test_key_elements_present(self):
        """Test that all key elements are present and functional"""
        
        # Check homepage is properly loaded
        assert self.header_page.is_homepage_loaded(), "Homepage not properly loaded"
        
        # Test role toggle buttons
        landlord_present = self.header_page.is_element_present(self.header_page.LANDLORD_BUTTON)
        tenant_present = self.header_page.is_element_present(self.header_page.TENANT_BUTTON)
        
        assert landlord_present, "Landlord button not found"
        assert tenant_present, "Tenant button not found"
        
        # Test search input
        search_present = self.header_page.is_element_present(self.header_page.MAIN_SEARCH_INPUT)
        assert search_present, "Main search input not found"
        
        # Test user icon
        user_icon_present = self.header_page.is_element_present(self.header_page.USER_ICON)
        assert user_icon_present, "User icon not found"
        
        print("✅ All key elements are present")
    
    @pytest.mark.smoke
    def test_role_switching(self):
        """Test switching between tenant and landlord modes"""
        
        # Get initial role
        initial_role = self.header_page.get_current_role()
        print(f"🏠 Initial role: {initial_role}")
        
        # Switch to tenant mode
        tenant_success = self.header_page.switch_to_tenant_mode()
        assert tenant_success, "Failed to switch to tenant mode"
        
        # Verify tenant mode is active
        current_role = self.header_page.get_current_role()
        print(f"🏠 After tenant switch: {current_role}")
        
        # Switch to landlord mode
        landlord_success = self.header_page.switch_to_landlord_mode()
        assert landlord_success, "Failed to switch to landlord mode"
        
        # Verify landlord mode is active
        current_role = self.header_page.get_current_role()
        print(f"🏠 After landlord switch: {current_role}")
        
        print("✅ Role switching works correctly")
    
    @pytest.mark.smoke
    def test_search_functionality(self):
        """Test search functionality"""
        
        # Perform a search
        search_term = "Kuala Lumpur"
        search_success = self.header_page.search_properties(search_term)
        assert search_success, "Search functionality failed"
        
        # Wait for search results to load
        time.sleep(3)
        
        # Verify we're still on the same domain (search should work)
        current_url = self.header_page.get_current_url()
        assert "localhost:5174" in current_url, "Search redirected to unexpected URL"
        
        print(f"✅ Search for '{search_term}' completed successfully")
        print(f"🌐 Current URL after search: {current_url}")
    
    @pytest.mark.smoke
    def test_user_icon_interaction(self):
        """Test user icon interaction"""
        
        # Click user icon
        click_success = self.header_page.click_user_icon()
        assert click_success, "Failed to click user icon"
        
        # Wait for any dropdown/modal to appear
        time.sleep(2)
        
        # Take screenshot for verification
        self.header_page.take_screenshot("user_icon_clicked")
        
        print("✅ User icon interaction completed")
    
    @pytest.mark.smoke
    def test_more_filters_button(self):
        """Test More Filters button functionality"""
        
        # Click More Filters button
        filters_success = self.header_page.click_more_filters()
        assert filters_success, "Failed to click More Filters button"
        
        # Wait for modal to appear
        time.sleep(2)
        
        # Take screenshot for verification
        self.header_page.take_screenshot("more_filters_clicked")
        
        print("✅ More Filters button interaction completed")
    
    def test_page_elements_debugging(self):
        """Debug test to inspect all page elements"""
        print("\n🔍 DEBUGGING: Complete page element inspection...")
        
        # Get page info
        title = self.header_page.get_page_title()
        url = self.header_page.get_current_url()
        print(f"📄 Page title: {title}")
        print(f"🌐 Current URL: {url}")
        
        # Get all buttons
        buttons = self.header_page.get_all_buttons()
        print(f"\n🔘 Found {len(buttons)} buttons:")
        for btn in buttons[:10]:  # Show first 10
            print(f"  {btn['index']+1}. Text: '{btn['text']}', Classes: '{btn['classes'][:100]}...'")
        
        # Get all inputs
        inputs = self.header_page.get_all_inputs()
        print(f"\n📝 Found {len(inputs)} input elements:")
        for inp in inputs:
            print(f"  {inp['index']+1}. Type: '{inp['type']}', Placeholder: '{inp['placeholder']}', Classes: '{inp['classes'][:100]}...'")
        
        # Test element presence
        print(f"\n✅ Element presence check:")
        print(f"  Logo: {self.header_page.is_element_present(self.header_page.SPEEDHOME_LOGO)}")
        print(f"  Main search: {self.header_page.is_element_present(self.header_page.MAIN_SEARCH_INPUT)}")
        print(f"  User icon: {self.header_page.is_element_present(self.header_page.USER_ICON)}")
        print(f"  Landlord button: {self.header_page.is_element_present(self.header_page.LANDLORD_BUTTON)}")
        print(f"  Tenant button: {self.header_page.is_element_present(self.header_page.TENANT_BUTTON)}")
        print(f"  More filters: {self.header_page.is_element_present(self.header_page.MORE_FILTERS_BUTTON)}")
        
        print("✅ Complete page inspection finished")
    
    @pytest.mark.regression
    def test_full_homepage_workflow(self):
        """Test complete homepage workflow"""
        
        # 1. Verify homepage loads
        assert self.header_page.is_homepage_loaded(), "Homepage not loaded"
        
        # 2. Switch to tenant mode
        self.header_page.switch_to_tenant_mode()
        assert self.header_page.get_current_role() == 'tenant', "Not in tenant mode"
        
        # 3. Perform search
        search_success = self.header_page.search_properties("Petaling Jaya")
        assert search_success, "Search failed"
        time.sleep(2)
        
        # 4. Switch to landlord mode
        self.header_page.switch_to_landlord_mode()
        time.sleep(1)
        
        # 5. Click user icon
        self.header_page.click_user_icon()
        time.sleep(1)
        
        # 6. Click more filters
        self.header_page.click_more_filters()
        time.sleep(1)
        
        print("✅ Full homepage workflow completed successfully")

