"""
LandlordDashboardPage class for landlord dashboard interactions
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
import time

class LandlordDashboardPage(BasePage):
    """Page Object Model for landlord dashboard page"""
    
    # Page title and navigation
    PAGE_TITLE = (By.XPATH, "//h1[contains(text(), 'Landlord Dashboard')]")
    
    # Tab navigation
    MY_PROPERTIES_TAB = (By.XPATH, "//button[contains(text(), 'My Properties')]")
    VIEWING_REQUESTS_TAB = (By.XPATH, "//button[contains(text(), 'Viewing Requests')]")
    APPLICATIONS_TAB = (By.XPATH, "//button[contains(text(), 'Applications')]")
    
    # My Properties section
    PROPERTIES_SECTION = (By.XPATH, "//div[contains(@class, 'properties-section')]")
    ADD_PROPERTY_BUTTON = (By.XPATH, "//button[contains(text(), 'Add New Property')]")
    PROPERTY_CARDS = (By.XPATH, "//div[contains(@class, 'property-card')]")
    PROPERTY_TABLE_ROWS = (By.XPATH, "//tbody/tr[contains(@class, 'property-row')]")
    
    # Property card/row elements
    PROPERTY_TITLE = (By.XPATH, ".//h4[contains(@class, 'property-title')]")
    PROPERTY_LOCATION = (By.XPATH, ".//span[contains(@class, 'property-location')]")
    PROPERTY_PRICE = (By.XPATH, ".//span[contains(@class, 'property-price')]")
    PROPERTY_STATUS = (By.XPATH, ".//span[contains(@class, 'property-status')]")
    PROPERTY_VIEWS = (By.XPATH, ".//span[contains(@class, 'property-views')]")
    
    # Property actions
    EDIT_PROPERTY_BUTTON = (By.XPATH, ".//button[contains(text(), 'Edit')]")
    DELETE_PROPERTY_BUTTON = (By.XPATH, ".//button[contains(text(), 'Delete')]")
    VIEW_PROPERTY_BUTTON = (By.XPATH, ".//button[contains(text(), 'View')]")
    STATUS_DROPDOWN = (By.XPATH, ".//select[contains(@class, 'status-select')]")
    
    # Add/Edit Property Modal
    PROPERTY_MODAL = (By.XPATH, "//div[contains(@class, 'property-modal')]")
    PROPERTY_MODAL_TITLE = (By.XPATH, "//h2[contains(text(), 'Add Property') or contains(text(), 'Edit Property')]")
    PROPERTY_MODAL_CLOSE = (By.XPATH, "//button[contains(@class, 'close-modal')]")
    
    # Property form fields
    PROPERTY_TITLE_INPUT = (By.XPATH, "//input[@name='title']")
    PROPERTY_LOCATION_INPUT = (By.XPATH, "//input[@name='location']")
    PROPERTY_PRICE_INPUT = (By.XPATH, "//input[@name='price']")
    PROPERTY_SQFT_INPUT = (By.XPATH, "//input[@name='sqft']")
    PROPERTY_BEDROOMS_INPUT = (By.XPATH, "//input[@name='bedrooms']")
    PROPERTY_BATHROOMS_INPUT = (By.XPATH, "//input[@name='bathrooms']")
    PROPERTY_PARKING_INPUT = (By.XPATH, "//input[@name='parking']")
    PROPERTY_TYPE_SELECT = (By.XPATH, "//select[@name='propertyType']")
    PROPERTY_FURNISHING_SELECT = (By.XPATH, "//select[@name='furnished']")
    PROPERTY_DESCRIPTION_TEXTAREA = (By.XPATH, "//textarea[@name='description']")
    
    # Property form checkboxes
    ZERO_DEPOSIT_CHECKBOX = (By.XPATH, "//input[@name='zeroDeposit']")
    COOKING_READY_CHECKBOX = (By.XPATH, "//input[@name='cookingReady']")
    HOT_PROPERTY_CHECKBOX = (By.XPATH, "//input[@name='hotProperty']")
    
    # Property form buttons
    SAVE_PROPERTY_BUTTON = (By.XPATH, "//button[contains(text(), 'Save Property')]")
    CANCEL_PROPERTY_BUTTON = (By.XPATH, "//button[contains(text(), 'Cancel')]")
    
    # Viewing Requests section
    VIEWING_REQUESTS_SECTION = (By.XPATH, "//div[contains(@class, 'viewing-requests')]")
    VIEWING_REQUEST_ROWS = (By.XPATH, "//tbody/tr[contains(@class, 'viewing-request-row')]")
    
    # Viewing request elements
    REQUEST_PROPERTY_NAME = (By.XPATH, ".//td[1]")
    REQUEST_TENANT_NAME = (By.XPATH, ".//td[2]")
    REQUEST_DATE_TIME = (By.XPATH, ".//td[3]")
    REQUEST_STATUS_CELL = (By.XPATH, ".//td[4]")
    REQUEST_ACTIONS_CELL = (By.XPATH, ".//td[5]")
    
    # Viewing request actions
    VIEW_DETAILS_BUTTON = (By.XPATH, ".//button[contains(text(), 'View Details')]")
    CONFIRM_REQUEST_BUTTON = (By.XPATH, ".//button[contains(text(), 'Confirm')]")
    DECLINE_REQUEST_BUTTON = (By.XPATH, ".//button[contains(text(), 'Decline')]")
    RESCHEDULE_REQUEST_BUTTON = (By.XPATH, ".//button[contains(text(), 'Reschedule')]")
    CANCEL_RESCHEDULE_BUTTON = (By.XPATH, ".//button[contains(text(), 'Cancel Request')]")
    
    # Expandable details section
    EXPANDABLE_DETAILS = (By.XPATH, "//tr[contains(@class, 'bg-gray-50')]")
    TENANT_CONTACT_INFO = (By.XPATH, ".//div[contains(text(), 'Contact Information')]")
    TENANT_NAME_DETAIL = (By.XPATH, ".//div[contains(text(), 'Name:')]")
    TENANT_EMAIL_DETAIL = (By.XPATH, ".//div[contains(text(), 'Email:')]")
    TENANT_PHONE_DETAIL = (By.XPATH, ".//div[contains(text(), 'Phone:')]")
    TENANT_MESSAGE_DETAIL = (By.XPATH, ".//div[contains(@class, 'bg-gray-50')]")
    
    # Reschedule modal
    RESCHEDULE_MODAL = (By.XPATH, "//div[contains(@class, 'reschedule-modal')]")
    RESCHEDULE_DATE_INPUT = (By.XPATH, "//input[@name='proposedDate']")
    RESCHEDULE_TIME_INPUT = (By.XPATH, "//input[@name='proposedTime']")
    RESCHEDULE_SUBMIT_BUTTON = (By.XPATH, "//button[contains(text(), 'Propose Reschedule')]")
    RESCHEDULE_CANCEL_BUTTON = (By.XPATH, "//button[contains(text(), 'Cancel')]")
    
    # Applications section
    APPLICATIONS_SECTION = (By.XPATH, "//div[contains(@class, 'applications')]")
    APPLICATION_ROWS = (By.XPATH, "//tbody/tr[contains(@class, 'application-row')]")
    
    # Application elements
    APP_PROPERTY_NAME = (By.XPATH, ".//td[1]")
    APP_TENANT_NAME = (By.XPATH, ".//td[2]")
    APP_SUBMISSION_DATE = (By.XPATH, ".//td[3]")
    APP_STATUS_CELL = (By.XPATH, ".//td[4]")
    APP_ACTIONS_CELL = (By.XPATH, ".//td[5]")
    
    # Application actions
    APPROVE_APPLICATION_BUTTON = (By.XPATH, ".//button[contains(text(), 'Approve')]")
    REJECT_APPLICATION_BUTTON = (By.XPATH, ".//button[contains(text(), 'Reject')]")
    VIEW_APPLICATION_BUTTON = (By.XPATH, ".//button[contains(text(), 'View')]")
    
    # Success/Error messages
    SUCCESS_MESSAGE = (By.XPATH, "//div[contains(@class, 'success-message')]")
    ERROR_MESSAGE = (By.XPATH, "//div[contains(@class, 'error-message')]")
    
    # Empty states
    NO_PROPERTIES_MESSAGE = (By.XPATH, "//div[contains(text(), 'No properties')]")
    NO_VIEWING_REQUESTS_MESSAGE = (By.XPATH, "//div[contains(text(), 'No viewing requests')]")
    NO_APPLICATIONS_MESSAGE = (By.XPATH, "//div[contains(text(), 'No applications')]")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def wait_for_dashboard_to_load(self):
        """Wait for dashboard to load"""
        self.wait.until(EC.visibility_of_element_located(self.PAGE_TITLE))
        return self
    
    def click_my_properties_tab(self):
        """Click My Properties tab"""
        self.click_element(self.MY_PROPERTIES_TAB)
        return self
    
    def click_viewing_requests_tab(self):
        """Click Viewing Requests tab"""
        self.click_element(self.VIEWING_REQUESTS_TAB)
        return self
    
    def click_applications_tab(self):
        """Click Applications tab"""
        self.click_element(self.APPLICATIONS_TAB)
        return self
    
    def click_add_property(self):
        """Click Add New Property button"""
        self.click_element(self.ADD_PROPERTY_BUTTON)
        self.wait.until(EC.visibility_of_element_located(self.PROPERTY_MODAL))
        return self
    
    def get_properties(self):
        """Get all property cards/rows"""
        # Try table rows first, then cards
        try:
            return self.find_elements(self.PROPERTY_TABLE_ROWS)
        except:
            return self.find_elements(self.PROPERTY_CARDS)
    
    def get_property_count(self):
        """Get number of properties"""
        return len(self.get_properties())
    
    def get_property_details(self, index=0):
        """Get property details by index"""
        properties = self.get_properties()
        if index < len(properties):
            property_element = properties[index]
            return {
                'title': property_element.find_element(*self.PROPERTY_TITLE).text,
                'location': property_element.find_element(*self.PROPERTY_LOCATION).text,
                'price': property_element.find_element(*self.PROPERTY_PRICE).text,
                'status': property_element.find_element(*self.PROPERTY_STATUS).text
            }
        return None
    
    def edit_property(self, index, property_data):
        """Edit property by index"""
        properties = self.get_properties()
        if index < len(properties):
            property_element = properties[index]
            edit_btn = property_element.find_element(*self.EDIT_PROPERTY_BUTTON)
            edit_btn.click()
            
            self.wait.until(EC.visibility_of_element_located(self.PROPERTY_MODAL))
            self.fill_property_form(property_data)
            self.save_property()
            return True
        return False
    
    def delete_property(self, index):
        """Delete property by index"""
        properties = self.get_properties()
        if index < len(properties):
            property_element = properties[index]
            delete_btn = property_element.find_element(*self.DELETE_PROPERTY_BUTTON)
            delete_btn.click()
            
            # Handle confirmation dialog
            try:
                self.accept_alert()
                return True
            except:
                return False
        return False
    
    def change_property_status(self, index, new_status):
        """Change property status by index"""
        properties = self.get_properties()
        if index < len(properties):
            property_element = properties[index]
            status_dropdown = property_element.find_element(*self.STATUS_DROPDOWN)
            self.select_dropdown_by_text((By.XPATH, "."), new_status)
            return True
        return False
    
    def fill_property_form(self, property_data):
        """Fill property form with data"""
        if 'title' in property_data:
            self.send_keys_to_element(self.PROPERTY_TITLE_INPUT, property_data['title'])
        
        if 'location' in property_data:
            self.send_keys_to_element(self.PROPERTY_LOCATION_INPUT, property_data['location'])
        
        if 'price' in property_data:
            self.send_keys_to_element(self.PROPERTY_PRICE_INPUT, str(property_data['price']))
        
        if 'sqft' in property_data:
            self.send_keys_to_element(self.PROPERTY_SQFT_INPUT, str(property_data['sqft']))
        
        if 'bedrooms' in property_data:
            self.send_keys_to_element(self.PROPERTY_BEDROOMS_INPUT, str(property_data['bedrooms']))
        
        if 'bathrooms' in property_data:
            self.send_keys_to_element(self.PROPERTY_BATHROOMS_INPUT, str(property_data['bathrooms']))
        
        if 'parking' in property_data:
            self.send_keys_to_element(self.PROPERTY_PARKING_INPUT, str(property_data['parking']))
        
        if 'property_type' in property_data:
            self.select_dropdown_by_text(self.PROPERTY_TYPE_SELECT, property_data['property_type'])
        
        if 'furnishing' in property_data:
            self.select_dropdown_by_text(self.PROPERTY_FURNISHING_SELECT, property_data['furnishing'])
        
        if 'description' in property_data:
            self.send_keys_to_element(self.PROPERTY_DESCRIPTION_TEXTAREA, property_data['description'])
        
        # Handle checkboxes
        if property_data.get('zero_deposit', False):
            checkbox = self.find_element(self.ZERO_DEPOSIT_CHECKBOX)
            if not checkbox.is_selected():
                checkbox.click()
        
        if property_data.get('cooking_ready', False):
            checkbox = self.find_element(self.COOKING_READY_CHECKBOX)
            if not checkbox.is_selected():
                checkbox.click()
        
        if property_data.get('hot_property', False):
            checkbox = self.find_element(self.HOT_PROPERTY_CHECKBOX)
            if not checkbox.is_selected():
                checkbox.click()
        
        return self
    
    def save_property(self):
        """Save property form"""
        self.click_element(self.SAVE_PROPERTY_BUTTON)
        self.wait_for_element_to_disappear(self.PROPERTY_MODAL)
        return self
    
    def cancel_property_form(self):
        """Cancel property form"""
        self.click_element(self.CANCEL_PROPERTY_BUTTON)
        self.wait_for_element_to_disappear(self.PROPERTY_MODAL)
        return self
    
    def close_property_modal(self):
        """Close property modal"""
        self.click_element(self.PROPERTY_MODAL_CLOSE)
        self.wait_for_element_to_disappear(self.PROPERTY_MODAL)
        return self
    
    def add_property(self, property_data):
        """Add new property"""
        self.click_add_property()
        self.fill_property_form(property_data)
        self.save_property()
        return self
    
    def get_viewing_requests(self):
        """Get all viewing request rows"""
        return self.find_elements(self.VIEWING_REQUEST_ROWS)
    
    def get_viewing_request_count(self):
        """Get number of viewing requests"""
        return len(self.get_viewing_requests())
    
    def get_viewing_request_details(self, index=0):
        """Get viewing request details by index"""
        requests = self.get_viewing_requests()
        if index < len(requests):
            request = requests[index]
            return {
                'property_name': request.find_element(*self.REQUEST_PROPERTY_NAME).text,
                'tenant_name': request.find_element(*self.REQUEST_TENANT_NAME).text,
                'date_time': request.find_element(*self.REQUEST_DATE_TIME).text,
                'status': request.find_element(*self.REQUEST_STATUS_CELL).text
            }
        return None
    
    def view_request_details(self, index):
        """View detailed information for viewing request"""
        requests = self.get_viewing_requests()
        if index < len(requests):
            request = requests[index]
            view_details_btn = request.find_element(*self.VIEW_DETAILS_BUTTON)
            view_details_btn.click()
            
            # Wait for expandable details to appear
            time.sleep(1)
            return True
        return False
    
    def confirm_viewing_request(self, index):
        """Confirm viewing request by index"""
        requests = self.get_viewing_requests()
        if index < len(requests):
            request = requests[index]
            confirm_btn = request.find_element(*self.CONFIRM_REQUEST_BUTTON)
            confirm_btn.click()
            return True
        return False
    
    def decline_viewing_request(self, index):
        """Decline viewing request by index"""
        requests = self.get_viewing_requests()
        if index < len(requests):
            request = requests[index]
            decline_btn = request.find_element(*self.DECLINE_REQUEST_BUTTON)
            decline_btn.click()
            return True
        return False
    
    def reschedule_viewing_request(self, index, new_date, new_time):
        """Reschedule viewing request by index"""
        requests = self.get_viewing_requests()
        if index < len(requests):
            request = requests[index]
            reschedule_btn = request.find_element(*self.RESCHEDULE_REQUEST_BUTTON)
            reschedule_btn.click()
            
            self.wait.until(EC.visibility_of_element_located(self.RESCHEDULE_MODAL))
            self.send_keys_to_element(self.RESCHEDULE_DATE_INPUT, new_date)
            self.send_keys_to_element(self.RESCHEDULE_TIME_INPUT, new_time)
            self.click_element(self.RESCHEDULE_SUBMIT_BUTTON)
            
            self.wait_for_element_to_disappear(self.RESCHEDULE_MODAL)
            return True
        return False
    
    def cancel_reschedule_request(self, index):
        """Cancel reschedule request by index"""
        requests = self.get_viewing_requests()
        if index < len(requests):
            request = requests[index]
            if self.is_element_present(self.CANCEL_RESCHEDULE_BUTTON):
                cancel_btn = request.find_element(*self.CANCEL_RESCHEDULE_BUTTON)
                cancel_btn.click()
                return True
        return False
    
    def get_tenant_details_from_expanded_view(self):
        """Get tenant details from expanded view"""
        if self.is_element_visible(self.EXPANDABLE_DETAILS):
            details_section = self.find_element(self.EXPANDABLE_DETAILS)
            
            # Extract tenant information
            tenant_info = {}
            
            try:
                name_element = details_section.find_element(*self.TENANT_NAME_DETAIL)
                tenant_info['name'] = name_element.text.split(':', 1)[1].strip()
            except:
                pass
            
            try:
                email_element = details_section.find_element(*self.TENANT_EMAIL_DETAIL)
                tenant_info['email'] = email_element.text.split(':', 1)[1].strip()
            except:
                pass
            
            try:
                phone_element = details_section.find_element(*self.TENANT_PHONE_DETAIL)
                tenant_info['phone'] = phone_element.text.split(':', 1)[1].strip()
            except:
                pass
            
            return tenant_info
        return None
    
    def get_applications(self):
        """Get all application rows"""
        return self.find_elements(self.APPLICATION_ROWS)
    
    def get_application_count(self):
        """Get number of applications"""
        return len(self.get_applications())
    
    def get_application_details(self, index=0):
        """Get application details by index"""
        applications = self.get_applications()
        if index < len(applications):
            application = applications[index]
            return {
                'property_name': application.find_element(*self.APP_PROPERTY_NAME).text,
                'tenant_name': application.find_element(*self.APP_TENANT_NAME).text,
                'submission_date': application.find_element(*self.APP_SUBMISSION_DATE).text,
                'status': application.find_element(*self.APP_STATUS_CELL).text
            }
        return None
    
    def approve_application(self, index):
        """Approve application by index"""
        applications = self.get_applications()
        if index < len(applications):
            application = applications[index]
            approve_btn = application.find_element(*self.APPROVE_APPLICATION_BUTTON)
            approve_btn.click()
            return True
        return False
    
    def reject_application(self, index):
        """Reject application by index"""
        applications = self.get_applications()
        if index < len(applications):
            application = applications[index]
            reject_btn = application.find_element(*self.REJECT_APPLICATION_BUTTON)
            reject_btn.click()
            return True
        return False
    
    def view_application(self, index):
        """View application details by index"""
        applications = self.get_applications()
        if index < len(applications):
            application = applications[index]
            view_btn = application.find_element(*self.VIEW_APPLICATION_BUTTON)
            view_btn.click()
            return True
        return False
    
    def has_properties(self):
        """Check if landlord has properties"""
        return not self.is_element_visible(self.NO_PROPERTIES_MESSAGE)
    
    def has_viewing_requests(self):
        """Check if there are viewing requests"""
        return not self.is_element_visible(self.NO_VIEWING_REQUESTS_MESSAGE)
    
    def has_applications(self):
        """Check if there are applications"""
        return not self.is_element_visible(self.NO_APPLICATIONS_MESSAGE)
    
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

