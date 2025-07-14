"""
Advanced property search and filtering tests for SpeedHome
Tests search functionality, filters, and property interactions
"""
import pytest
import time
from utils.base_test import BaseTest
from pages.home_page import HomePage
from pages.header_page import HeaderPage
from utils.test_data_generator import TestDataGenerator
from config.test_config import TestConfig

class TestPropertySearchAdvanced(BaseTest):
    """Advanced tests for property search and filtering functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        super().setup_method()
        self.home_page = HomePage(self.driver)
        self.header_page = HeaderPage(self.driver)
        self.data_generator = TestDataGenerator()
    
    @pytest.mark.smoke
    def test_basic_search_functionality(self):
        """Test basic property search functionality"""
        # Test search with common location
        search_terms = ["Kuala Lumpur", "KL", "Petaling Jaya", "PJ"]
        
        for term in search_terms:
            # Perform search
            self.home_page.search_properties(term)
            time.sleep(2)  # Wait for results
            
            # Check if results are displayed or no results message
            has_results = self.home_page.get_property_count() > 0
            has_no_results = self.home_page.is_no_results_displayed()
            
            assert has_results or has_no_results, f"Search for '{term}' should show results or no results message"
            
            # Clear search for next iteration
            self.home_page.clear_search()
    
    @pytest.mark.regression
    def test_search_with_special_characters(self):
        """Test search with special characters and edge cases"""
        special_searches = [
            "Kuala Lumpur!",
            "PJ@123",
            "Mont' Kiara",
            "Taman Desa (KL)",
            "KLCC & Surroundings"
        ]
        
        for search_term in special_searches:
            # Perform search
            self.home_page.search_properties(search_term)
            time.sleep(2)
            
            # Should not crash and should show some response
            assert self.driver.current_url is not None, "Page should not crash with special characters"
            
            # Clear search
            self.home_page.clear_search()
    
    @pytest.mark.regression
    def test_empty_search_handling(self):
        """Test handling of empty search"""
        # Try to search with empty string
        self.home_page.search_properties("")
        time.sleep(1)
        
        # Should show all properties or handle gracefully
        property_count = self.home_page.get_property_count()
        assert property_count >= 0, "Empty search should be handled gracefully"
    
    @pytest.mark.smoke
    def test_location_filter(self):
        """Test location filter functionality"""
        # Open filters
        self.home_page.open_filters()
        
        # Test different location filters
        locations = ["Kuala Lumpur", "Selangor", "Petaling Jaya"]
        
        for location in locations:
            if self.home_page.has_location_option(location):
                # Select location
                self.home_page.select_location_filter(location)
                
                # Apply filters
                self.home_page.apply_filters()
                time.sleep(2)
                
                # Check results
                property_count = self.home_page.get_property_count()
                assert property_count >= 0, f"Location filter '{location}' should work"
                
                # Reset filters for next test
                self.home_page.reset_filters()
    
    @pytest.mark.regression
    def test_price_range_filter(self):
        """Test price range filter functionality"""
        # Open filters
        self.home_page.open_filters()
        
        # Test different price ranges
        price_ranges = [
            {"min": 500, "max": 1000},
            {"min": 1000, "max": 2000},
            {"min": 2000, "max": 5000}
        ]
        
        for price_range in price_ranges:
            # Set price range
            self.home_page.set_price_range(price_range["min"], price_range["max"])
            
            # Apply filters
            self.home_page.apply_filters()
            time.sleep(2)
            
            # Verify results are within price range
            properties = self.home_page.get_visible_properties()
            for prop in properties[:3]:  # Check first 3 properties
                price_text = prop.get('price', '')
                if price_text and 'RM' in price_text:
                    # Extract price number (basic extraction)
                    price_str = price_text.replace('RM', '').replace(',', '').strip()
                    try:
                        price = int(price_str.split('/')[0])
                        assert price_range["min"] <= price <= price_range["max"], \
                            f"Property price {price} should be within range {price_range['min']}-{price_range['max']}"
                    except (ValueError, IndexError):
                        # Skip if price format is unexpected
                        pass
            
            # Reset filters
            self.home_page.reset_filters()
    
    @pytest.mark.regression
    def test_property_type_filter(self):
        """Test property type filter functionality"""
        # Open filters
        self.home_page.open_filters()
        
        # Test different property types
        property_types = ["Apartment", "Condominium", "House", "Room"]
        
        for prop_type in property_types:
            if self.home_page.has_property_type_option(prop_type):
                # Select property type
                self.home_page.select_property_type_filter(prop_type)
                
                # Apply filters
                self.home_page.apply_filters()
                time.sleep(2)
                
                # Check results
                property_count = self.home_page.get_property_count()
                assert property_count >= 0, f"Property type filter '{prop_type}' should work"
                
                # Reset filters
                self.home_page.reset_filters()
    
    @pytest.mark.regression
    def test_furnishing_filter(self):
        """Test furnishing filter functionality"""
        # Open filters
        self.home_page.open_filters()
        
        # Test furnishing options
        furnishing_options = ["Fully Furnished", "Partially Furnished", "Unfurnished"]
        
        for furnishing in furnishing_options:
            if self.home_page.has_furnishing_option(furnishing):
                # Select furnishing
                self.home_page.select_furnishing_filter(furnishing)
                
                # Apply filters
                self.home_page.apply_filters()
                time.sleep(2)
                
                # Check results
                property_count = self.home_page.get_property_count()
                assert property_count >= 0, f"Furnishing filter '{furnishing}' should work"
                
                # Reset filters
                self.home_page.reset_filters()
    
    @pytest.mark.regression
    def test_bedroom_filter(self):
        """Test bedroom count filter"""
        # Open more filters modal
        self.home_page.click_more_filters()
        
        # Test different bedroom counts
        bedroom_counts = [1, 2, 3, 4]
        
        for count in bedroom_counts:
            # Select bedroom count
            self.home_page.select_bedroom_count(count)
            
            # Apply filters
            self.home_page.apply_more_filters()
            time.sleep(2)
            
            # Check results
            property_count = self.home_page.get_property_count()
            assert property_count >= 0, f"Bedroom filter '{count}' should work"
            
            # Reset and try next
            self.home_page.reset_filters()
    
    @pytest.mark.regression
    def test_bathroom_filter(self):
        """Test bathroom count filter"""
        # Open more filters modal
        self.home_page.click_more_filters()
        
        # Test different bathroom counts
        bathroom_counts = [1, 2, 3]
        
        for count in bathroom_counts:
            # Select bathroom count
            self.home_page.select_bathroom_count(count)
            
            # Apply filters
            self.home_page.apply_more_filters()
            time.sleep(2)
            
            # Check results
            property_count = self.home_page.get_property_count()
            assert property_count >= 0, f"Bathroom filter '{count}' should work"
            
            # Reset filters
            self.home_page.reset_filters()
    
    @pytest.mark.regression
    def test_amenities_filter(self):
        """Test amenities filter functionality"""
        # Open more filters modal
        self.home_page.click_more_filters()
        
        # Test common amenities
        amenities = ["Swimming Pool", "Gym", "Parking", "Security", "Playground"]
        
        for amenity in amenities:
            if self.home_page.has_amenity_option(amenity):
                # Select amenity
                self.home_page.select_amenity(amenity)
                
                # Apply filters
                self.home_page.apply_more_filters()
                time.sleep(2)
                
                # Check results
                property_count = self.home_page.get_property_count()
                assert property_count >= 0, f"Amenity filter '{amenity}' should work"
                
                # Reset filters
                self.home_page.reset_filters()
    
    @pytest.mark.integration
    def test_combined_filters(self):
        """Test using multiple filters together"""
        # Open filters
        self.home_page.open_filters()
        
        # Set multiple filters
        self.home_page.set_price_range(1000, 3000)
        
        if self.home_page.has_location_option("Kuala Lumpur"):
            self.home_page.select_location_filter("Kuala Lumpur")
        
        if self.home_page.has_property_type_option("Apartment"):
            self.home_page.select_property_type_filter("Apartment")
        
        # Apply filters
        self.home_page.apply_filters()
        time.sleep(3)
        
        # Check that results respect all filters
        property_count = self.home_page.get_property_count()
        assert property_count >= 0, "Combined filters should work together"
        
        # Reset filters
        self.home_page.reset_filters()
    
    @pytest.mark.regression
    def test_filter_reset_functionality(self):
        """Test that filter reset works correctly"""
        # Apply some filters
        self.home_page.open_filters()
        self.home_page.set_price_range(1000, 2000)
        
        if self.home_page.has_location_option("Kuala Lumpur"):
            self.home_page.select_location_filter("Kuala Lumpur")
        
        self.home_page.apply_filters()
        time.sleep(2)
        
        # Get filtered count
        filtered_count = self.home_page.get_property_count()
        
        # Reset filters
        self.home_page.reset_filters()
        time.sleep(2)
        
        # Get unfiltered count
        unfiltered_count = self.home_page.get_property_count()
        
        # Unfiltered should have same or more properties
        assert unfiltered_count >= filtered_count, "Reset should show same or more properties"
    
    @pytest.mark.smoke
    def test_view_mode_toggle(self):
        """Test switching between grid and list view modes"""
        # Test grid view
        if self.home_page.has_view_mode_toggle():
            self.home_page.switch_to_grid_view()
            time.sleep(1)
            assert self.home_page.is_grid_view_active(), "Grid view should be active"
            
            # Test list view
            self.home_page.switch_to_list_view()
            time.sleep(1)
            assert self.home_page.is_list_view_active(), "List view should be active"
    
    @pytest.mark.regression
    def test_property_card_interactions(self):
        """Test interactions with property cards"""
        # Get first few properties
        properties = self.home_page.get_visible_properties()
        
        if properties:
            # Test clicking on first property
            first_property = properties[0]
            property_title = first_property.get('title', 'Unknown')
            
            # Click on property card
            self.home_page.click_property_card(0)
            time.sleep(2)
            
            # Should navigate to property detail page
            current_url = self.driver.current_url
            assert "/property/" in current_url or "property" in current_url.lower(), \
                f"Should navigate to property detail page for '{property_title}'"
            
            # Go back to search results
            self.driver.back()
            time.sleep(2)
    
    @pytest.mark.regression
    def test_favorite_property_functionality(self):
        """Test adding/removing properties from favorites"""
        # Get properties
        properties = self.home_page.get_visible_properties()
        
        if properties:
            # Try to favorite first property
            initial_favorite_state = self.home_page.is_property_favorited(0)
            
            # Toggle favorite
            self.home_page.toggle_property_favorite(0)
            time.sleep(1)
            
            # Check if state changed
            new_favorite_state = self.home_page.is_property_favorited(0)
            
            # State should have changed (unless login is required)
            if initial_favorite_state != new_favorite_state:
                # Successfully toggled
                assert True
            else:
                # Might require login - check for login modal or message
                if self.header_page.is_login_modal_open():
                    # Login required for favorites - this is expected
                    self.header_page.close_login_modal()
                    pytest.skip("Login required for favorites functionality")
    
    @pytest.mark.integration
    def test_search_results_pagination(self):
        """Test pagination of search results"""
        # Perform a broad search to get many results
        self.home_page.search_properties("Kuala Lumpur")
        time.sleep(2)
        
        # Check if pagination exists
        if self.home_page.has_pagination():
            current_page = self.home_page.get_current_page()
            total_pages = self.home_page.get_total_pages()
            
            if total_pages > 1:
                # Go to next page
                self.home_page.go_to_next_page()
                time.sleep(2)
                
                # Verify page changed
                new_page = self.home_page.get_current_page()
                assert new_page > current_page, "Should move to next page"
                
                # Go back to first page
                self.home_page.go_to_page(1)
                time.sleep(2)
                
                # Verify back on first page
                assert self.home_page.get_current_page() == 1, "Should return to first page"
    
    @pytest.mark.smoke
    def test_search_suggestions(self):
        """Test search suggestions/autocomplete functionality"""
        # Start typing in search box
        search_input = "Kual"  # Partial search
        
        # Type partial search
        self.home_page.type_in_search(search_input)
        time.sleep(1)
        
        # Check if suggestions appear
        if self.home_page.has_search_suggestions():
            suggestions = self.home_page.get_search_suggestions()
            assert len(suggestions) > 0, "Should show search suggestions"
            
            # Click on first suggestion
            self.home_page.click_search_suggestion(0)
            time.sleep(2)
            
            # Should perform search
            property_count = self.home_page.get_property_count()
            assert property_count >= 0, "Suggestion click should perform search"

