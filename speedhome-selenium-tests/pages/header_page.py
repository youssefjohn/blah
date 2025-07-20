"""
HeaderPage class for navigation and authentication interactions
"""
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
import time

class HeaderPage(BasePage):
    """Page Object Model for SpeedHome header navigation"""
    
    # Header elements
    LOGO = (By.CSS_SELECTOR, "a[href='/'] div")
    LANDLORD_BUTTON = (By.XPATH, "//button[contains(text(), 'Landlord')]")
    TENANT_BUTTON = (By.XPATH, "//button[contains(text(), 'Tenant')]")
    SEARCH_BAR = (By.XPATH, "//input[@placeholder='Search by property name or location...']")
    
    # Authentication buttons (when not logged in)
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")
    REGISTER_BUTTON = (By.XPATH, "//button[normalize-space()='Sign Up']")
    
    # User account dropdown (when logged in)
    USER_ACCOUNT_BUTTON = (By.XPATH, "//button[contains(text(),'👤')]")
    USER_NAME_DISPLAY = (By.XPATH, "//span[contains(@class, 'user-name')]")
    ACCOUNT_DROPDOWN = (By.XPATH, "//div[@class='relative dropdown-container']/div")
    LOGOUT_BUTTON = (By.XPATH, "//button[normalize-space()='Logout']")
    
    # Notifications
    NOTIFICATION_BELL = (By.XPATH, "//button[contains(@class, 'notification-bell')]")
    NOTIFICATION_BADGE = (By.XPATH, "//span[contains(@class, 'notification-badge')]")
    NOTIFICATION_DROPDOWN = (By.XPATH, "//div[contains(@class, 'notification-dropdown')]")
    NOTIFICATION_ITEMS = (By.XPATH, "//div[contains(@class, 'notification-item')]")
    
    # Login Modal
    LOGIN_MODAL = (By.XPATH, "//h2[contains(text(), 'Login')]")
    LOGIN_EMAIL_INPUT = (By.XPATH, "//input[@id='username']")
    LOGIN_PASSWORD_INPUT = (By.XPATH, "//input[@type='password']")
    LOGIN_SUBMIT_BUTTON = (By.XPATH, "//button[@type='submit' and contains(text(), 'Login')]")
    LOGIN_CLOSE_BUTTON = (By.XPATH, "//h2[contains(text(), 'Login')]/following-sibling::button")
    FORGOT_PASSWORD_LINK = (By.XPATH, "//a[contains(text(), 'Forgot Password')]")
    REGISTER_LINK = (By.XPATH, "//button[normalize-space()='Sign Up']")
    REMEMBER_ME_CHECKBOX = (By.XPATH, "//input[@type='checkbox']")
    
    # Register Modal
    REGISTER_MODAL = (By.XPATH, "//h2[contains(text(), 'Sign Up')]")
    REGISTER_USERNAME_INPUT = (By.XPATH, "//input[@id='username']")
    REGISTER_EMAIL_INPUT = (By.XPATH, "//input[@name='email']")
    REGISTER_PASSWORD_INPUT = (By.XPATH, "//input[@name='password']")
    REGISTER_CONFIRM_PASSWORD_INPUT = (By.XPATH, "//input[@name='confirmPassword']")
    REGISTER_FIRST_NAME_INPUT = (By.XPATH, "//input[@id='first_name']")
    REGISTER_LAST_NAME_INPUT = (By.XPATH, "//input[@id='last_name']")
    REGISTER_PHONE_INPUT = (By.XPATH, "//input[@name='phone']")
    REGISTER_TENANT_RADIO = (By.XPATH, "//input[@value='tenant']")
    REGISTER_LANDLORD_RADIO = (By.XPATH, "//input[@value='landlord']")
    REGISTER_SUBMIT_BUTTON = (By.XPATH, "//button[@type='submit' and contains(text(), 'Create Account')]")
    REGISTER_CLOSE_BUTTON = (By.XPATH, "//h2[contains(text(), 'Sign Up')]/following-sibling::button")
    LOGIN_LINK = (By.XPATH, "//a[contains(text(), 'Login')]")
    
    # Error messages
    ERROR_MESSAGE = (By.XPATH, "//div[contains(@class, 'error-message')]")
    SUCCESS_MESSAGE = (By.XPATH, "//div[contains(@class, 'success-message')]")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def click_logo(self):
        """Click on SpeedHome logo"""
        self.click_element(self.LOGO)
        return self

    def click_user_icon(self):
        try:
            element = self.find_element(self.USER_ACCOUNT_BUTTON)
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            self.driver.execute_script("arguments[0].click();", element)
        except:
            # Fallback to regular click
            self.click_element(self.LANDLORD_BUTTON)
        return self

    def click_landlord_button(self):
        """Click Landlord button with interception handling"""
        try:
            element = self.find_element(self.LANDLORD_BUTTON)
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            self.driver.execute_script("arguments[0].click();", element)
        except:
            # Fallback to regular click
            self.click_element(self.LANDLORD_BUTTON)
        return self

    def click_login_link(self):
        try:
            element = self.find_element(self.LOGIN_LINK)
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            self.driver.execute_script("arguments[0].click();", element)
        except:
            # Fallback to regular click
            self.click_element(self.LANDLORD_BUTTON)
        return self

    def click_account_icon(self):
        try:
            element = self.find_element(self.USER_ACCOUNT_BUTTON)
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            self.driver.execute_script("arguments[0].click();", element)
        except:
            # Fallback to regular click
            self.click_element(self.LANDLORD_BUTTON)
        return self

    def click_register_link(self):
        try:
            element = self.find_element(self.REGISTER_BUTTON)
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            self.driver.execute_script("arguments[0].click();", element)
        except:
            # Fallback to regular click
            self.click_element(self.LANDLORD_BUTTON)
        return self

    def click_tenant_button(self):
        """Click Tenant button with interception handling"""
        try:
            element = self.find_element(self.TENANT_BUTTON)
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            self.driver.execute_script("arguments[0].click();", element)
        except:
            # Fallback to regular click
            self.click_element(self.TENANT_BUTTON)
        return self
    
    def search_in_header(self, search_term):
        """Search using header search bar"""
        self.send_keys_to_element(self.SEARCH_BAR, search_term)
        return self
    
    def click_login_button(self):
        """Click Login button to open modal"""
        self.click_element(self.LOGIN_BUTTON)
        self.wait.until(EC.visibility_of_element_located(self.LOGIN_MODAL))
        return self
    
    def click_register_button(self):
        """Click Register button to open modal"""
        self.click_element(self.REGISTER_BUTTON)
        self.wait.until(EC.visibility_of_element_located(self.REGISTER_MODAL))
        return self
    
    def login(self, email, password, remember_me=False):
        """Perform login with credentials"""
        self.click_account_icon()
        self.click_login_button()
        self.send_keys_to_element(self.LOGIN_EMAIL_INPUT, email)
        self.send_keys_to_element(self.LOGIN_PASSWORD_INPUT, password)
        
        if remember_me:
            self.click_element(self.REMEMBER_ME_CHECKBOX)
        
        self.click_element(self.LOGIN_SUBMIT_BUTTON)
        
        # Wait for modal to close or error to appear
        try:
            self.wait_for_element_to_disappear(self.LOGIN_MODAL, timeout=5)
            return True
        except:
            return False

    def register(self, user_data):
        """Perform registration with user data"""
        self.click_account_icon()
        self.click_register_button()

        self.send_keys_to_element(self.REGISTER_USERNAME_INPUT, user_data['user_name'])
        self.send_keys_to_element(self.REGISTER_EMAIL_INPUT, user_data['email'])
        self.send_keys_to_element(self.REGISTER_PASSWORD_INPUT, user_data['password'])
        self.send_keys_to_element(self.REGISTER_CONFIRM_PASSWORD_INPUT, user_data['password'])
        self.send_keys_to_element(self.REGISTER_FIRST_NAME_INPUT, user_data['first_name'])
        self.send_keys_to_element(self.REGISTER_LAST_NAME_INPUT, user_data['last_name'])
        self.send_keys_to_element(self.REGISTER_PHONE_INPUT, user_data['phone'])

        # Select user role
        if user_data.get('role', 'tenant') == 'landlord':
            self.click_element(self.REGISTER_LANDLORD_RADIO)
        else:
            self.click_element(self.REGISTER_TENANT_RADIO)

        self.click_element(self.REGISTER_SUBMIT_BUTTON)

        # --- NEW CODE TO HANDLE THE ALERT ---
        try:
            # Wait for the alert to appear and then accept it
            print("INFO: Waiting for registration confirmation alert...")
            self.accept_alert()
            print("INFO: Alert accepted.")

            # After accepting the alert, wait for the modal to close
            self.wait_for_element_to_disappear(self.REGISTER_MODAL, timeout=5)
            return True
        except TimeoutException:
            # If no alert appears after a few seconds, assume it was successful anyway
            # and just check if the modal closed.
            print("WARN: No alert appeared. Checking if modal closed.")
            try:
                self.wait_for_element_to_disappear(self.REGISTER_MODAL, timeout=5)
                return True
            except:
                print("ERROR: Modal did not close after registration.")
                return False
        except Exception as e:
            print(f"ERROR: An unexpected error occurred during alert handling: {e}")
            return False

    def close_login_modal(self):
        """Close login modal"""
        self.click_element(self.LOGIN_CLOSE_BUTTON)
        self.wait_for_element_to_disappear(self.LOGIN_MODAL)
        return self
    
    def close_register_modal(self):
        """Close register modal"""
        self.click_element(self.REGISTER_CLOSE_BUTTON)
        self.wait_for_element_to_disappear(self.REGISTER_MODAL)
        return self
    
    def click_forgot_password(self):
        """Click forgot password link"""
        self.click_element(self.FORGOT_PASSWORD_LINK)
        return self
    
    def switch_to_register_from_login(self):
        """Switch from login modal to register modal"""
        self.close_login_modal()
        self.click_account_icon()
        self.click_element(self.REGISTER_BUTTON)
        self.wait_for_element_to_disappear(self.LOGIN_MODAL)
        self.wait.until(EC.visibility_of_element_located(self.REGISTER_MODAL))
        return self
    
    def switch_to_login_from_register(self):
        """Switch from register modal to login modal"""
        self.click_element(self.LOGIN_LINK)
        self.wait_for_element_to_disappear(self.REGISTER_MODAL)
        self.wait.until(EC.visibility_of_element_located(self.LOGIN_MODAL))
        return self
    
    def logout(self):
        """Logout user"""
        self.wait.until(EC.visibility_of_element_located(self.ACCOUNT_DROPDOWN))
        self.click_element(self.LOGOUT_BUTTON)
        return self
    
    def click_notifications(self):
        """Click notification bell"""
        self.click_element(self.NOTIFICATION_BELL)
        self.wait.until(EC.visibility_of_element_located(self.NOTIFICATION_DROPDOWN))
        return self
    
    def get_notification_count(self):
        """Get notification count from badge"""
        if self.is_element_visible(self.NOTIFICATION_BADGE):
            return int(self.get_element_text(self.NOTIFICATION_BADGE))
        return 0
    
    def get_notifications(self):
        """Get all notification items"""
        self.click_notifications()
        notifications = self.find_elements(self.NOTIFICATION_ITEMS)
        return [notif.text for notif in notifications]
    
    def click_notification_item(self, index=0):
        """Click on notification item by index"""
        notifications = self.find_elements(self.NOTIFICATION_ITEMS)
        if index < len(notifications):
            notifications[index].click()
            return True
        return False
    
    def is_user_logged_in(self):
        """Check if user is logged in"""
        self.click_account_icon()
        return self.is_element_visible(self.USER_ACCOUNT_BUTTON)
    
    def is_user_logged_out(self):
        """Check if user is logged out"""
        self.click_account_icon()
        return self.is_element_visible(self.LOGIN_BUTTON)
    
    def get_user_name(self):
        """Get displayed user name"""
        if self.is_element_visible(self.USER_NAME_DISPLAY):
            return self.get_element_text(self.USER_NAME_DISPLAY)
        return None
    
    def get_error_message(self):
        """Get error message text"""
        if self.is_element_visible(self.ERROR_MESSAGE):
            return self.get_element_text(self.ERROR_MESSAGE)
        return None
    
    def get_success_message(self):
        """Get success message text"""
        if self.is_element_visible(self.SUCCESS_MESSAGE):
            return self.get_element_text(self.SUCCESS_MESSAGE)
        return None
    
    def is_login_modal_open(self):
        """Check if login modal is open"""
        return self.is_element_visible(self.LOGIN_MODAL)
    
    def is_register_modal_open(self):
        """Check if register modal is open"""
        return self.is_element_visible(self.REGISTER_MODAL)
    
    def wait_for_login_modal_to_open(self, timeout=10):
        """Wait for login modal to open"""
        self.wait.until(EC.visibility_of_element_located(self.LOGIN_MODAL))
        return self
    
    def wait_for_register_modal_to_open(self, timeout=10):
        """Wait for register modal to open"""
        self.wait.until(EC.visibility_of_element_located(self.REGISTER_MODAL))
        return self
    
    def wait_for_login_modal_to_close(self, timeout=10):
        """Wait for login modal to close"""
        self.wait_for_element_to_disappear(self.LOGIN_MODAL, timeout)
        return self
    
    def wait_for_register_modal_to_close(self, timeout=10):
        """Wait for register modal to close"""
        self.wait_for_element_to_disappear(self.REGISTER_MODAL, timeout)
        return self
    
    def clear_login_form(self):
        """Clear login form fields"""
        self.clear_element(self.LOGIN_EMAIL_INPUT)
        self.clear_element(self.LOGIN_PASSWORD_INPUT)
        return self
    
    def clear_register_form(self):
        """Clear register form fields"""
        self.clear_element(self.REGISTER_EMAIL_INPUT)
        self.clear_element(self.REGISTER_PASSWORD_INPUT)
        self.clear_element(self.REGISTER_CONFIRM_PASSWORD_INPUT)
        self.clear_element(self.REGISTER_FIRST_NAME_INPUT)
        self.clear_element(self.REGISTER_LAST_NAME_INPUT)
        self.clear_element(self.REGISTER_PHONE_INPUT)
        return self
    
    def fill_login_form(self, email, password, remember_me=False):
        """Fill login form without submitting"""
        self.send_keys_to_element(self.LOGIN_EMAIL_INPUT, email)
        self.send_keys_to_element(self.LOGIN_PASSWORD_INPUT, password)
        
        if remember_me:
            checkbox = self.find_element(self.REMEMBER_ME_CHECKBOX)
            if not checkbox.is_selected():
                checkbox.click()
        
        return self
    
    def fill_register_form(self, user_data):
        """Fill register form without submitting"""
        self.send_keys_to_element(self.REGISTER_EMAIL_INPUT, user_data['email'])
        self.send_keys_to_element(self.REGISTER_PASSWORD_INPUT, user_data['password'])
        self.send_keys_to_element(self.REGISTER_CONFIRM_PASSWORD_INPUT, user_data.get('confirm_password', user_data['password']))
        self.send_keys_to_element(self.REGISTER_FIRST_NAME_INPUT, user_data['first_name'])
        self.send_keys_to_element(self.REGISTER_LAST_NAME_INPUT, user_data['last_name'])
        self.send_keys_to_element(self.REGISTER_PHONE_INPUT, user_data['phone'])
        
        # Select user role
        if user_data.get('role', 'tenant') == 'landlord':
            self.click_element(self.REGISTER_LANDLORD_RADIO)
        else:
            self.click_element(self.REGISTER_TENANT_RADIO)
        
        return self
    
    def submit_login_form(self):
        """Submit login form"""
        self.click_element(self.LOGIN_SUBMIT_BUTTON)
        return self
    
    def submit_register_form(self):
        """Submit register form"""
        self.click_element(self.REGISTER_SUBMIT_BUTTON)
        return self
    
    def is_remember_me_checked(self):
        """Check if remember me checkbox is checked"""
        checkbox = self.find_element(self.REMEMBER_ME_CHECKBOX)
        return checkbox.is_selected()
    
    def get_selected_role(self):
        """Get selected role in register form"""
        tenant_radio = self.find_element(self.REGISTER_TENANT_RADIO)
        landlord_radio = self.find_element(self.REGISTER_LANDLORD_RADIO)
        
        if tenant_radio.is_selected():
            return 'tenant'
        elif landlord_radio.is_selected():
            return 'landlord'
        else:
            return None
    
    def has_notifications(self):
        """Check if user has notifications"""
        return self.get_notification_count() > 0
    
    def clear_all_notifications(self):
        """Clear all notifications if clear option exists"""
        # This would depend on implementation
        # For now, just click each notification
        notifications = self.find_elements(self.NOTIFICATION_ITEMS)
        for notification in notifications:
            try:
                notification.click()
                time.sleep(0.5)
            except:
                pass
        return self
    
    def navigate_to_home(self):
        """Navigate to home page by clicking logo"""
        self.click_logo()
        return self
    
    def navigate_to_tenant_dashboard(self):
        """Navigate to tenant dashboard"""
        self.click_tenant_button()
        return self
    
    def navigate_to_landlord_dashboard(self):
        """Navigate to landlord dashboard"""
        self.click_landlord_button()
        return self
    
    def perform_header_search(self, search_term):
        """Perform search from header and submit"""
        from selenium.webdriver.common.keys import Keys
        search_element = self.find_element(self.SEARCH_BAR)
        search_element.clear()
        search_element.send_keys(search_term)
        search_element.send_keys(Keys.ENTER)
        return self
    
    def get_current_user_role(self):
        """Determine current user role based on visible elements"""
        # This would depend on how roles are indicated in the header
        # For now, check which dashboard button is more prominent or active
        if self.is_element_visible(self.LANDLORD_BUTTON):
            return 'landlord'
        elif self.is_element_visible(self.TENANT_BUTTON):
            return 'tenant'
        else:
            return None
    
    def wait_for_page_to_load(self):
        """Wait for header to be fully loaded"""
        self.wait.until(EC.visibility_of_element_located(self.LOGO))
        return self
    
    def is_header_visible(self):
        """Check if header is visible"""
        return self.is_element_visible(self.LOGO)
    
    def get_search_placeholder_text(self):
        """Get search bar placeholder text"""
        search_element = self.find_element(self.SEARCH_BAR)
        return search_element.get_attribute('placeholder')
    
    def is_search_bar_focused(self):
        """Check if search bar is focused"""
        search_element = self.find_element(self.SEARCH_BAR)
        return search_element == self.driver.switch_to.active_element
    
    def click_outside_modals(self):
        """Click outside modals to close them"""
        # Click on logo or another safe area
        self.click_element(self.LOGO)
        return self
    
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