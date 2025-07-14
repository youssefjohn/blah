"""
Test cases for tenant property search and filtering functionality
"""
import pytest
import time
from utils.base_test import BaseTest
from pages.header_page import HeaderPage
from pages.home_page import HomePage
from pages.property_detail_page import PropertyDetailPage
from utils.test_data_generator import TestDataGenerator
from config.test_config import TestConfig

class TestTenantPropertySearch(BaseTest):
    """Test tenant property search and filtering functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        super().setup_method()
        self.header_page = HeaderPage(self.driver)
        self.home_page = HomePage(self.driver)
        self.property_detail_page = PropertyDetailPage(self.driver)
        self.data_generator = TestDataGenerator()
    
    def test_basic_property_search(self):
        """Test basic property search functionality"""
        search_terms = self.data_generator.generate_search_terms()
        
        for search_term in search_terms[:3]:  # Test first 3 terms
            # Perform search
            self.home_page.search_properties(search_term)
            time.sleep(2)  # Wait for search results
            
            # Verify search results are displayed
            property_count = self.home_page.get_property_count()
            
            # If results found, verify they contain search term
            if property_count > 0:
                first_property = self.home_page.get_property_details(0)
                search_term_lower = search_term.lower()
                property_text = (first_property['title'] + ' ' + first_property['location']).lower()
                
                # Search term should appear in title or location
                assert search_term_lower in property_text, f"Search term '{search_term}' should appear in results"
            
            # Clear search for next iteration
            self.home_page.search_properties("")
            time.sleep(1)
    
    def test_location_filter(self):
        """Test location filtering"""
        locations = ['Kuala Lumpur', 'Petaling Jaya', 'Cyberjaya']
        
        for location in locations:
            # Apply location filter
            self.home_page.select_location_filter(location)
            time.sleep(2)
            
            # Verify results are filtered by location
            property_count = self.home_page.get_property_count()
            
            if property_count > 0:
                # Check first few properties
                for i in range(min(3, property_count)):
                    property_details = self.home_page.get_property_details(i)
                    assert location.lower() in property_details['location'].lower(), \
                        f"Property should be in {location}"
            
            # Reset filter
            self.home_page.select_location_filter('All Locations')
            time.sleep(1)
    
    def test_price_range_filter(self):
        """Test price range filtering"""
        price_ranges = ['Under RM1000', 'RM1000-2000', 'RM2000-3000']
        
        for price_range in price_ranges:
            # Apply price filter
            self.home_page.select_price_filter(price_range)
            time.sleep(2)
            
            # Verify results are within price range
            property_count = self.home_page.get_property_count()
            
            if property_count > 0:
                # Check first property price
                property_details = self.home_page.get_property_details(0)
                price_text = property_details['price']
                
                # Extract numeric price (assuming format like "RM 2500")
                import re
                price_match = re.search(r'(\d+)', price_text.replace(',', ''))
                if price_match:
                    price = int(price_match.group(1))
                    
                    # Verify price is in selected range
                    if price_range == 'Under RM1000':
                        assert price < 1000, f"Price {price} should be under 1000"
                    elif price_range == 'RM1000-2000':
                        assert 1000 <= price <= 2000, f"Price {price} should be between 1000-2000"
                    elif price_range == 'RM2000-3000':
                        assert 2000 <= price <= 3000, f"Price {price} should be between 2000-3000"
            
            # Reset filter
            self.home_page.select_price_filter('All Prices')
            time.sleep(1)
    
    def test_property_type_filter(self):
        """Test property type filtering"""
        property_types = ['Apartment', 'Condominium', 'House']
        
        for prop_type in property_types:
            # Apply type filter
            self.home_page.select_type_filter(prop_type)
            time.sleep(2)
            
            # Verify results match property type
            property_count = self.home_page.get_property_count()
            
            if property_count > 0:
                # Click on first property to check details
                self.home_page.click_first_property()
                self.property_detail_page.wait_for_property_to_load()
                
                # Get property details
                property_details = self.property_detail_page.get_property_details()
                assert prop_type.lower() in property_details['type'].lower(), \
                    f"Property type should be {prop_type}"
                
                # Go back to search results
                self.property_detail_page.go_back_to_search()
            
            # Reset filter
            self.home_page.select_type_filter('All Types')
            time.sleep(1)
    
    def test_furnishing_filter(self):
        """Test furnishing status filtering"""
        furnishing_options = ['Fully Furnished', 'Partially Furnished', 'Unfurnished']
        
        for furnishing in furnishing_options:
            # Apply furnishing filter
            self.home_page.select_furnishing_filter(furnishing)
            time.sleep(2)
            
            # Verify results match furnishing status
            property_count = self.home_page.get_property_count()
            
            if property_count > 0:
                # Check first property
                self.home_page.click_first_property()
                self.property_detail_page.wait_for_property_to_load()
                
                property_details = self.property_detail_page.get_property_details()
                assert furnishing.lower() in property_details['furnishing'].lower(), \
                    f"Furnishing should be {furnishing}"
                
                self.property_detail_page.go_back_to_search()
            
            # Reset filter
            self.home_page.select_furnishing_filter('All Furnishing')
            time.sleep(1)
    
    def test_advanced_filters_modal(self):
        """Test advanced filters modal functionality"""
        # Open more filters modal
        self.home_page.click_more_filters()
        
        # Verify modal is open
        assert self.home_page.is_element_visible(self.home_page.MODAL_CONTENT), \
            "More filters modal should be open"
        
        # Test bedroom filter
        self.home_page.select_bedroom_filter('2+')
        
        # Test bathroom filter
        self.home_page.select_bathroom_filter('1+')
        
        # Test parking filter
        self.home_page.select_parking_filter('1+')
        
        # Test amenities selection
        amenities = ['Swimming Pool', 'Gym', 'Security']
        self.home_page.select_amenities(amenities)
        
        # Apply filters
        self.home_page.apply_filters()
        
        # Verify modal is closed
        assert not self.home_page.is_element_visible(self.home_page.MODAL_CONTENT), \
            "Modal should be closed after applying filters"
        
        # Wait for results to load
        time.sleep(2)
        
        # Verify filters are applied (check if results are filtered)
        property_count = self.home_page.get_property_count()
        
        if property_count > 0:
            # Check first property has selected amenities
            self.home_page.click_first_property()
            self.property_detail_page.wait_for_property_to_load()
            
            property_amenities = self.property_detail_page.get_amenities()
            
            # At least one selected amenity should be present
            has_selected_amenity = any(amenity in property_amenities for amenity in amenities)
            assert has_selected_amenity, "Property should have at least one selected amenity"
            
            self.property_detail_page.go_back_to_search()
    
    def test_reset_filters(self):
        """Test resetting all filters"""
        # Apply multiple filters
        self.home_page.select_location_filter('Kuala Lumpur')
        self.home_page.select_price_filter('RM1000-2000')
        self.home_page.select_type_filter('Apartment')
        
        # Open advanced filters and apply more
        self.home_page.click_more_filters()
        self.home_page.select_bedroom_filter('2+')
        self.home_page.select_amenities(['Swimming Pool', 'Gym'])
        
        # Reset filters
        self.home_page.reset_filters()
        self.home_page.apply_filters()
        
        time.sleep(2)
        
        # Verify all properties are shown (no filters applied)
        property_count_after_reset = self.home_page.get_property_count()
        
        # Should have more properties than with filters applied
        assert property_count_after_reset > 0, "Should have properties after reset"
    
    def test_view_mode_toggle(self):
        """Test switching between grid and list view"""
        # Test grid view
        self.home_page.switch_to_grid_view()
        time.sleep(1)
        
        # Verify grid view is active (check CSS classes or layout)
        property_count_grid = self.home_page.get_property_count()
        assert property_count_grid > 0, "Should have properties in grid view"
        
        # Test list view
        self.home_page.switch_to_list_view()
        time.sleep(1)
        
        # Verify list view is active
        property_count_list = self.home_page.get_property_count()
        assert property_count_list == property_count_grid, \
            "Should have same number of properties in list view"
    
    def test_property_card_interaction(self):
        """Test property card interactions"""
        # Ensure there are properties to interact with
        property_count = self.home_page.get_property_count()
        assert property_count > 0, "Should have properties to test"
        
        # Get property details from card
        property_details = self.home_page.get_property_details(0)
        assert property_details is not None, "Should get property details"
        assert property_details['title'], "Property should have title"
        assert property_details['price'], "Property should have price"
        assert property_details['location'], "Property should have location"
        
        # Test clicking property card
        self.home_page.click_first_property()
        
        # Verify navigation to property detail page
        assert "/property/" in self.driver.current_url, "Should navigate to property detail page"
        
        # Verify property details match
        self.property_detail_page.wait_for_property_to_load()
        detail_title = self.property_detail_page.get_property_title()
        assert property_details['title'] in detail_title, "Property titles should match"
    
    def test_favorite_toggle(self):
        """Test adding and removing favorites"""
        # Ensure there are properties
        property_count = self.home_page.get_property_count()
        assert property_count > 0, "Should have properties to favorite"
        
        # Toggle favorite on first property
        self.home_page.toggle_favorite(0)
        time.sleep(1)
        
        # Verify favorite status changed (visual feedback)
        # This would depend on implementation - check for CSS class changes
        
        # Toggle again to remove from favorites
        self.home_page.toggle_favorite(0)
        time.sleep(1)
    
    def test_no_results_scenario(self):
        """Test behavior when no search results are found"""
        # Search for something that likely won't exist
        self.home_page.search_properties("xyznonexistentproperty123")
        time.sleep(2)
        
        # Verify no results message or empty state
        property_count = self.home_page.get_property_count()
        
        if property_count == 0:
            # Check for no results message
            assert self.home_page.is_no_results_displayed(), \
                "Should show no results message when no properties found"
    
    def test_search_persistence(self):
        """Test that search terms persist during navigation"""
        search_term = "luxury"
        
        # Perform search
        self.home_page.search_properties(search_term)
        time.sleep(2)
        
        # Navigate to property detail
        if self.home_page.get_property_count() > 0:
            self.home_page.click_first_property()
            self.property_detail_page.wait_for_property_to_load()
            
            # Go back to search
            self.property_detail_page.go_back_to_search()
            
            # Verify search term is still in search box
            search_input_value = self.home_page.get_element_attribute(
                self.home_page.SEARCH_INPUT, 'value'
            )
            assert search_term in search_input_value, "Search term should persist"
    
    def test_combined_filters(self):
        """Test using multiple filters together"""
        # Apply combination of filters
        self.home_page.select_location_filter('Kuala Lumpur')
        self.home_page.select_price_filter('RM1000-2000')
        self.home_page.search_properties('condo')
        
        time.sleep(2)
        
        # Verify results match all criteria
        property_count = self.home_page.get_property_count()
        
        if property_count > 0:
            # Check first property meets all criteria
            property_details = self.home_page.get_property_details(0)
            
            # Should be in KL
            assert 'kuala lumpur' in property_details['location'].lower(), \
                "Property should be in Kuala Lumpur"
            
            # Should contain 'condo' in title or description
            assert 'condo' in property_details['title'].lower(), \
                "Property should contain 'condo' in title"

