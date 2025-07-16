"""
HomePage class for main page interactions
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
import time

class HomePage(BasePage):
    """Page Object Model for SpeedHome homepage"""
    
    # Locators
    SEARCH_INPUT = (By.XPATH, "//input[@placeholder='Search by property name or location...']")
    SEARCH_BUTTON = (By.XPATH, "//button[contains(@class, 'search-button')]")
    
    # Filter elements
    LOCATION_DROPDOWN = (By.XPATH, "//select[contains(@class, 'location-filter')]")
    PRICE_DROPDOWN = (By.XPATH, "//select[contains(@class, 'price-filter')]")
    TYPE_DROPDOWN = (By.XPATH, "//select[contains(@class, 'type-filter')]")
    FURNISHING_DROPDOWN = (By.XPATH, "//select[contains(@class, 'furnishing-filter')]")
    MORE_FILTERS_BUTTON = (By.XPATH, "//button[contains(text(), 'More Filters')]")
    
    # View mode toggles
    GRID_VIEW_BUTTON = (By.XPATH, "//button[contains(@class, 'grid-view')]")
    LIST_VIEW_BUTTON = (By.XPATH, "//button[contains(@class, 'list-view')]")
    
    # Property cards
    PROPERTY_CARDS = (By.XPATH, "//div[contains(@class, 'property-card')]")
    PROPERTY_TITLE = (By.XPATH, ".//h3[contains(@class, 'property-title')]")
    PROPERTY_PRICE = (By.XPATH, ".//span[contains(@class, 'property-price')]")
    PROPERTY_LOCATION = (By.XPATH, ".//span[contains(@class, 'property-location')]")
    FAVORITE_BUTTON = (By.XPATH, ".//button[contains(@class, 'favorite-btn')]")
    
    # More Filters Modal
    MODAL_OVERLAY = (By.XPATH, "//div[contains(@class, 'fixed inset-0')]")
    MODAL_CONTENT = (By.XPATH, "//div[contains(@class, 'bg-white rounded-xl')]")
    MODAL_CLOSE_BUTTON = (By.XPATH, "//button[contains(@class, 'text-gray-400')]")
    
    # Bedroom filters
    BEDROOM_ANY = (By.XPATH, "//button[contains(text(), 'Any') and ancestor::div[contains(text(), 'Number of Bedrooms')]]")
    BEDROOM_1_PLUS = (By.XPATH, "//button[contains(text(), '1+') and ancestor::div[contains(text(), 'Number of Bedrooms')]]")
    BEDROOM_2_PLUS = (By.XPATH, "//button[contains(text(), '2+') and ancestor::div[contains(text(), 'Number of Bedrooms')]]")
    BEDROOM_3_PLUS = (By.XPATH, "//button[contains(text(), '3+') and ancestor::div[contains(text(), 'Number of Bedrooms')]]")
    BEDROOM_4_PLUS = (By.XPATH, "//button[contains(text(), '4+') and ancestor::div[contains(text(), 'Number of Bedrooms')]]")
    
    # Bathroom filters
    BATHROOM_ANY = (By.XPATH, "//button[contains(text(), 'Any') and ancestor::div[contains(text(), 'Number of Bathrooms')]]")
    BATHROOM_1_PLUS = (By.XPATH, "//button[contains(text(), '1+') and ancestor::div[contains(text(), 'Number of Bathrooms')]]")
    BATHROOM_2_PLUS = (By.XPATH, "//button[contains(text(), '2+') and ancestor::div[contains(text(), 'Number of Bathrooms')]]")
    BATHROOM_3_PLUS = (By.XPATH, "//button[contains(text(), '3+') and ancestor::div[contains(text(), 'Number of Bathrooms')]]")
    BATHROOM_4_PLUS = (By.XPATH, "//button[contains(text(), '4+') and ancestor::div[contains(text(), 'Number of Bathrooms')]]")
    
    # Parking filters
    PARKING_ANY = (By.XPATH, "//button[contains(text(), 'Any') and ancestor::div[contains(text(), 'Number of Car Parks')]]")
    PARKING_1_PLUS = (By.XPATH, "//button[contains(text(), '1+') and ancestor::div[contains(text(), 'Number of Car Parks')]]")
    PARKING_2_PLUS = (By.XPATH, "//button[contains(text(), '2+') and ancestor::div[contains(text(), 'Number of Car Parks')]]")
    PARKING_3_PLUS = (By.XPATH, "//button[contains(text(), '3+') and ancestor::div[contains(text(), 'Number of Car Parks')]]")
    
    # Extra information checkboxes
    ZERO_DEPOSIT_CHECKBOX = (By.XPATH, "//button[contains(text(), 'Zero Deposit')]")
    PET_FRIENDLY_CHECKBOX = (By.XPATH, "//button[contains(text(), 'Pet-Friendly')]")
    
    # Amenities checkboxes
    SWIMMING_POOL_CHECKBOX = (By.XPATH, "//button[contains(text(), 'Swimming Pool')]")
    GYM_CHECKBOX = (By.XPATH, "//button[contains(text(), 'Gym')]")
    SECURITY_CHECKBOX = (By.XPATH, "//button[contains(text(), 'Security')]")
    PARKING_CHECKBOX = (By.XPATH, "//button[contains(text(), 'Parking')]")
    PLAYGROUND_CHECKBOX = (By.XPATH, "//button[contains(text(), 'Playground')]")
    BBQ_AREA_CHECKBOX = (By.XPATH, "//button[contains(text(), 'BBQ Area')]")
    LAUNDRY_CHECKBOX = (By.XPATH, "//button[contains(text(), 'Laundry')]")
    CONCIERGE_CHECKBOX = (By.XPATH, "//button[contains(text(), 'Concierge')]")
    PRIVATE_LIFT_CHECKBOX = (By.XPATH, "//button[contains(text(), 'Private Lift')]")
    COOKING_ALLOWED_CHECKBOX = (By.XPATH, "//button[contains(text(), 'Cooking Allowed')]")
    AIR_CONDITIONING_CHECKBOX = (By.XPATH, "//button[contains(text(), 'Air Conditioning')]")
    BALCONY_CHECKBOX = (By.XPATH, "//button[contains(text(), 'Balcony')]")
    WATER_HEATER_CHECKBOX = (By.XPATH, "//button[contains(text(), 'Water Heater')]")
    INTERNET_CHECKBOX = (By.XPATH, "//button[contains(text(), 'Internet')]")
    
    # Filter actions
    RESET_FILTER_BUTTON = (By.XPATH, "//button[contains(text(), 'Reset Filter')]")
    FILTER_APPLY_BUTTON = (By.XPATH, "//button[contains(text(), 'Filter')]")
    
    # Results
    RESULTS_COUNT = (By.XPATH, "//span[contains(@class, 'results-count')]")
    NO_RESULTS_MESSAGE = (By.XPATH, "//div[contains(text(), 'No properties found')]")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def search_properties(self, search_term):
        """Search for properties using search bar"""
        self.send_keys_to_element(self.SEARCH_INPUT, search_term)
        time.sleep(1)  # Wait for debounce
        return self
    
    def click_search_button(self):
        """Click search button"""
        self.click_element(self.SEARCH_BUTTON)
        return self
    
    def select_location_filter(self, location):
        """Select location from dropdown"""
        self.select_dropdown_by_text(self.LOCATION_DROPDOWN, location)
        return self
    
    def select_price_filter(self, price_range):
        """Select price range from dropdown"""
        self.select_dropdown_by_text(self.PRICE_DROPDOWN, price_range)
        return self
    
    def select_type_filter(self, property_type):
        """Select property type from dropdown"""
        self.select_dropdown_by_text(self.TYPE_DROPDOWN, property_type)
        return self
    
    def select_furnishing_filter(self, furnishing):
        """Select furnishing from dropdown"""
        self.select_dropdown_by_text(self.FURNISHING_DROPDOWN, furnishing)
        return self
    
    def click_more_filters(self):
        """Click More Filters button to open modal"""
        self.click_element(self.MORE_FILTERS_BUTTON)
        self.wait.until(EC.visibility_of_element_located(self.MODAL_CONTENT))
        return self
    
    def close_more_filters_modal(self):
        """Close More Filters modal"""
        self.click_element(self.MODAL_CLOSE_BUTTON)
        self.wait_for_element_to_disappear(self.MODAL_CONTENT)
        return self
    
    def select_bedroom_filter(self, bedrooms):
        """Select bedroom filter"""
        bedroom_map = {
            'Any': self.BEDROOM_ANY,
            '1+': self.BEDROOM_1_PLUS,
            '2+': self.BEDROOM_2_PLUS,
            '3+': self.BEDROOM_3_PLUS,
            '4+': self.BEDROOM_4_PLUS
        }
        self.click_element(bedroom_map[bedrooms])
        return self
    
    def select_bathroom_filter(self, bathrooms):
        """Select bathroom filter"""
        bathroom_map = {
            'Any': self.BATHROOM_ANY,
            '1+': self.BATHROOM_1_PLUS,
            '2+': self.BATHROOM_2_PLUS,
            '3+': self.BATHROOM_3_PLUS,
            '4+': self.BATHROOM_4_PLUS
        }
        self.click_element(bathroom_map[bathrooms])
        return self
    
    def select_parking_filter(self, parking):
        """Select parking filter"""
        parking_map = {
            'Any': self.PARKING_ANY,
            '1+': self.PARKING_1_PLUS,
            '2+': self.PARKING_2_PLUS,
            '3+': self.PARKING_3_PLUS
        }
        self.click_element(parking_map[parking])
        return self
    
    def toggle_zero_deposit(self):
        """Toggle zero deposit filter"""
        self.click_element(self.ZERO_DEPOSIT_CHECKBOX)
        return self
    
    def toggle_pet_friendly(self):
        """Toggle pet friendly filter"""
        self.click_element(self.PET_FRIENDLY_CHECKBOX)
        return self
    
    def select_amenities(self, amenities_list):
        """Select multiple amenities"""
        amenity_map = {
            'Swimming Pool': self.SWIMMING_POOL_CHECKBOX,
            'Gym': self.GYM_CHECKBOX,
            'Security': self.SECURITY_CHECKBOX,
            'Parking': self.PARKING_CHECKBOX,
            'Playground': self.PLAYGROUND_CHECKBOX,
            'BBQ Area': self.BBQ_AREA_CHECKBOX,
            'Laundry': self.LAUNDRY_CHECKBOX,
            'Concierge': self.CONCIERGE_CHECKBOX,
            'Private Lift': self.PRIVATE_LIFT_CHECKBOX,
            'Cooking Allowed': self.COOKING_ALLOWED_CHECKBOX,
            'Air Conditioning': self.AIR_CONDITIONING_CHECKBOX,
            'Balcony': self.BALCONY_CHECKBOX,
            'Water Heater': self.WATER_HEATER_CHECKBOX,
            'Internet': self.INTERNET_CHECKBOX
        }
        
        for amenity in amenities_list:
            if amenity in amenity_map:
                self.click_element(amenity_map[amenity])
        return self
    
    def reset_filters(self):
        """Reset all filters"""
        self.click_element(self.RESET_FILTER_BUTTON)
        return self
    
    def apply_filters(self):
        """Apply filters and close modal"""
        self.click_element(self.FILTER_APPLY_BUTTON)
        self.wait_for_element_to_disappear(self.MODAL_CONTENT)
        return self
    
    def open_filters(self):
        """Alias for click_more_filters to match test script."""
        return self.click_more_filters()

    def has_view_mode_toggle(self):
        """Check if view mode toggle buttons are present."""
        return self.is_element_visible(self.GRID_VIEW_BUTTON) and self.is_element_visible(self.LIST_VIEW_BUTTON)

    def type_in_search(self, search_term):
        """Alias for search_properties to match test script."""
        return self.search_properties(search_term)
    
    def switch_to_grid_view(self):
        """Switch to grid view"""
        self.click_element(self.GRID_VIEW_BUTTON)
        return self
    
    def switch_to_list_view(self):
        """Switch to list view"""
        self.click_element(self.LIST_VIEW_BUTTON)
        return self
    
    def get_property_cards(self):
        """Get all property cards"""
        return self.find_elements(self.PROPERTY_CARDS)
    
    def get_visible_properties(self):
        """
        Gets all currently visible property card elements.
        This is an alias for get_property_cards() to ensure test compatibility.
        """
        return self.get_property_cards()
    
    def get_property_count(self):
        """Get number of properties displayed"""
        return len(self.get_property_cards())
    
    def click_property_card(self, index=0):
        """Click on property card by index"""
        cards = self.get_property_cards()
        if index < len(cards):
            cards[index].click()
            return True
        return False
    
    def click_first_property(self):
        """Click on first property card"""
        return self.click_property_card(0)
    
    def toggle_favorite(self, index=0):
        """Toggle favorite for property by index"""
        cards = self.get_property_cards()
        if index < len(cards):
            favorite_btn = cards[index].find_element(*self.FAVORITE_BUTTON)
            favorite_btn.click()
            return True
        return False
    
    def get_property_details(self, index=0):
        """Get property details from card"""
        cards = self.get_property_cards()
        if index < len(cards):
            card = cards[index]
            return {
                'title': card.find_element(*self.PROPERTY_TITLE).text,
                'price': card.find_element(*self.PROPERTY_PRICE).text,
                'location': card.find_element(*self.PROPERTY_LOCATION).text
            }
        return None
    
    def is_no_results_displayed(self):
        """Check if no results message is displayed"""
        return self.is_element_visible(self.NO_RESULTS_MESSAGE)
    
    def get_results_count_text(self):
        """Get results count text"""
        if self.is_element_visible(self.RESULTS_COUNT):
            return self.get_element_text(self.RESULTS_COUNT)
        return None
    
    def take_screenshot(self, name):
        """Take screenshot for debugging"""
        try:
            import os
            os.makedirs("reports/screenshots", exist_ok=True)
            self.driver.save_screenshot(f"reports/screenshots/{name}.png")
            return True
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return False

