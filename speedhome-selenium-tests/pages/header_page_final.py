"""
Final HeaderPage class with correct selectors based on actual SpeedHome UI inspection
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages.base_page import BasePage
import time
import os

class HeaderPage(BasePage):
    """Page object for SpeedHome header/navigation with correct selectors"""
    
    # Header elements based on actual page inspection
    SPEEDHOME_LOGO = (By.CSS_SELECTOR, "a[href='/'], .logo, [class*='logo']")
    
    # Role toggle buttons (found in inspection)
    LANDLORD_BUTTON = (By.XPATH, "//button[contains(text(), 'Landlord')]")
    TENANT_BUTTON = (By.XPATH, "//button[contains(text(), 'Tenant')]")
    
    # Search elements (found in inspection)
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[placeholder*='Search by area'], input[placeholder*='property name']")
    MAIN_SEARCH_INPUT = (By.CSS_SELECTOR, "input[placeholder='Search by area/property name']")
    SECONDARY_SEARCH_INPUT = (By.CSS_SELECTOR, "input[placeholder='Search by property name or location...']")
    
    # User icon (found as button with 👤 text)
    USER_ICON = (By.XPATH, "//button[contains(text(), '👤')]")
    USER_BUTTON = (By.CSS_SELECTOR, "button[class*='text-gray-600'][class*='hover:text-gray-900']")
    
    # Language/Globe icon (found as button with 🌐 text)
    LANGUAGE_ICON = (By.XPATH, "//button[contains(text(), '🌐')]")
    
    # More Filters button (found in inspection)
    MORE_FILTERS_BUTTON = (By.XPATH, "//button[contains(text(), 'More Filters')]")
    
    # Authentication elements (likely in dropdown/modal after clicking user icon)
    LOGIN_LINK = (By.XPATH, "//a[contains(text(), 'Login')] | //button[contains(text(), 'Login')] | //span[contains(text(), 'Login')]")
    REGISTER_LINK = (By.XPATH, "//a[contains(text(), 'Register')] | //button[contains(text(), 'Register')] | //span[contains(text(), 'Register')] | //a[contains(text(), 'Sign Up')] | //button[contains(text(), 'Sign Up')]")
    
    # Modal elements
    LOGIN_MODAL = (By.CSS_SELECTOR, ".modal, [class*='modal'], [role='dialog']")
    REGISTER_MODAL = (By.CSS_SELECTOR, ".modal, [class*='modal'], [role='dialog']")
    MODAL_CLOSE = (By.CSS_SELECTOR, ".close, [class*='close'], button[aria-label='Close']")
    
    # Form elements (generic selectors that should work)
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[placeholder*='email']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password'], input[name='password'], input[placeholder*='password']")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def click_user_icon(self):
        """Click the user icon (👤 button) with improved click handling"""
        try:
            # Find the element first
            user_icon = self.driver.find_element(*self.USER_ICON)
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", user_icon)
            time.sleep(0.5)
            
            # Try regular click first
            try:
                user_icon.click()
            except Exception:
                # If regular click fails, use JavaScript click
                self.driver.execute_script("arguments[0].click();", user_icon)
            
            time.sleep(1)  # Wait for dropdown to appear
            return True
        except Exception as e:
            print(f"❌ Could not find or click user icon: {e}")
            return False
    
    def click_language_icon(self):
        """Click the language icon (🌐 button) with improved click handling"""
        try:
            lang_icon = self.driver.find_element(*self.LANGUAGE_ICON)
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", lang_icon)
            time.sleep(0.5)
            
            # Try regular click first
            try:
                lang_icon.click()
            except Exception:
                # If regular click fails, use JavaScript click
                self.driver.execute_script("arguments[0].click();", lang_icon)
            
            time.sleep(1)
            return True
        except Exception as e:
            print(f"❌ Could not find or click language icon: {e}")
            return False
    
    def click_more_filters(self):
        """Click the More Filters button with improved click handling"""
        try:
            filters_btn = self.driver.find_element(*self.MORE_FILTERS_BUTTON)
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", filters_btn)
            time.sleep(0.5)
            
            # Try regular click first
            try:
                filters_btn.click()
            except Exception:
                # If regular click fails, use JavaScript click
                self.driver.execute_script("arguments[0].click();", filters_btn)
            
            time.sleep(1)
            return True
        except Exception as e:
            print(f"❌ Could not find or click More Filters button: {e}")
            return False
    
    def search_properties(self, search_term):
        """Search for properties using the main search input with improved submission"""
        try:
            search_input = None
            
            # Try main search input first
            if self.is_element_present(self.MAIN_SEARCH_INPUT):
                search_input = self.driver.find_element(*self.MAIN_SEARCH_INPUT)
            elif self.is_element_present(self.SECONDARY_SEARCH_INPUT):
                search_input = self.driver.find_element(*self.SECONDARY_SEARCH_INPUT)
            else:
                print("❌ No search input found")
                return False
            
            # Clear and enter search term
            search_input.clear()
            search_input.send_keys(search_term)
            
            # Use Enter key instead of submit() to avoid form submission error
            search_input.send_keys(Keys.ENTER)
            
            time.sleep(2)
            return True
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False
    
    def switch_to_tenant_mode(self):
        """Switch to tenant mode with improved click handling"""
        try:
            tenant_btn = self.driver.find_element(*self.TENANT_BUTTON)
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tenant_btn)
            time.sleep(0.5)
            
            # Try regular click first
            try:
                tenant_btn.click()
            except Exception:
                # If regular click fails, use JavaScript click
                self.driver.execute_script("arguments[0].click();", tenant_btn)
            
            time.sleep(1)
            return True
        except Exception as e:
            print(f"❌ Could not click tenant button: {e}")
            return False
    
    def switch_to_landlord_mode(self):
        """Switch to landlord mode with improved click handling"""
        try:
            landlord_btn = self.driver.find_element(*self.LANDLORD_BUTTON)
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", landlord_btn)
            time.sleep(0.5)
            
            # Try regular click first
            try:
                landlord_btn.click()
            except Exception:
                # If regular click fails, use JavaScript click
                self.driver.execute_script("arguments[0].click();", landlord_btn)
            
            time.sleep(1)
            return True
        except Exception as e:
            print(f"❌ Could not click landlord button: {e}")
            return False
    
    def get_current_role(self):
        """Get the currently selected role based on button styling"""
        try:
            tenant_btn = self.driver.find_element(*self.TENANT_BUTTON)
            landlord_btn = self.driver.find_element(*self.LANDLORD_BUTTON)
            
            tenant_classes = tenant_btn.get_attribute('class')
            landlord_classes = landlord_btn.get_attribute('class')
            
            # Check which button has active styling (blue background for tenant, green for landlord)
            if 'bg-blue-600' in tenant_classes:
                return 'tenant'
            elif 'bg-green-600' in landlord_classes or 'bg-green-100' in landlord_classes:
                return 'landlord'
            else:
                return 'unknown'
        except:
            return 'unknown'
    
    def is_user_logged_in(self):
        """Check if user is logged in (placeholder - needs actual implementation)"""
        # This would need to be implemented based on actual UI changes when logged in
        return False
    
    def get_page_title(self):
        """Get the page title"""
        return self.driver.title
    
    def get_current_url(self):
        """Get the current URL"""
        return self.driver.current_url
    
    def is_homepage_loaded(self):
        """Check if homepage is properly loaded"""
        try:
            # Check for key elements that should be present on homepage
            logo_present = self.is_element_present(self.SPEEDHOME_LOGO)
            search_present = self.is_element_present(self.MAIN_SEARCH_INPUT)
            tenant_btn_present = self.is_element_present(self.TENANT_BUTTON)
            
            return logo_present and search_present and tenant_btn_present
        except:
            return False
    
    def get_all_buttons(self):
        """Get all buttons on the page for debugging"""
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            button_info = []
            
            for i, btn in enumerate(buttons):
                try:
                    text = btn.text.strip()
                    classes = btn.get_attribute('class')
                    button_info.append({
                        'index': i,
                        'text': text,
                        'classes': classes
                    })
                except:
                    button_info.append({
                        'index': i,
                        'text': 'Could not get text',
                        'classes': 'Could not get classes'
                    })
            
            return button_info
        except:
            return []
    
    def get_all_inputs(self):
        """Get all input elements on the page for debugging"""
        try:
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            input_info = []
            
            for i, inp in enumerate(inputs):
                try:
                    placeholder = inp.get_attribute('placeholder')
                    input_type = inp.get_attribute('type')
                    classes = inp.get_attribute('class')
                    input_info.append({
                        'index': i,
                        'type': input_type,
                        'placeholder': placeholder,
                        'classes': classes
                    })
                except:
                    input_info.append({
                        'index': i,
                        'type': 'Could not get type',
                        'placeholder': 'Could not get placeholder',
                        'classes': 'Could not get classes'
                    })
            
            return input_info
        except:
            return []


    def take_screenshot(self, name):
        """Take screenshot for debugging"""
        try:
            # Ensure screenshots directory exists
            screenshot_dir = "reports/screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # Save screenshot
            screenshot_path = f"{screenshot_dir}/{name}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved: {screenshot_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to take screenshot: {e}")
            return False

