"""
Updated HeaderPage class for SpeedHome application with correct selectors
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages.base_page import BasePage
import time

class HeaderPage(BasePage):
    """Page object for SpeedHome header/navigation"""
    
    # Header elements based on observed UI structure
    SPEEDHOME_LOGO = (By.CSS_SELECTOR, "a[href='/'], .logo, [class*='logo']")
    
    # Role toggle buttons (Landlord/Tenant)
    LANDLORD_BUTTON = (By.XPATH, "//button[contains(text(), 'Landlord')]")
    TENANT_BUTTON = (By.XPATH, "//button[contains(text(), 'Tenant')]")
    
    # Search elements
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[placeholder*='Search'], input[placeholder*='area'], input[placeholder*='property']")
    
    # User/Profile icon (top right)
    USER_ICON = (By.CSS_SELECTOR, "svg[class*='user'], .user-icon, [class*='profile'], button[class*='user']")
    USER_DROPDOWN = (By.CSS_SELECTOR, ".dropdown-menu, [class*='dropdown'], [class*='menu']")
    
    # Authentication elements (likely in dropdown/modal)
    LOGIN_LINK = (By.XPATH, "//a[contains(text(), 'Login')] | //button[contains(text(), 'Login')] | //span[contains(text(), 'Login')]")
    REGISTER_LINK = (By.XPATH, "//a[contains(text(), 'Register')] | //button[contains(text(), 'Register')] | //span[contains(text(), 'Register')] | //a[contains(text(), 'Sign Up')] | //button[contains(text(), 'Sign Up')]")
    
    # Modal elements
    LOGIN_MODAL = (By.CSS_SELECTOR, ".modal, [class*='modal'], [role='dialog']")
    REGISTER_MODAL = (By.CSS_SELECTOR, ".modal, [class*='modal'], [role='dialog']")
    MODAL_CLOSE = (By.CSS_SELECTOR, ".close, [class*='close'], button[aria-label='Close']")
    
    # Login form elements
    LOGIN_EMAIL = (By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[placeholder*='email']")
    LOGIN_PASSWORD = (By.CSS_SELECTOR, "input[type='password'], input[name='password'], input[placeholder*='password']")
    LOGIN_SUBMIT = (By.CSS_SELECTOR, "button[type='submit'], button[class*='login'], input[type='submit']")
    REMEMBER_ME = (By.CSS_SELECTOR, "input[type='checkbox'][name*='remember'], input[type='checkbox'][id*='remember']")
    
    # Register form elements
    REGISTER_EMAIL = (By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[placeholder*='email']")
    REGISTER_PASSWORD = (By.CSS_SELECTOR, "input[type='password'], input[name='password'], input[placeholder*='password']")
    REGISTER_FIRST_NAME = (By.CSS_SELECTOR, "input[name='firstName'], input[name='first_name'], input[placeholder*='first']")
    REGISTER_LAST_NAME = (By.CSS_SELECTOR, "input[name='lastName'], input[name='last_name'], input[placeholder*='last']")
    REGISTER_PHONE = (By.CSS_SELECTOR, "input[name='phone'], input[type='tel'], input[placeholder*='phone']")
    REGISTER_ROLE_TENANT = (By.CSS_SELECTOR, "input[value='tenant'], button[data-role='tenant'], [class*='tenant']")
    REGISTER_ROLE_LANDLORD = (By.CSS_SELECTOR, "input[value='landlord'], button[data-role='landlord'], [class*='landlord']")
    REGISTER_SUBMIT = (By.CSS_SELECTOR, "button[type='submit'], button[class*='register'], input[type='submit']")
    
    # User state elements
    USER_NAME_DISPLAY = (By.CSS_SELECTOR, ".user-name, [class*='username'], [class*='user-display']")
    LOGOUT_BUTTON = (By.XPATH, "//a[contains(text(), 'Logout')] | //button[contains(text(), 'Logout')] | //span[contains(text(), 'Logout')]")
    
    # Notification elements
    NOTIFICATION_ICON = (By.CSS_SELECTOR, ".notification, [class*='notification'], .bell")
    NOTIFICATION_BADGE = (By.CSS_SELECTOR, ".badge, [class*='badge'], .count")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def click_user_icon(self):
        """Click the user icon to open dropdown/modal"""
        try:
            self.click_element(self.USER_ICON)
            time.sleep(1)  # Wait for dropdown to appear
            return True
        except TimeoutException:
            print("❌ Could not find or click user icon")
            return False
    
    def click_login_link(self):
        """Click login link (after opening user dropdown)"""
        try:
            # First try to click user icon if not already open
            self.click_user_icon()
            # Then click login
            self.click_element(self.LOGIN_LINK)
            return True
        except TimeoutException:
            print("❌ Could not find login link")
            return False
    
    def click_register_link(self):
        """Click register link (after opening user dropdown)"""
        try:
            # First try to click user icon if not already open
            self.click_user_icon()
            # Then click register
            self.click_element(self.REGISTER_LINK)
            return True
        except TimeoutException:
            print("❌ Could not find register link")
            return False
    
    def is_login_modal_open(self):
        """Check if login modal is open"""
        try:
            modal = self.wait.until(EC.presence_of_element_located(self.LOGIN_MODAL))
            return modal.is_displayed()
        except TimeoutException:
            return False
    
    def is_register_modal_open(self):
        """Check if register modal is open"""
        try:
            modal = self.wait.until(EC.presence_of_element_located(self.REGISTER_MODAL))
            return modal.is_displayed()
        except TimeoutException:
            return False
    
    def login(self, email, password, remember_me=False):
        """Complete login process"""
        try:
            # Open login modal/form
            if not self.click_login_link():
                return False
            
            # Wait for modal to open
            time.sleep(2)
            
            # Fill login form
            self.send_keys_to_element(self.LOGIN_EMAIL, email)
            self.send_keys_to_element(self.LOGIN_PASSWORD, password)
            
            if remember_me:
                try:
                    self.click_element(self.REMEMBER_ME)
                except:
                    pass  # Remember me is optional
            
            # Submit form
            self.click_element(self.LOGIN_SUBMIT)
            
            # Wait for login to complete
            time.sleep(3)
            
            return self.is_user_logged_in()
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def register(self, user_data):
        """Complete registration process"""
        try:
            # Open register modal/form
            if not self.click_register_link():
                return False
            
            # Wait for modal to open
            time.sleep(2)
            
            # Fill registration form
            self.send_keys_to_element(self.REGISTER_EMAIL, user_data['email'])
            self.send_keys_to_element(self.REGISTER_PASSWORD, user_data['password'])
            
            if 'first_name' in user_data:
                self.send_keys_to_element(self.REGISTER_FIRST_NAME, user_data['first_name'])
            
            if 'last_name' in user_data:
                self.send_keys_to_element(self.REGISTER_LAST_NAME, user_data['last_name'])
            
            if 'phone' in user_data:
                self.send_keys_to_element(self.REGISTER_PHONE, user_data['phone'])
            
            # Select role if specified
            if user_data.get('role') == 'tenant':
                try:
                    self.click_element(self.REGISTER_ROLE_TENANT)
                except:
                    pass
            elif user_data.get('role') == 'landlord':
                try:
                    self.click_element(self.REGISTER_ROLE_LANDLORD)
                except:
                    pass
            
            # Submit form
            self.click_element(self.REGISTER_SUBMIT)
            
            # Wait for registration to complete
            time.sleep(3)
            
            return self.is_user_logged_in()
            
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return False
    
    def is_user_logged_in(self):
        """Check if user is logged in"""
        try:
            # Look for user name display or logout button
            user_name = self.driver.find_elements(*self.USER_NAME_DISPLAY)
            logout_btn = self.driver.find_elements(*self.LOGOUT_BUTTON)
            
            return len(user_name) > 0 or len(logout_btn) > 0
        except:
            return False
    
    def get_user_name(self):
        """Get displayed user name"""
        try:
            element = self.driver.find_element(*self.USER_NAME_DISPLAY)
            return element.text.strip()
        except:
            return ""
    
    def logout(self):
        """Logout user"""
        try:
            # Click user icon first
            self.click_user_icon()
            # Then click logout
            self.click_element(self.LOGOUT_BUTTON)
            time.sleep(2)
            return not self.is_user_logged_in()
        except:
            return False
    
    def search_properties(self, search_term):
        """Search for properties"""
        try:
            self.send_keys_to_element(self.SEARCH_INPUT, search_term)
            # Press Enter or look for search button
            search_input = self.driver.find_element(*self.SEARCH_INPUT)
            search_input.submit()
            time.sleep(2)
            return True
        except:
            return False
    
    def switch_to_tenant_mode(self):
        """Switch to tenant mode"""
        try:
            self.click_element(self.TENANT_BUTTON)
            time.sleep(1)
            return True
        except:
            return False
    
    def switch_to_landlord_mode(self):
        """Switch to landlord mode"""
        try:
            self.click_element(self.LANDLORD_BUTTON)
            time.sleep(1)
            return True
        except:
            return False
    
    def close_modal(self):
        """Close any open modal"""
        try:
            self.click_element(self.MODAL_CLOSE)
            time.sleep(1)
            return True
        except:
            return False

