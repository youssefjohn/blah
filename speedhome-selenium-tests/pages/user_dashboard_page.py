"""
UserDashboardPage class for tenant dashboard interactions
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
import time

class UserDashboardPage(BasePage):
    """Page Object Model for tenant dashboard page"""
    
    # Page title and navigation
    PAGE_TITLE = (By.XPATH, "//h1[contains(text(), 'My Dashboard')]")
    
    # Profile section
    PROFILE_SECTION = (By.XPATH, "//div[contains(@class, 'profile-section')]")
    PROFILE_PICTURE = (By.XPATH, "//img[contains(@class, 'profile-picture')]")
    USER_NAME = (By.XPATH, "//h2[contains(@class, 'user-name')]")
    USER_EMAIL = (By.XPATH, "//span[contains(@class, 'user-email')]")
    EDIT_PROFILE_BUTTON = (By.XPATH, "//button[contains(text(), 'Edit Profile')]")
    SAVE_PROFILE_BUTTON = (By.XPATH, "//button[contains(text(), 'Save Profile')]")
    CANCEL_EDIT_BUTTON = (By.XPATH, "//button[contains(text(), 'Cancel')]")
    
    # Profile form fields
    FIRST_NAME_INPUT = (By.XPATH, "//input[@name='first_name']")
    LAST_NAME_INPUT = (By.XPATH, "//input[@name='last_name']")
    PHONE_INPUT = (By.XPATH, "//input[@name='phone']")
    BIO_TEXTAREA = (By.XPATH, "//textarea[@name='bio']")
    OCCUPATION_INPUT = (By.XPATH, "//input[@name='occupation']")
    COMPANY_INPUT = (By.XPATH, "//input[@name='company_name']")
    PROFILE_PICTURE_INPUT = (By.XPATH, "//input[@type='file']")
    
    # Viewing Requests section
    VIEWING_REQUESTS_SECTION = (By.XPATH, "//h2[normalize-space()='My Viewing Appointments']")
    VIEWING_REQUESTS_TITLE = (By.XPATH, "//h2[normalize-space()='My Viewing Appointments']")
    VIEWING_REQUEST_CARDS = (By.XPATH, "//h2[normalize-space()='My Viewing Appointments']/following-sibling::div/div")
    
    # Viewing request card elements
    REQUEST_PROPERTY_TITLE = (By.XPATH, "(//h3)[1]")
    REQUEST_PROPERTY_LOCATION = (By.XPATH, ".//span[contains(@class, 'property-location')]")
    REQUEST_DATE = (By.XPATH, "(//h3)[1]/following-sibling::div/div/div")
    REQUEST_TIME = (By.XPATH, "(//h3)[1]/following-sibling::div/div/div/following-sibling::div")
    REQUEST_STATUS = (By.XPATH, "//div[@class='space-y-4']/div[1]/div[1]/div[2]/span[1]")
    
    # Viewing request actions
    RESCHEDULE_BUTTON = (By.XPATH, ".//button[contains(text(), 'Reschedule')]")
    CANCEL_REQUEST_BUTTON = (By.XPATH, ".//button[contains(text(), 'Cancel')]")
    CANCEL_RESCHEDULE_BUTTON = (By.XPATH, ".//button[contains(text(), 'Cancel Request')]")
    
    # Reschedule modal
    RESCHEDULE_MODAL = (By.XPATH, "//div[contains(@class, 'reschedule-modal')]")
    RESCHEDULE_DATE_INPUT = (By.XPATH, "//input[@name='newDate']")
    RESCHEDULE_TIME_INPUT = (By.XPATH, "//input[@name='newTime']")
    RESCHEDULE_SUBMIT_BUTTON = (By.XPATH, "//button[contains(text(), 'Request Reschedule')]")
    RESCHEDULE_CANCEL_BUTTON = (By.XPATH, "//button[contains(text(), 'Cancel')]")
    RESCHEDULE_CLOSE_BUTTON = (By.XPATH, "//button[contains(@class, 'close-modal')]")
    
    # Applications section
    APPLICATIONS_SECTION = (By.XPATH, "//h2[contains(text(), 'My Rental Applications')]")
    APPLICATIONS_TITLE = (By.XPATH, "//h2[contains(text(), 'My Rental Applications')]")
    APPLICATION_CARDS = (By.XPATH, "//h2[contains(text(), 'My Rental Applications')]/following-sibling::div/div")
    
    # Application card elements
    APP_PROPERTY_TITLE = (By.XPATH, "(//h3)[1]")
    APP_PROPERTY_LOCATION = (By.XPATH, ".//span[contains(@class, 'property-location')]")
    APP_SUBMISSION_DATE = (By.XPATH, "(//h3)[1]/following-sibling::div/span[1]")
    APP_STATUS = (By.XPATH, "//div[@class='space-y-4']/div/div/div/following-sibling::div//span")
    
    # Favorites section
    FAVORITES_SECTION = (By.XPATH, "//div[contains(@class, 'favorites')]")
    FAVORITES_TITLE = (By.XPATH, "//h3[contains(text(), 'My Favorites')]")
    FAVORITE_CARDS = (By.XPATH, "//div[contains(@class, 'favorite-card')]")
    
    # Favorite card elements
    FAV_PROPERTY_TITLE = (By.XPATH, ".//h4[contains(@class, 'property-title')]")
    FAV_PROPERTY_LOCATION = (By.XPATH, ".//span[contains(@class, 'property-location')]")
    FAV_PROPERTY_PRICE = (By.XPATH, ".//span[contains(@class, 'property-price')]")
    REMOVE_FAVORITE_BUTTON = (By.XPATH, ".//button[contains(text(), 'Remove')]")
    VIEW_PROPERTY_BUTTON = (By.XPATH, ".//button[contains(text(), 'View Property')]")
    
    # Empty states
    NO_VIEWING_REQUESTS = (By.XPATH, "//p[normalize-space()='No viewing appointments yet']")
    NO_APPLICATIONS = (By.XPATH, "//p[contains(text(), 'No applications submitted yet')]")
    NO_FAVORITES = (By.XPATH, "//div[contains(text(), 'No favorites')]")
    
    # Success/Error messages
    SUCCESS_MESSAGE = (By.XPATH, "//div[contains(@class, 'success-message')]")
    ERROR_MESSAGE = (By.XPATH, "//div[contains(@class, 'error-message')]")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def wait_for_dashboard_to_load(self):
        """Wait for dashboard to load"""
        self.wait.until(EC.visibility_of_element_located(self.PAGE_TITLE))
        return self
    
    def get_user_name(self):
        """Get displayed user name"""
        return self.get_element_text(self.USER_NAME)
    
    def get_user_email(self):
        """Get displayed user email"""
        return self.get_element_text(self.USER_EMAIL)
    
    def click_edit_profile(self):
        """Click edit profile button"""
        self.click_element(self.EDIT_PROFILE_BUTTON)
        return self
    
    def update_profile(self, profile_data):
        """Update profile information"""
        self.click_edit_profile()
        
        if 'first_name' in profile_data:
            self.send_keys_to_element(self.FIRST_NAME_INPUT, profile_data['first_name'])
        
        if 'last_name' in profile_data:
            self.send_keys_to_element(self.LAST_NAME_INPUT, profile_data['last_name'])
        
        if 'phone' in profile_data:
            self.send_keys_to_element(self.PHONE_INPUT, profile_data['phone'])
        
        if 'bio' in profile_data:
            self.send_keys_to_element(self.BIO_TEXTAREA, profile_data['bio'])
        
        if 'occupation' in profile_data:
            self.send_keys_to_element(self.OCCUPATION_INPUT, profile_data['occupation'])
        
        if 'company_name' in profile_data:
            self.send_keys_to_element(self.COMPANY_INPUT, profile_data['company_name'])
        
        self.click_element(self.SAVE_PROFILE_BUTTON)
        return self
    
    def cancel_profile_edit(self):
        """Cancel profile editing"""
        self.click_element(self.CANCEL_EDIT_BUTTON)
        return self
    
    def upload_profile_picture(self, file_path):
        """Upload profile picture"""
        self.upload_file(self.PROFILE_PICTURE_INPUT, file_path)
        return self
    
    def get_viewing_requests(self):
        """Get all viewing request cards"""
        return self.find_elements(self.VIEWING_REQUEST_CARDS)
    
    def get_viewing_request_count(self):
        """Get number of viewing requests"""
        return len(self.get_viewing_requests())
    
    def get_viewing_request_details(self, index=0):
        """Get viewing request details by index"""
        requests = self.get_viewing_requests()
        if index < len(requests):
            request = requests[index]
            return {
                'property_title': request.find_element(*self.REQUEST_PROPERTY_TITLE).text,
                # 'property_location': request.find_element(*self.REQUEST_PROPERTY_LOCATION).text,
                'date': request.find_element(*self.REQUEST_DATE).text,
                'time': request.find_element(*self.REQUEST_TIME).text,
                'status': request.find_element(*self.REQUEST_STATUS).text
            }
        return None
    
    def reschedule_viewing_request(self, index, new_date, new_time):
        """Reschedule viewing request by index"""
        requests = self.get_viewing_requests()
        if index < len(requests):
            request = requests[index]
            reschedule_btn = request.find_element(*self.RESCHEDULE_BUTTON)
            reschedule_btn.click()
            
            self.wait.until(EC.visibility_of_element_located(self.RESCHEDULE_MODAL))
            self.send_keys_to_element(self.RESCHEDULE_DATE_INPUT, new_date)
            self.send_keys_to_element(self.RESCHEDULE_TIME_INPUT, new_time)
            self.click_element(self.RESCHEDULE_SUBMIT_BUTTON)
            
            # Wait for modal to close
            self.wait_for_element_to_disappear(self.RESCHEDULE_MODAL)
            return True
        return False
    
    def cancel_viewing_request(self, index):
        """Cancel viewing request by index"""
        requests = self.get_viewing_requests()
        if index < len(requests):
            request = requests[index]
            cancel_btn = request.find_element(*self.CANCEL_REQUEST_BUTTON)
            cancel_btn.click()
            
            # Handle confirmation if needed
            try:
                self.accept_alert()
            except:
                pass
            
            return True
        return False
    
    def cancel_reschedule_request(self, index):
        """Cancel reschedule request by index"""
        requests = self.get_viewing_requests()
        if index < len(requests):
            request = requests[index]
            if self.is_element_present(self.CANCEL_RESCHEDULE_BUTTON):
                cancel_reschedule_btn = request.find_element(*self.CANCEL_RESCHEDULE_BUTTON)
                cancel_reschedule_btn.click()
                return True
        return False
    
    def close_reschedule_modal(self):
        """Close reschedule modal"""
        self.click_element(self.RESCHEDULE_CLOSE_BUTTON)
        self.wait_for_element_to_disappear(self.RESCHEDULE_MODAL)
        return self
    
    def get_applications(self):
        """Get all application cards"""
        return self.find_elements(self.APPLICATION_CARDS)
    
    def get_application_count(self):
        """Get number of applications"""
        return len(self.get_applications())
    
    def get_application_details(self, index=0):
        """Get application details by index"""
        applications = self.get_applications()
        if index < len(applications):
            application = applications[index]
            return {
                'property_title': application.find_element(*self.APP_PROPERTY_TITLE).text,
                # 'property_location': application.find_element(*self.APP_PROPERTY_LOCATION).text,
                'submission_date': application.find_element(*self.APP_SUBMISSION_DATE).text,
                'status': application.find_element(*self.APP_STATUS).text
            }
        return None
    
    def get_favorites(self):
        """Get all favorite cards"""
        return self.find_elements(self.FAVORITE_CARDS)
    
    def get_favorites_count(self):
        """Get number of favorites"""
        return len(self.get_favorites())
    
    def get_favorite_details(self, index=0):
        """Get favorite details by index"""
        favorites = self.get_favorites()
        if index < len(favorites):
            favorite = favorites[index]
            return {
                'property_title': favorite.find_element(*self.FAV_PROPERTY_TITLE).text,
                'property_location': favorite.find_element(*self.FAV_PROPERTY_LOCATION).text,
                'property_price': favorite.find_element(*self.FAV_PROPERTY_PRICE).text
            }
        return None
    
    def remove_favorite(self, index):
        """Remove favorite by index"""
        favorites = self.get_favorites()
        if index < len(favorites):
            favorite = favorites[index]
            remove_btn = favorite.find_element(*self.REMOVE_FAVORITE_BUTTON)
            remove_btn.click()
            return True
        return False
    
    def view_favorite_property(self, index):
        """View favorite property by index"""
        favorites = self.get_favorites()
        if index < len(favorites):
            favorite = favorites[index]
            view_btn = favorite.find_element(*self.VIEW_PROPERTY_BUTTON)
            view_btn.click()
            return True
        return False
    
    def has_viewing_requests(self):
        """Check if user has viewing requests"""
        return not self.is_element_visible(self.NO_VIEWING_REQUESTS)
    
    def has_applications(self):
        """Check if user has applications"""
        return not self.is_element_visible(self.NO_APPLICATIONS)
    
    def has_favorites(self):
        """Check if user has favorites"""
        return not self.is_element_visible(self.NO_FAVORITES)
    
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
    
    def scroll_to_viewing_requests(self):
        """Scroll to viewing requests section"""
        element = self.find_element(self.VIEWING_REQUESTS_SECTION)
        self.scroll_to_element(element)
        return self
    
    def scroll_to_applications(self):
        """Scroll to applications section"""
        element = self.find_element(self.APPLICATIONS_SECTION)
        self.scroll_to_element(element)
        return self
    
    def scroll_to_favorites(self):
        """Scroll to favorites section"""
        element = self.find_element(self.FAVORITES_SECTION)
        self.scroll_to_element(element)
        return self

