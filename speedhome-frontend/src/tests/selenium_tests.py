from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import unittest

class SpeedHomeTests(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.base_url = "http://localhost:5173"  # Updated for local testing
        self.driver.get(self.base_url)
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(2)  # Additional wait to ensure all elements are loaded

    def tearDown(self):
        self.driver.quit()

    def test_header_buttons_clickable(self):
        """Test that all header buttons (landlord, tenant, account) are clickable"""
        print("Testing header buttons...")
        
        # Test Landlord button
        landlord_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Landlord')]")
        self.assertTrue(landlord_button.is_displayed(), "Landlord button is not displayed")
        landlord_button.click()
        time.sleep(3)
        # Verify navigation worked (should go to landlord dashboard)
        self.assertTrue("/landlord" in self.driver.current_url, 
                      f"Landlord button click did not navigate correctly. Current URL: {self.driver.current_url}")
        
        # Verify landlord dashboard content is loaded (not blank)
        dashboard_title = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Landlord Dashboard')]"))
        )
        self.assertTrue(dashboard_title.is_displayed(), "Landlord dashboard did not load properly")
        
        # Go back to home page
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Test Tenant button
        tenant_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Tenant')]")
        self.assertTrue(tenant_button.is_displayed(), "Tenant button is not displayed")
        tenant_button.click()
        time.sleep(2)
        # Verify we're back on home page (tenant should go to home page)
        self.assertTrue(self.driver.current_url == self.base_url + "/" or self.driver.current_url == self.base_url, 
                      f"Tenant button click did not navigate to home. Current URL: {self.driver.current_url}")
        
        print("Header buttons test passed!")

    def test_account_dropdown_functionality(self):
        """Test that account dropdown menu works and provides access to dashboard"""
        print("Testing account dropdown functionality...")
        
        # Test Account button dropdown
        account_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '👤')]")
        self.assertTrue(account_button.is_displayed(), "Account button is not displayed")
        account_button.click()
        time.sleep(2)
        
        # Verify dropdown menu appears
        try:
            dropdown_menu = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'absolute right-0 mt-2 w-48')]"))
            )
            self.assertTrue(dropdown_menu.is_displayed(), "Account dropdown menu did not appear")
            
            # Test Login/Register option
            login_option = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login / Register')]")
            self.assertTrue(login_option.is_displayed(), "Login/Register option not found in dropdown")
            login_option.click()
            time.sleep(2)
            
            # Verify login modal appears
            login_modal = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//h2[contains(text(), 'Login')]"))
            )
            self.assertTrue(login_modal.is_displayed(), "Login modal did not appear")
            
            # Close login modal
            close_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '×')]")
            close_button.click()
            time.sleep(1)
            
            # Test Dashboard option
            account_button.click()  # Open dropdown again
            time.sleep(1)
            dashboard_option = self.driver.find_element(By.XPATH, "//button[contains(text(), 'My Dashboard')]")
            self.assertTrue(dashboard_option.is_displayed(), "Dashboard option not found in dropdown")
            dashboard_option.click()
            time.sleep(3)
            
            # Verify navigation to dashboard
            self.assertTrue("/dashboard" in self.driver.current_url, 
                          f"Dashboard option did not navigate correctly. Current URL: {self.driver.current_url}")
            
            # Verify dashboard content is loaded
            dashboard_title = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'My Dashboard')]"))
            )
            self.assertTrue(dashboard_title.is_displayed(), "User dashboard did not load properly")
            
        except TimeoutException:
            self.fail("Account dropdown functionality test failed")
        
        print("Account dropdown functionality test passed!")

    def test_property_listing_navigation(self):
        """Test that clicking on property listings navigates to property detail page"""
        print("Testing property listing navigation...")
        
        # Go back to home page first
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Find the first property card
        try:
            property_cards = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'bg-white rounded-lg shadow-sm')]"))
            )
            self.assertTrue(len(property_cards) > 0, "No property cards found on the page")
            
            # Get the title of the first property for verification later
            property_title = property_cards[0].find_element(By.XPATH, ".//h3").text
            
            # Click on the first property card
            property_cards[0].click()
            time.sleep(3)
            
            # Verify we're on a property detail page (not blank)
            self.assertTrue("/property/" in self.driver.current_url, 
                          f"Property card click did not navigate to detail page. Current URL: {self.driver.current_url}")
            
            # Verify the page is not blank by checking for property content
            try:
                detail_content = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h1 | //h2 | //div[contains(@class, 'property')]"))
                )
                self.assertTrue(detail_content.is_displayed(), "Property detail page appears to be blank")
            except TimeoutException:
                self.fail("Property detail page is blank or did not load properly")
            
        except TimeoutException:
            self.fail("Property cards not found or not clickable")
        
        print("Property listing navigation test passed!")

    def test_interactive_elements(self):
        """Test that all interactive elements on property detail page work"""
        print("Testing interactive elements on property detail page...")
        
        # Go back to home page first
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # First navigate to a property detail page
        try:
            property_cards = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'bg-white rounded-lg shadow-sm')]"))
            )
            property_cards[0].click()
            time.sleep(3)
            
            # Test floor plan button if it exists
            try:
                floor_plan_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'View Floor Plan')]"))
                )
                floor_plan_button.click()
                time.sleep(2)
                
                # Verify floor plan modal appears
                floor_plan_modal = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'fixed inset-0')]//img"))
                )
                self.assertTrue(floor_plan_modal.is_displayed(), "Floor plan modal did not appear")
                
                # Close the modal
                close_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '✕') or contains(text(), '×')]")
                close_button.click()
                time.sleep(1)
            except TimeoutException:
                print("Floor plan button not found, skipping floor plan test")
            
            # Test schedule viewing button
            try:
                schedule_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Schedule Viewing')]"))
                )
                schedule_button.click()
                time.sleep(2)
                
                # Verify schedule viewing modal appears
                schedule_modal = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, "//h2[contains(text(), 'Schedule Viewing')]"))
                )
                self.assertTrue(schedule_modal.is_displayed(), "Schedule viewing modal did not appear")
            except TimeoutException:
                print("Schedule viewing button not found, skipping schedule viewing test")
            
        except TimeoutException as e:
            self.fail(f"Interactive elements test failed: {str(e)}")
        
        print("Interactive elements test passed!")

    def test_favorites_functionality(self):
        """Test that favorites functionality works"""
        print("Testing favorites functionality...")
        
        # Go back to home page first
        self.driver.get(self.base_url)
        time.sleep(2)
        
        try:
            # Find favorite buttons on property cards
            favorite_buttons = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//button[contains(@class, 'absolute top-2 right-2')]"))
            )
            self.assertTrue(len(favorite_buttons) > 0, "No favorite buttons found")
            
            # Click the first favorite button
            initial_classes = favorite_buttons[0].get_attribute("class")
            favorite_buttons[0].click()
            time.sleep(2)
            
            # Check if the button state changed
            new_classes = favorite_buttons[0].get_attribute("class")
            self.assertNotEqual(initial_classes, new_classes, "Favorite button state did not change")
            
            # Refresh the page to verify persistence
            self.driver.refresh()
            time.sleep(3)
            
            # Find favorite buttons again and verify persistence
            favorite_buttons = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//button[contains(@class, 'absolute top-2 right-2')]"))
            )
            
            # Verify the state persisted
            persisted_classes = favorite_buttons[0].get_attribute("class")
            self.assertEqual(new_classes, persisted_classes, "Favorite state did not persist after refresh")
            
        except TimeoutException:
            self.fail("Favorites functionality test failed")
        
        print("Favorites functionality test passed!")

    def test_search_functionality(self):
        """Test that search bar functionality works properly"""
        print("Testing search functionality...")
        
        # Go back to home page first
        self.driver.get(self.base_url)
        time.sleep(2)
        
        try:
            # Find the search input
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search by area/property name']"))
            )
            self.assertTrue(search_input.is_displayed(), "Search input not found")
            
            # Test typing multiple characters without losing focus
            search_input.click()
            time.sleep(1)
            search_input.send_keys("Bangsar")
            time.sleep(2)
            
            # Verify the full text was entered
            entered_text = search_input.get_attribute("value")
            self.assertEqual(entered_text, "Bangsar", f"Search input did not retain full text. Got: {entered_text}")
            
            # Clear and test another search term
            search_input.clear()
            search_input.send_keys("KLCC")
            time.sleep(2)
            
            entered_text = search_input.get_attribute("value")
            self.assertEqual(entered_text, "KLCC", f"Search input did not retain second search term. Got: {entered_text}")
            
        except TimeoutException:
            self.fail("Search functionality test failed")
        
        print("Search functionality test passed!")

    def test_landlord_dashboard_functionality(self):
        """Test landlord dashboard property management functionality"""
        print("Testing landlord dashboard functionality...")
        
        # Navigate to landlord dashboard
        landlord_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Landlord')]")
        landlord_button.click()
        time.sleep(3)
        
        # Verify we're on the landlord dashboard
        self.assertTrue("/landlord" in self.driver.current_url, "Not on landlord dashboard")
        
        # Test Add New Property button
        try:
            add_property_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '+ Add New Property')]"))
            )
            add_property_button.click()
            time.sleep(2)
            
            # Verify modal appears
            modal_title = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//h3[contains(text(), 'Add New Property')]"))
            )
            self.assertTrue(modal_title.is_displayed(), "Add Property modal did not appear")
            
            # Fill in the form
            title_input = self.driver.find_element(By.XPATH, "//input[@name='title']")
            location_input = self.driver.find_element(By.XPATH, "//input[@name='location']")
            price_input = self.driver.find_element(By.XPATH, "//input[@name='price']")
            
            title_input.send_keys("Test Property")
            location_input.send_keys("Test Location, KL")
            price_input.send_keys("2000")
            
            # Submit the form
            submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Add Property')]")
            submit_button.click()
            time.sleep(2)
            
            # Handle the alert
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                self.assertIn("successfully", alert_text.lower(), "Success message not found")
                alert.accept()
                time.sleep(1)
            except:
                pass  # No alert appeared
            
            # Verify the property was added to the table
            property_rows = self.driver.find_elements(By.XPATH, "//tbody//tr")
            self.assertTrue(len(property_rows) > 3, "New property was not added to the table")
            
        except TimeoutException:
            self.fail("Add Property functionality test failed")
        
        print("Add Property functionality test passed!")

    def test_landlord_edit_property_functionality(self):
        """Test editing property functionality"""
        print("Testing edit property functionality...")
        
        # Navigate to landlord dashboard
        self.driver.get(self.base_url)
        time.sleep(2)
        landlord_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Landlord')]")
        landlord_button.click()
        time.sleep(3)
        
        try:
            # Find and click the first Edit button
            edit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Edit')]"))
            )
            edit_button.click()
            time.sleep(2)
            
            # Verify edit modal appears
            modal_title = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//h3[contains(text(), 'Edit Property')]"))
            )
            self.assertTrue(modal_title.is_displayed(), "Edit Property modal did not appear")
            
            # Modify the title
            title_input = self.driver.find_element(By.XPATH, "//input[@name='title']")
            original_title = title_input.get_attribute("value")
            title_input.clear()
            title_input.send_keys(original_title + " - Updated")
            
            # Submit the form
            update_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Update Property')]")
            update_button.click()
            time.sleep(2)
            
            # Handle the alert
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                self.assertIn("updated successfully", alert_text.lower(), "Update success message not found")
                alert.accept()
                time.sleep(1)
            except:
                pass  # No alert appeared
            
        except TimeoutException:
            self.fail("Edit Property functionality test failed")
        
        print("Edit Property functionality test passed!")

    def test_landlord_property_status_change(self):
        """Test changing property status functionality"""
        print("Testing property status change functionality...")
        
        # Navigate to landlord dashboard
        self.driver.get(self.base_url)
        time.sleep(2)
        landlord_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Landlord')]")
        landlord_button.click()
        time.sleep(3)
        
        try:
            # Find the first status dropdown
            status_dropdown = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//select[contains(@class, 'text-gray-600')]"))
            )
            
            # Get current status
            original_status = status_dropdown.get_attribute("value")
            
            # Change status to a different value
            new_status = "Inactive" if original_status != "Inactive" else "Active"
            status_dropdown.click()
            time.sleep(1)
            
            # Select new status
            option = self.driver.find_element(By.XPATH, f"//option[@value='{new_status}']")
            option.click()
            time.sleep(2)
            
            # Handle the alert
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                self.assertIn(new_status, alert_text, f"Status change alert should mention {new_status}")
                alert.accept()
                time.sleep(1)
            except:
                pass  # No alert appeared
            
            # Verify status was changed
            updated_dropdown = self.driver.find_element(By.XPATH, "//select[contains(@class, 'text-gray-600')]")
            updated_status = updated_dropdown.get_attribute("value")
            self.assertEqual(updated_status, new_status, f"Status was not updated. Expected: {new_status}, Got: {updated_status}")
            
        except TimeoutException:
            self.fail("Property status change test failed")
        
        print("Property status change test passed!")

    def test_landlord_delete_property_functionality(self):
        """Test deleting property functionality"""
        print("Testing delete property functionality...")
        
        # Navigate to landlord dashboard
        self.driver.get(self.base_url)
        time.sleep(2)
        landlord_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Landlord')]")
        landlord_button.click()
        time.sleep(3)
        
        try:
            # Count initial properties
            initial_rows = self.driver.find_elements(By.XPATH, "//tbody//tr")
            initial_count = len(initial_rows)
            
            # Find and click the first Delete button
            delete_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Delete')]"))
            )
            delete_button.click()
            time.sleep(1)
            
            # Handle the confirmation dialog
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                self.assertIn("sure", alert_text.lower(), "Confirmation dialog should ask for confirmation")
                alert.accept()  # Confirm deletion
                time.sleep(2)
                
                # Handle success alert
                try:
                    success_alert = self.driver.switch_to.alert
                    success_text = success_alert.text
                    self.assertIn("deleted successfully", success_text.lower(), "Delete success message not found")
                    success_alert.accept()
                    time.sleep(1)
                except:
                    pass  # No success alert
                
            except:
                self.fail("Confirmation dialog did not appear")
            
            # Verify property was deleted
            final_rows = self.driver.find_elements(By.XPATH, "//tbody//tr")
            final_count = len(final_rows)
            self.assertEqual(final_count, initial_count - 1, f"Property was not deleted. Initial: {initial_count}, Final: {final_count}")
            
        except TimeoutException:
            self.fail("Delete Property functionality test failed")
        
        print("Delete Property functionality test passed!")

    def test_landlord_dashboard_tabs_navigation(self):
        """Test navigation between different tabs in landlord dashboard"""
        print("Testing landlord dashboard tabs navigation...")
        
        # Navigate to landlord dashboard
        self.driver.get(self.base_url)
        time.sleep(2)
        landlord_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Landlord')]")
        landlord_button.click()
        time.sleep(3)
        
        try:
            # Test Viewing Requests tab
            viewing_requests_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Viewing Requests')]"))
            )
            viewing_requests_tab.click()
            time.sleep(2)
            
            # Verify viewing requests content is displayed
            viewing_content = self.driver.find_element(By.XPATH, "//th[contains(text(), 'Tenant Name')] | //th[contains(text(), 'Property')]")
            self.assertTrue(viewing_content.is_displayed(), "Viewing Requests content not displayed")
            
            # Test Tenant Applications tab
            tenant_applications_tab = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Tenant Applications')]")
            tenant_applications_tab.click()
            time.sleep(2)
            
            # Verify tenant applications content is displayed
            applications_content = self.driver.find_element(By.XPATH, "//th[contains(text(), 'Applicant')] | //th[contains(text(), 'Application Date')]")
            self.assertTrue(applications_content.is_displayed(), "Tenant Applications content not displayed")
            
            # Test Earnings tab
            earnings_tab = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Earnings')]")
            earnings_tab.click()
            time.sleep(2)
            
            # Verify earnings content is displayed
            earnings_content = self.driver.find_element(By.XPATH, "//th[contains(text(), 'Date')] | //th[contains(text(), 'Amount')]")
            self.assertTrue(earnings_content.is_displayed(), "Earnings content not displayed")
            
            # Go back to My Properties tab
            my_properties_tab = self.driver.find_element(By.XPATH, "//button[contains(text(), 'My Properties')]")
            my_properties_tab.click()
            time.sleep(2)
            
            # Verify we're back to properties view
            properties_content = self.driver.find_element(By.XPATH, "//th[contains(text(), 'Property')] | //button[contains(text(), '+ Add New Property')]")
            self.assertTrue(properties_content.is_displayed(), "My Properties content not displayed")
            
        except TimeoutException:
            self.fail("Landlord dashboard tabs navigation test failed")
        
        print("Landlord dashboard tabs navigation test passed!")

    def test_landlord_viewing_requests_confirm_functionality(self):
        """Test the confirm viewing request functionality in landlord dashboard"""
        print("Testing landlord viewing requests confirm functionality...")
        
        try:
            # Navigate to landlord dashboard
            self.driver.get(f"{self.base_url}/landlord")
            time.sleep(3)
            
            # Click on Viewing Requests tab
            viewing_requests_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Viewing Requests')]"))
            )
            viewing_requests_tab.click()
            time.sleep(2)
            
            # Verify viewing requests content is displayed
            viewing_requests_content = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'Property')] | //th[contains(text(), 'Tenant Details')]"))
            )
            self.assertTrue(viewing_requests_content.is_displayed(), "Viewing Requests content not displayed")
            
            # Find a pending viewing request and click confirm
            confirm_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Confirm') and contains(@class, 'bg-green-500')]")
            if confirm_buttons:
                initial_button_count = len(confirm_buttons)
                confirm_buttons[0].click()
                time.sleep(1)
                
                # Handle the alert
                try:
                    alert = WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                    alert_text = alert.text
                    self.assertIn("confirmed successfully", alert_text.lower(), "Confirm alert message not correct")
                    alert.accept()
                    time.sleep(1)
                    
                    # Verify the status changed (button should be gone or changed)
                    updated_confirm_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Confirm') and contains(@class, 'bg-green-500')]")
                    self.assertLess(len(updated_confirm_buttons), initial_button_count, "Confirm button should be removed after confirmation")
                    
                except TimeoutException:
                    self.fail("Confirm alert not displayed")
            else:
                print("No pending viewing requests found to test confirm functionality")
            
        except TimeoutException:
            self.fail("Landlord viewing requests confirm functionality test failed")
        
        print("Landlord viewing requests confirm functionality test passed!")

    def test_landlord_viewing_requests_decline_functionality(self):
        """Test the decline viewing request functionality in landlord dashboard"""
        print("Testing landlord viewing requests decline functionality...")
        
        try:
            # Navigate to landlord dashboard
            self.driver.get(f"{self.base_url}/landlord")
            time.sleep(3)
            
            # Click on Viewing Requests tab
            viewing_requests_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Viewing Requests')]"))
            )
            viewing_requests_tab.click()
            time.sleep(2)
            
            # Find a pending viewing request and click decline
            decline_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Decline') and contains(@class, 'bg-red-500')]")
            if decline_buttons:
                initial_button_count = len(decline_buttons)
                decline_buttons[0].click()
                time.sleep(1)
                
                # Handle the alert
                try:
                    alert = WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                    alert_text = alert.text
                    self.assertIn("declined successfully", alert_text.lower(), "Decline alert message not correct")
                    alert.accept()
                    time.sleep(1)
                    
                    # Verify the status changed (button should be gone or changed)
                    updated_decline_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Decline') and contains(@class, 'bg-red-500')]")
                    self.assertLess(len(updated_decline_buttons), initial_button_count, "Decline button should be removed after declining")
                    
                except TimeoutException:
                    self.fail("Decline alert not displayed")
            else:
                print("No pending viewing requests found to test decline functionality")
            
        except TimeoutException:
            self.fail("Landlord viewing requests decline functionality test failed")
        
        print("Landlord viewing requests decline functionality test passed!")

    def test_landlord_viewing_requests_status_updates(self):
        """Test that viewing request status updates are reflected in the UI"""
        print("Testing landlord viewing requests status updates...")
        
        try:
            # Navigate to landlord dashboard
            self.driver.get(f"{self.base_url}/landlord")
            time.sleep(3)
            
            # Click on Viewing Requests tab
            viewing_requests_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Viewing Requests')]"))
            )
            viewing_requests_tab.click()
            time.sleep(2)
            
            # Check for different status badges
            status_badges = self.driver.find_elements(By.XPATH, "//span[contains(@class, 'rounded-full') and (contains(text(), 'Pending') or contains(text(), 'Confirmed') or contains(text(), 'Declined'))]")
            self.assertGreater(len(status_badges), 0, "No status badges found")
            
            # Verify status colors
            for badge in status_badges:
                status_text = badge.text
                badge_classes = badge.get_attribute("class")
                
                if status_text == "Confirmed":
                    self.assertIn("bg-green-100", badge_classes, "Confirmed status should have green background")
                elif status_text == "Pending":
                    self.assertIn("bg-yellow-100", badge_classes, "Pending status should have yellow background")
                elif status_text == "Declined":
                    self.assertIn("bg-red-100", badge_classes, "Declined status should have red background")
            
        except TimeoutException:
            self.fail("Landlord viewing requests status updates test failed")
        
        print("Landlord viewing requests status updates test passed!")

    def test_landlord_tenant_applications_approve_functionality(self):
        """Test the approve tenant application functionality in landlord dashboard"""
        print("Testing landlord tenant applications approve functionality...")
        
        try:
            # Navigate to landlord dashboard
            self.driver.get(f"{self.base_url}/landlord")
            time.sleep(3)
            
            # Click on Tenant Applications tab
            applications_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Tenant Applications')]"))
            )
            applications_tab.click()
            time.sleep(2)
            
            # Verify tenant applications content is displayed
            applications_content = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'Tenant')] | //th[contains(text(), 'Property')]"))
            )
            self.assertTrue(applications_content.is_displayed(), "Tenant Applications content not displayed")
            
            # Find an "Under Review" application and click approve
            approve_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Approve') and contains(@class, 'bg-green-500')]")
            if approve_buttons:
                initial_button_count = len(approve_buttons)
                approve_buttons[0].click()
                time.sleep(1)
                
                # Handle the alert
                try:
                    alert = WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                    alert_text = alert.text
                    self.assertIn("approved successfully", alert_text.lower(), "Approve alert message not correct")
                    alert.accept()
                    time.sleep(1)
                    
                    # Verify the status changed (button should be gone)
                    updated_approve_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Approve') and contains(@class, 'bg-green-500')]")
                    self.assertLess(len(updated_approve_buttons), initial_button_count, "Approve button should be removed after approval")
                    
                except TimeoutException:
                    self.fail("Approve alert not displayed")
            else:
                print("No applications under review found to test approve functionality")
            
        except TimeoutException:
            self.fail("Landlord tenant applications approve functionality test failed")
        
        print("Landlord tenant applications approve functionality test passed!")

    def test_landlord_tenant_applications_reject_functionality(self):
        """Test the reject tenant application functionality in landlord dashboard"""
        print("Testing landlord tenant applications reject functionality...")
        
        try:
            # Navigate to landlord dashboard
            self.driver.get(f"{self.base_url}/landlord")
            time.sleep(3)
            
            # Click on Tenant Applications tab
            applications_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Tenant Applications')]"))
            )
            applications_tab.click()
            time.sleep(2)
            
            # Find an "Under Review" application and click reject
            reject_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Reject') and contains(@class, 'bg-red-500')]")
            if reject_buttons:
                initial_button_count = len(reject_buttons)
                reject_buttons[0].click()
                time.sleep(1)
                
                # Handle the alert
                try:
                    alert = WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                    alert_text = alert.text
                    self.assertIn("rejected successfully", alert_text.lower(), "Reject alert message not correct")
                    alert.accept()
                    time.sleep(1)
                    
                    # Verify the status changed (button should be gone)
                    updated_reject_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Reject') and contains(@class, 'bg-red-500')]")
                    self.assertLess(len(updated_reject_buttons), initial_button_count, "Reject button should be removed after rejection")
                    
                except TimeoutException:
                    self.fail("Reject alert not displayed")
            else:
                print("No applications under review found to test reject functionality")
            
        except TimeoutException:
            self.fail("Landlord tenant applications reject functionality test failed")
        
        print("Landlord tenant applications reject functionality test passed!")

    def test_landlord_tenant_applications_view_details_functionality(self):
        """Test the view details functionality for tenant applications"""
        print("Testing landlord tenant applications view details functionality...")
        
        try:
            # Navigate to landlord dashboard
            self.driver.get(f"{self.base_url}/landlord")
            time.sleep(3)
            
            # Click on Tenant Applications tab
            applications_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Tenant Applications')]"))
            )
            applications_tab.click()
            time.sleep(2)
            
            # Find and click a "View Details" button
            view_details_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'View Details')]")
            if view_details_buttons:
                view_details_buttons[0].click()
                time.sleep(2)
                
                # Verify the modal opened
                modal_title = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Tenant Application Details')]"))
                )
                self.assertTrue(modal_title.is_displayed(), "Application details modal not displayed")
                
                # Verify modal content sections
                property_info = self.driver.find_element(By.XPATH, "//h4[contains(text(), 'Property Information')]")
                self.assertTrue(property_info.is_displayed(), "Property Information section not displayed")
                
                tenant_info = self.driver.find_element(By.XPATH, "//h4[contains(text(), 'Tenant Information')]")
                self.assertTrue(tenant_info.is_displayed(), "Tenant Information section not displayed")
                
                employment_info = self.driver.find_element(By.XPATH, "//h4[contains(text(), 'Employment Information')]")
                self.assertTrue(employment_info.is_displayed(), "Employment Information section not displayed")
                
                application_details = self.driver.find_element(By.XPATH, "//h4[contains(text(), 'Application Details')]")
                self.assertTrue(application_details.is_displayed(), "Application Details section not displayed")
                
                # Close the modal
                close_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Close')]")
                close_button.click()
                time.sleep(1)
                
                # Verify modal is closed
                try:
                    modal_title = self.driver.find_element(By.XPATH, "//h3[contains(text(), 'Tenant Application Details')]")
                    self.assertFalse(modal_title.is_displayed(), "Modal should be closed")
                except:
                    pass  # Modal is properly closed
                
            else:
                self.fail("No View Details buttons found")
            
        except TimeoutException:
            self.fail("Landlord tenant applications view details functionality test failed")
        
        print("Landlord tenant applications view details functionality test passed!")

    def test_landlord_tenant_applications_status_updates(self):
        """Test that tenant application status updates are reflected in the UI"""
        print("Testing landlord tenant applications status updates...")
        
        try:
            # Navigate to landlord dashboard
            self.driver.get(f"{self.base_url}/landlord")
            time.sleep(3)
            
            # Click on Tenant Applications tab
            applications_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Tenant Applications')]"))
            )
            applications_tab.click()
            time.sleep(2)
            
            # Check for different status badges
            status_badges = self.driver.find_elements(By.XPATH, "//span[contains(@class, 'rounded-full') and (contains(text(), 'Under Review') or contains(text(), 'Approved') or contains(text(), 'Rejected'))]")
            self.assertGreater(len(status_badges), 0, "No status badges found")
            
            # Verify status colors
            for badge in status_badges:
                status_text = badge.text
                badge_classes = badge.get_attribute("class")
                
                if status_text == "Approved":
                    self.assertIn("bg-green-100", badge_classes, "Approved status should have green background")
                elif status_text == "Under Review":
                    self.assertIn("bg-yellow-100", badge_classes, "Under Review status should have yellow background")
                elif status_text == "Rejected":
                    self.assertIn("bg-red-100", badge_classes, "Rejected status should have red background")
            
        except TimeoutException:
            self.fail("Landlord tenant applications status updates test failed")
        
        print("Landlord tenant applications status updates test passed!")

    def test_landlord_my_properties_row_click_navigation(self):
        """Test that clicking a property row navigates to the property listing page"""
        print("Testing landlord my properties row click navigation...")
        
        try:
            # Navigate to landlord dashboard
            self.driver.get(f"{self.base_url}/landlord")
            time.sleep(3)
            
            # Click on My Properties tab (if not already active)
            my_properties_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'My Properties')]"))
            )
            my_properties_tab.click()
            time.sleep(2)
            
            # Find the first property row (excluding header and action buttons)
            # We need to be careful not to click on the action buttons within the row
            # So we'll click on a specific cell within the row that is not a button
            property_row_cell = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//tbody/tr[1]/td[1]")) # First cell of the first row
            )
            property_row_cell.click()
            time.sleep(3)
            
            # Verify navigation to property detail page
            # The URL should change to something like /property/{id}
            current_url = self.driver.current_url
            self.assertRegex(current_url, r"/property/\d+", "Did not navigate to property detail page")
            
        except TimeoutException:
            self.fail("Landlord my properties row click navigation test failed")
        
        print("Landlord my properties row click navigation test passed!")

    def test_landlord_my_properties_edit_button_functionality(self):
        """Test that Edit buttons work independently of row clicks"""
        print("Testing landlord my properties edit button functionality...")
        
        try:
            # Navigate to landlord dashboard
            self.driver.get(f"{self.base_url}/landlord")
            time.sleep(3)
            
            # Click on My Properties tab (if not already active)
            my_properties_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'My Properties')]"))
            )
            my_properties_tab.click()
            time.sleep(2)
            
            # Find and click the first Edit button
            edit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Edit')]"))
            )
            edit_button.click()
            time.sleep(2)
            
            # Verify the edit modal opened (should not navigate to property page)
            edit_modal = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Edit Property')]"))
            )
            self.assertTrue(edit_modal.is_displayed(), "Edit modal not displayed")
            
            # Verify we're still on the landlord dashboard page
            current_url = self.driver.current_url
            self.assertIn("/landlord", current_url, "Should still be on landlord dashboard")
            self.assertNotRegex(current_url, r"/property/\d+", "Should not navigate to property detail page")
            
            # Close the modal
            close_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
            close_button.click()
            time.sleep(1)
            
        except TimeoutException:
            self.fail("Landlord my properties edit button functionality test failed")
        
        print("Landlord my properties edit button functionality test passed!")

    def test_landlord_my_properties_status_dropdown_functionality(self):
        """Test that Status dropdown works independently of row clicks"""
        print("Testing landlord my properties status dropdown functionality...")
        
        try:
            # Navigate to landlord dashboard
            self.driver.get(f"{self.base_url}/landlord")
            time.sleep(3)
            
            # Click on My Properties tab (if not already active)
            my_properties_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'My Properties')]"))
            )
            my_properties_tab.click()
            time.sleep(2)
            
            # Find the first status dropdown
            status_dropdown = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//select[contains(@class, 'text-gray-600')]"))
            )
            
            # Get the current value
            current_value = status_dropdown.get_attribute("value")
            
            # Click on the dropdown (should not trigger row navigation)
            status_dropdown.click()
            time.sleep(1)
            
            # Change the status
            if current_value == "Active":
                status_dropdown.send_keys("Inactive")
            else:
                status_dropdown.send_keys("Active")
            
            time.sleep(2)
            
            # Verify we're still on the landlord dashboard page
            current_url = self.driver.current_url
            self.assertIn("/landlord", current_url, "Should still be on landlord dashboard")
            self.assertNotRegex(current_url, r"/property/\d+", "Should not navigate to property detail page")
            
        except TimeoutException:
            self.fail("Landlord my properties status dropdown functionality test failed")
        
        print("Landlord my properties status dropdown functionality test passed!")

if __name__ == "__main__":
    unittest.main()
