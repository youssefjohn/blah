"""
PropertyDetailPage class for property details and booking interactions
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
import time

class PropertyDetailPage(BasePage):
    """Page Object Model for property detail page"""
    
    # Property information
    PROPERTY_TITLE = (By.XPATH, "//h1[contains(@class, 'property-title')]")
    PROPERTY_PRICE = (By.XPATH, "//span[contains(@class, 'property-price')]")
    PROPERTY_LOCATION = (By.XPATH, "//span[contains(@class, 'property-location')]")
    PROPERTY_DESCRIPTION = (By.XPATH, "//div[contains(@class, 'property-description')]")
    
    # Property details
    BEDROOMS_COUNT = (By.XPATH, "//span[contains(@class, 'bedrooms')]")
    BATHROOMS_COUNT = (By.XPATH, "//span[contains(@class, 'bathrooms')]")
    SQFT_SIZE = (By.XPATH, "//span[contains(@class, 'sqft')]")
    PARKING_COUNT = (By.XPATH, "//span[contains(@class, 'parking')]")
    PROPERTY_TYPE = (By.XPATH, "//span[contains(@class, 'property-type')]")
    FURNISHING_STATUS = (By.XPATH, "//span[contains(@class, 'furnishing')]")
    
    # Special badges
    ZERO_DEPOSIT_BADGE = (By.XPATH, "//span[contains(text(), 'Zero Deposit')]")
    COOKING_READY_BADGE = (By.XPATH, "//span[contains(text(), 'Cooking Ready')]")
    HOT_PROPERTY_BADGE = (By.XPATH, "//span[contains(text(), 'Hot Property')]")
    
    # Images and gallery
    MAIN_IMAGE = (By.XPATH, "//img[contains(@class, 'main-property-image')]")
    GALLERY_IMAGES = (By.XPATH, "//div[contains(@class, 'gallery-image')]")
    IMAGE_LIGHTBOX = (By.XPATH, "//div[contains(@class, 'lightbox')]")
    LIGHTBOX_CLOSE = (By.XPATH, "//button[contains(@class, 'lightbox-close')]")
    
    # Amenities
    AMENITIES_LIST = (By.XPATH, "//div[contains(@class, 'amenities-list')]")
    AMENITY_ITEMS = (By.XPATH, "//span[contains(@class, 'amenity-item')]")
    
    # Action buttons
    SCHEDULE_VIEWING_BUTTON = (By.XPATH, "//button[contains(text(), 'Schedule Viewing')]")
    VIEWING_REQUESTED_BUTTON = (By.XPATH, "//button[contains(text(), '✓ Viewing Requested')]")
    APPLY_NOW_BUTTON = (By.XPATH, "//button[contains(text(), 'Apply Now')]")
    APPLIED_BUTTON = (By.XPATH, "//button[contains(text(), '✓ You have applied')]")
    FAVORITE_BUTTON = (By.XPATH, "//button[contains(@class, 'favorite-btn')]")
    BACK_TO_SEARCH_LINK = (By.XPATH, "//a[contains(text(), 'Back to Search Results')]")
    
    # Booking Modal
    BOOKING_MODAL = (By.XPATH, "//div[contains(@class, 'booking-modal')]")
    BOOKING_MODAL_TITLE = (By.XPATH, "//h2[contains(text(), 'Schedule Viewing')]")
    BOOKING_CLOSE_BUTTON = (By.XPATH, "//button[contains(@class, 'close-modal')]")
    
    # Booking form fields
    BOOKING_NAME_INPUT = (By.XPATH, "//input[@name='name']")
    BOOKING_EMAIL_INPUT = (By.XPATH, "//input[@name='email']")
    BOOKING_PHONE_INPUT = (By.XPATH, "//input[@name='phone']")
    BOOKING_DATE_INPUT = (By.XPATH, "//input[@type='date']")
    BOOKING_TIME_INPUT = (By.XPATH, "//input[@type='time']")
    BOOKING_MESSAGE_TEXTAREA = (By.XPATH, "//textarea[@name='message']")
    BOOKING_OCCUPATION_INPUT = (By.XPATH, "//input[@name='occupation']")
    BOOKING_INCOME_INPUT = (By.XPATH, "//input[@name='monthly_income']")
    BOOKING_OCCUPANTS_INPUT = (By.XPATH, "//input[@name='number_of_occupants']")
    
    # Booking form buttons
    BOOKING_CANCEL_BUTTON = (By.XPATH, "//button[contains(text(), 'Cancel')]")
    BOOKING_SUBMIT_BUTTON = (By.XPATH, "//button[contains(text(), 'Book Viewing')]")
    
    # Application Modal
    APPLICATION_MODAL = (By.XPATH, "//div[contains(@class, 'application-modal')]")
    APPLICATION_MODAL_TITLE = (By.XPATH, "//h2[contains(text(), 'Apply for Property')]")
    APPLICATION_CLOSE_BUTTON = (By.XPATH, "//button[contains(@class, 'close-modal')]")
    
    # Application form fields
    APPLICATION_MESSAGE_TEXTAREA = (By.XPATH, "//textarea[@name='applicationMessage']")
    APPLICATION_CANCEL_BUTTON = (By.XPATH, "//button[contains(text(), 'Cancel')]")
    APPLICATION_SUBMIT_BUTTON = (By.XPATH, "//button[contains(text(), 'Submit Application')]")
    
    # Similar properties
    SIMILAR_PROPERTIES_SECTION = (By.XPATH, "//div[contains(@class, 'similar-properties')]")
    SIMILAR_PROPERTY_CARDS = (By.XPATH, "//div[contains(@class, 'similar-property-card')]")
    
    # Loading and error states
    LOADING_INDICATOR = (By.XPATH, "//div[contains(text(), 'Loading property...')]")
    NOT_FOUND_MESSAGE = (By.XPATH, "//div[contains(text(), 'Property not found')]")
    
    # Success and error messages
    SUCCESS_MESSAGE = (By.XPATH, "//div[contains(@class, 'success-message')]")
    ERROR_MESSAGE = (By.XPATH, "//div[contains(@class, 'error-message')]")
    
    # Form validation messages
    VALIDATION_ERRORS = (By.XPATH, "//div[contains(@class, 'validation-error')]")
    REQUIRED_FIELD_ERROR = (By.XPATH, "//span[contains(text(), 'This field is required')]")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def wait_for_property_to_load(self):
        """Wait for property details to load"""
        self.wait.until(EC.visibility_of_element_located(self.PROPERTY_TITLE))
        return self
    
    def get_property_title(self):
        """Get property title"""
        return self.get_element_text(self.PROPERTY_TITLE)
    
    def get_property_price(self):
        """Get property price"""
        return self.get_element_text(self.PROPERTY_PRICE)
    
    def get_property_location(self):
        """Get property location"""
        return self.get_element_text(self.PROPERTY_LOCATION)
    
    def get_property_description(self):
        """Get property description"""
        return self.get_element_text(self.PROPERTY_DESCRIPTION)
    
    def get_property_details(self):
        """Get all property details"""
        return {
            'title': self.get_property_title(),
            'price': self.get_property_price(),
            'location': self.get_property_location(),
            'bedrooms': self.get_element_text(self.BEDROOMS_COUNT),
            'bathrooms': self.get_element_text(self.BATHROOMS_COUNT),
            'sqft': self.get_element_text(self.SQFT_SIZE),
            'parking': self.get_element_text(self.PARKING_COUNT),
            'type': self.get_element_text(self.PROPERTY_TYPE),
            'furnishing': self.get_element_text(self.FURNISHING_STATUS)
        }
    
    def get_amenities(self):
        """Get list of amenities"""
        amenity_elements = self.find_elements(self.AMENITY_ITEMS)
        return [amenity.text for amenity in amenity_elements]
    
    def has_zero_deposit(self):
        """Check if property has zero deposit"""
        return self.is_element_visible(self.ZERO_DEPOSIT_BADGE)
    
    def has_cooking_ready(self):
        """Check if property is cooking ready"""
        return self.is_element_visible(self.COOKING_READY_BADGE)
    
    def is_hot_property(self):
        """Check if property is marked as hot"""
        return self.is_element_visible(self.HOT_PROPERTY_BADGE)
    
    def click_main_image(self):
        """Click main property image to open lightbox"""
        self.click_element(self.MAIN_IMAGE)
        self.wait.until(EC.visibility_of_element_located(self.IMAGE_LIGHTBOX))
        return self
    
    def close_lightbox(self):
        """Close image lightbox"""
        self.click_element(self.LIGHTBOX_CLOSE)
        self.wait_for_element_to_disappear(self.IMAGE_LIGHTBOX)
        return self
    
    def click_gallery_image(self, index=0):
        """Click gallery image by index"""
        images = self.find_elements(self.GALLERY_IMAGES)
        if index < len(images):
            images[index].click()
            return True
        return False
    
    def toggle_favorite(self):
        """Toggle favorite status"""
        self.click_element(self.FAVORITE_BUTTON)
        return self
    
    def click_schedule_viewing(self):
        """Click Schedule Viewing button"""
        self.click_element(self.SCHEDULE_VIEWING_BUTTON)
        self.wait.until(EC.visibility_of_element_located(self.BOOKING_MODAL))
        return self
    
    def click_apply_now(self):
        """Click Apply Now button"""
        self.click_element(self.APPLY_NOW_BUTTON)
        self.wait.until(EC.visibility_of_element_located(self.APPLICATION_MODAL))
        return self
    
    def is_viewing_requested(self):
        """Check if viewing has been requested"""
        return self.is_element_visible(self.VIEWING_REQUESTED_BUTTON)
    
    def is_already_applied(self):
        """Check if user has already applied"""
        return self.is_element_visible(self.APPLIED_BUTTON)
    
    def fill_booking_form(self, booking_data):
        """Fill booking form with data"""
        self.send_keys_to_element(self.BOOKING_NAME_INPUT, booking_data['name'])
        self.send_keys_to_element(self.BOOKING_EMAIL_INPUT, booking_data['email'])
        self.send_keys_to_element(self.BOOKING_PHONE_INPUT, booking_data['phone'])
        self.send_keys_to_element(self.BOOKING_DATE_INPUT, booking_data['date'])
        self.send_keys_to_element(self.BOOKING_TIME_INPUT, booking_data['time'])
        
        if 'message' in booking_data:
            self.send_keys_to_element(self.BOOKING_MESSAGE_TEXTAREA, booking_data['message'])
        
        if 'occupation' in booking_data:
            self.send_keys_to_element(self.BOOKING_OCCUPATION_INPUT, booking_data['occupation'])
        
        if 'monthly_income' in booking_data:
            self.send_keys_to_element(self.BOOKING_INCOME_INPUT, booking_data['monthly_income'])
        
        if 'number_of_occupants' in booking_data:
            self.send_keys_to_element(self.BOOKING_OCCUPANTS_INPUT, booking_data['number_of_occupants'])
        
        return self
    
    def submit_booking(self):
        """Submit booking form"""
        self.click_element(self.BOOKING_SUBMIT_BUTTON)
        # Wait for modal to close or success message
        try:
            self.wait_for_element_to_disappear(self.BOOKING_MODAL, timeout=10)
            return True
        except:
            return False
    
    def cancel_booking(self):
        """Cancel booking form"""
        self.click_element(self.BOOKING_CANCEL_BUTTON)
        self.wait_for_element_to_disappear(self.BOOKING_MODAL)
        return self
    
    def close_booking_modal(self):
        """Close booking modal"""
        self.click_element(self.BOOKING_CLOSE_BUTTON)
        self.wait_for_element_to_disappear(self.BOOKING_MODAL)
        return self
    
    def schedule_viewing(self, booking_data):
        """Complete viewing scheduling process"""
        self.click_schedule_viewing()
        self.fill_booking_form(booking_data)
        return self.submit_booking()
    
    def fill_application_form(self, application_data):
        """Fill application form with data"""
        self.send_keys_to_element(self.APPLICATION_MESSAGE_TEXTAREA, application_data['message'])
        return self
    
    def submit_application(self):
        """Submit application form"""
        self.click_element(self.APPLICATION_SUBMIT_BUTTON)
        # Wait for modal to close or success message
        try:
            self.wait_for_element_to_disappear(self.APPLICATION_MODAL, timeout=10)
            return True
        except:
            return False
    
    def cancel_application(self):
        """Cancel application form"""
        self.click_element(self.APPLICATION_CANCEL_BUTTON)
        self.wait_for_element_to_disappear(self.APPLICATION_MODAL)
        return self
    
    def close_application_modal(self):
        """Close application modal"""
        self.click_element(self.APPLICATION_CLOSE_BUTTON)
        self.wait_for_element_to_disappear(self.APPLICATION_MODAL)
        return self
    
    def apply_for_property(self, application_data):
        """Complete property application process"""
        self.click_apply_now()
        self.fill_application_form(application_data)
        return self.submit_application()
    
    def get_similar_properties(self):
        """Get similar property cards"""
        return self.find_elements(self.SIMILAR_PROPERTY_CARDS)
    
    def click_similar_property(self, index=0):
        """Click on similar property by index"""
        similar_properties = self.get_similar_properties()
        if index < len(similar_properties):
            similar_properties[index].click()
            return True
        return False
    
    def go_back_to_search(self):
        """Click back to search results link"""
        self.click_element(self.BACK_TO_SEARCH_LINK)
        return self
    
    def is_property_not_found(self):
        """Check if property not found message is displayed"""
        return self.is_element_visible(self.NOT_FOUND_MESSAGE)
    
    def is_loading(self):
        """Check if property is still loading"""
        return self.is_element_visible(self.LOADING_INDICATOR)
    
    def wait_for_booking_modal_to_open(self):
        """Wait for booking modal to open"""
        self.wait.until(EC.visibility_of_element_located(self.BOOKING_MODAL))
        return self
    
    def wait_for_application_modal_to_open(self):
        """Wait for application modal to open"""
        self.wait.until(EC.visibility_of_element_located(self.APPLICATION_MODAL))
        return self
    
    def is_booking_modal_open(self):
        """Check if booking modal is open"""
        return self.is_element_visible(self.BOOKING_MODAL)
    
    def is_application_modal_open(self):
        """Check if application modal is open"""
        return self.is_element_visible(self.APPLICATION_MODAL)
    
    def clear_booking_form(self):
        """Clear all booking form fields"""
        self.clear_element(self.BOOKING_NAME_INPUT)
        self.clear_element(self.BOOKING_EMAIL_INPUT)
        self.clear_element(self.BOOKING_PHONE_INPUT)
        self.clear_element(self.BOOKING_DATE_INPUT)
        self.clear_element(self.BOOKING_TIME_INPUT)
        self.clear_element(self.BOOKING_MESSAGE_TEXTAREA)
        
        if self.is_element_visible(self.BOOKING_OCCUPATION_INPUT):
            self.clear_element(self.BOOKING_OCCUPATION_INPUT)
        if self.is_element_visible(self.BOOKING_INCOME_INPUT):
            self.clear_element(self.BOOKING_INCOME_INPUT)
        if self.is_element_visible(self.BOOKING_OCCUPANTS_INPUT):
            self.clear_element(self.BOOKING_OCCUPANTS_INPUT)
        
        return self
    
    def clear_application_form(self):
        """Clear application form fields"""
        self.clear_element(self.APPLICATION_MESSAGE_TEXTAREA)
        return self
    
    def get_booking_form_data(self):
        """Get current booking form data"""
        return {
            'name': self.get_element_value(self.BOOKING_NAME_INPUT),
            'email': self.get_element_value(self.BOOKING_EMAIL_INPUT),
            'phone': self.get_element_value(self.BOOKING_PHONE_INPUT),
            'date': self.get_element_value(self.BOOKING_DATE_INPUT),
            'time': self.get_element_value(self.BOOKING_TIME_INPUT),
            'message': self.get_element_value(self.BOOKING_MESSAGE_TEXTAREA)
        }
    
    def get_application_form_data(self):
        """Get current application form data"""
        return {
            'message': self.get_element_value(self.APPLICATION_MESSAGE_TEXTAREA)
        }
    
    def has_validation_errors(self):
        """Check if form has validation errors"""
        return self.is_element_visible(self.VALIDATION_ERRORS)
    
    def get_validation_errors(self):
        """Get all validation error messages"""
        error_elements = self.find_elements(self.VALIDATION_ERRORS)
        return [error.text for error in error_elements]
    
    def get_success_message(self):
        """Get success message text"""
        if self.is_element_visible(self.SUCCESS_MESSAGE):
            return self.get_element_text(self.SUCCESS_MESSAGE)
        return None
    
    def get_error_message(self):
        """Get error message text"""
        if self.is_element_visible(self.ERROR_MESSAGE):
            return self.get_element_text(self.ERROR_MESSAGE)
        return None
    
    def is_favorite_active(self):
        """Check if property is favorited"""
        favorite_btn = self.find_element(self.FAVORITE_BUTTON)
        return 'active' in favorite_btn.get_attribute('class')
    
    def get_gallery_image_count(self):
        """Get number of gallery images"""
        return len(self.find_elements(self.GALLERY_IMAGES))
    
    def view_all_gallery_images(self):
        """Click through all gallery images"""
        images = self.find_elements(self.GALLERY_IMAGES)
        for i, image in enumerate(images):
            image.click()
            time.sleep(1)  # Brief pause between clicks
        return self
    
    def has_similar_properties(self):
        """Check if similar properties section exists"""
        return self.is_element_visible(self.SIMILAR_PROPERTIES_SECTION)
    
    def get_similar_properties_count(self):
        """Get number of similar properties"""
        return len(self.get_similar_properties())
    
    def scroll_to_similar_properties(self):
        """Scroll to similar properties section"""
        if self.has_similar_properties():
            self.scroll_to_element(self.SIMILAR_PROPERTIES_SECTION)
        return self
    
    def scroll_to_booking_section(self):
        """Scroll to booking buttons section"""
        self.scroll_to_element(self.SCHEDULE_VIEWING_BUTTON)
        return self
    
    def scroll_to_amenities(self):
        """Scroll to amenities section"""
        if self.is_element_visible(self.AMENITIES_LIST):
            self.scroll_to_element(self.AMENITIES_LIST)
        return self
    
    def get_property_badges(self):
        """Get all property badges"""
        badges = []
        if self.has_zero_deposit():
            badges.append('Zero Deposit')
        if self.has_cooking_ready():
            badges.append('Cooking Ready')
        if self.is_hot_property():
            badges.append('Hot Property')
        return badges
    
    def wait_for_page_to_load_completely(self):
        """Wait for entire property page to load"""
        self.wait_for_property_to_load()
        # Wait for images to load
        self.wait.until(EC.presence_of_element_located(self.MAIN_IMAGE))
        # Wait for action buttons to be clickable
        self.wait.until(EC.element_to_be_clickable(self.SCHEDULE_VIEWING_BUTTON))
        return self
    
    def is_schedule_viewing_available(self):
        """Check if schedule viewing button is available and clickable"""
        return self.is_element_visible(self.SCHEDULE_VIEWING_BUTTON) and \
               self.is_element_clickable(self.SCHEDULE_VIEWING_BUTTON)
    
    def is_apply_now_available(self):
        """Check if apply now button is available and clickable"""
        return self.is_element_visible(self.APPLY_NOW_BUTTON) and \
               self.is_element_clickable(self.APPLY_NOW_BUTTON)
    
    def get_property_status_indicators(self):
        """Get property status indicators"""
        status = {}
        status['viewing_requested'] = self.is_viewing_requested()
        status['already_applied'] = self.is_already_applied()
        status['can_schedule_viewing'] = self.is_schedule_viewing_available()
        status['can_apply'] = self.is_apply_now_available()
        status['is_favorited'] = self.is_favorite_active()
        return status
    
    def perform_quick_booking(self, name, email, phone, date, time, message=""):
        """Perform quick booking with minimal data"""
        booking_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'date': date,
            'time': time,
            'message': message
        }
        return self.schedule_viewing(booking_data)
    
    def perform_quick_application(self, message):
        """Perform quick application with message"""
        application_data = {'message': message}
        return self.apply_for_property(application_data)
    
    def validate_required_booking_fields(self):
        """Check which booking fields are required"""
        required_fields = []
        
        # Try submitting empty form to see validation
        self.click_schedule_viewing()
        self.click_element(self.BOOKING_SUBMIT_BUTTON)
        
        # Check for required field errors
        if self.has_validation_errors():
            errors = self.get_validation_errors()
            required_fields = errors
        
        # Close modal
        self.close_booking_modal()
        return required_fields
    
    def validate_required_application_fields(self):
        """Check which application fields are required"""
        required_fields = []
        
        # Try submitting empty form to see validation
        self.click_apply_now()
        self.click_element(self.APPLICATION_SUBMIT_BUTTON)
        
        # Check for required field errors
        if self.has_validation_errors():
            errors = self.get_validation_errors()
            required_fields = errors
        
        # Close modal
        self.close_application_modal()
        return required_fields
    
    def take_screenshot_of_property(self, filename="property_detail.png"):
        """Take screenshot of property detail page"""
        return self.take_screenshot(filename)
    
    def get_page_url(self):
        """Get current page URL"""
        return self.driver.current_url
    
    def refresh_page(self):
        """Refresh the property detail page"""
        self.driver.refresh()
        self.wait_for_page_to_load_completely()
        return self

