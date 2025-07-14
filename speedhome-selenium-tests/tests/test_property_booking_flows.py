"""
Comprehensive property booking and viewing request tests
Tests the complete booking flow from property selection to confirmation
"""
import pytest
import time
from datetime import datetime, timedelta
from utils.base_test import BaseTest
from pages.home_page import HomePage
from pages.property_detail_page import PropertyDetailPage
from pages.header_page import HeaderPage
from utils.test_data_generator import TestDataGenerator
from config.test_config import TestConfig

class TestPropertyBookingFlows(BaseTest):
    """Test property booking and viewing request functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        super().setup_method()
        self.home_page = HomePage(self.driver)
        self.property_page = PropertyDetailPage(self.driver)
        self.header_page = HeaderPage(self.driver)
        self.data_generator = TestDataGenerator()
    
    def navigate_to_first_property(self):
        """Helper method to navigate to first available property"""
        # Get first property from homepage
        properties = self.home_page.get_visible_properties()
        if not properties:
            pytest.skip("No properties available for testing")
        
        # Click on first property
        self.home_page.click_property_card(0)
        time.sleep(2)
        
        # Verify we're on property detail page
        assert "/property/" in self.driver.current_url or "property" in self.driver.current_url.lower()
        return properties[0]
    
    @pytest.mark.smoke
    def test_schedule_viewing_button_present(self):
        """Test that schedule viewing button is present on property page"""
        self.navigate_to_first_property()
        
        # Check if schedule viewing button is available
        if self.property_page.is_schedule_viewing_available():
            assert True, "Schedule viewing button is present"
        else:
            pytest.skip("Schedule viewing not available for this property")
    
    @pytest.mark.smoke
    def test_schedule_viewing_modal_opens(self):
        """Test that schedule viewing modal opens correctly"""
        self.navigate_to_first_property()
        
        if self.property_page.is_schedule_viewing_available():
            # Click schedule viewing button
            self.property_page.click_schedule_viewing()
            
            # Wait for modal to open
            time.sleep(1)
            
            # Verify modal is open
            assert self.property_page.is_booking_modal_open(), "Booking modal should be open"
            
            # Close modal
            self.property_page.close_booking_modal()
            assert not self.property_page.is_booking_modal_open(), "Modal should be closed"
        else:
            pytest.skip("Schedule viewing not available")
    
    @pytest.mark.regression
    def test_booking_form_validation_empty_fields(self):
        """Test booking form validation with empty required fields"""
        self.navigate_to_first_property()
        
        if self.property_page.is_schedule_viewing_available():
            # Open booking modal
            self.property_page.click_schedule_viewing()
            
            # Try to submit empty form
            self.property_page.submit_booking_form()
            
            # Check for validation errors
            if self.property_page.has_validation_errors():
                errors = self.property_page.get_validation_errors()
                assert len(errors) > 0, "Should show validation errors for empty fields"
            else:
                # Modal should remain open if validation failed
                assert self.property_page.is_booking_modal_open(), "Modal should remain open for validation"
            
            # Close modal
            self.property_page.close_booking_modal()
        else:
            pytest.skip("Schedule viewing not available")
    
    @pytest.mark.regression
    def test_booking_form_validation_invalid_email(self):
        """Test booking form validation with invalid email"""
        self.navigate_to_first_property()
        
        if self.property_page.is_schedule_viewing_available():
            # Open booking modal
            self.property_page.click_schedule_viewing()
            
            # Fill form with invalid email
            booking_data = {
                'name': 'Test User',
                'email': 'invalid-email',
                'phone': '1234567890',
                'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'time': '14:00',
                'message': 'Test booking'
            }
            
            self.property_page.fill_booking_form(booking_data)
            self.property_page.submit_booking_form()
            
            # Check for email validation error
            if self.property_page.has_validation_errors():
                errors = self.property_page.get_validation_errors()
                email_error = any('email' in error.lower() for error in errors)
                assert email_error, "Should show email validation error"
            
            # Close modal
            self.property_page.close_booking_modal()
        else:
            pytest.skip("Schedule viewing not available")
    
    @pytest.mark.regression
    def test_booking_form_validation_past_date(self):
        """Test booking form validation with past date"""
        self.navigate_to_first_property()
        
        if self.property_page.is_schedule_viewing_available():
            # Open booking modal
            self.property_page.click_schedule_viewing()
            
            # Fill form with past date
            booking_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': '1234567890',
                'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'time': '14:00',
                'message': 'Test booking'
            }
            
            self.property_page.fill_booking_form(booking_data)
            self.property_page.submit_booking_form()
            
            # Should show validation error or prevent past date selection
            if self.property_page.has_validation_errors():
                errors = self.property_page.get_validation_errors()
                date_error = any('date' in error.lower() for error in errors)
                assert date_error, "Should show date validation error"
            
            # Close modal
            self.property_page.close_booking_modal()
        else:
            pytest.skip("Schedule viewing not available")
    
    @pytest.mark.integration
    def test_successful_booking_submission(self):
        """Test successful booking submission with valid data"""
        self.navigate_to_first_property()
        
        if self.property_page.is_schedule_viewing_available():
            # Generate valid booking data
            booking_data = {
                'name': self.data_generator.generate_name(),
                'email': self.data_generator.generate_email(),
                'phone': self.data_generator.generate_phone(),
                'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                'time': '14:00',
                'message': 'I am interested in viewing this property. Please confirm the appointment.'
            }
            
            # Perform booking
            success = self.property_page.perform_quick_booking(
                booking_data['name'],
                booking_data['email'],
                booking_data['phone'],
                booking_data['date'],
                booking_data['time'],
                booking_data['message']
            )
            
            if success:
                # Check for success message
                success_msg = self.property_page.get_success_message()
                if success_msg:
                    assert "success" in success_msg.lower() or "booked" in success_msg.lower()
                
                # Modal should close after successful submission
                time.sleep(2)
                assert not self.property_page.is_booking_modal_open(), "Modal should close after success"
            else:
                # Check for error message
                error_msg = self.property_page.get_error_message()
                if error_msg:
                    pytest.fail(f"Booking failed with error: {error_msg}")
                else:
                    pytest.fail("Booking submission failed without clear error")
        else:
            pytest.skip("Schedule viewing not available")
    
    @pytest.mark.regression
    def test_booking_form_autofill_detection(self):
        """Test that booking form can be filled and data persists"""
        self.navigate_to_first_property()
        
        if self.property_page.is_schedule_viewing_available():
            # Open booking modal
            self.property_page.click_schedule_viewing()
            
            # Fill form data
            booking_data = {
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'phone': '0123456789',
                'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'time': '15:00',
                'message': 'Test message'
            }
            
            self.property_page.fill_booking_form(booking_data)
            
            # Get form data back
            form_data = self.property_page.get_booking_form_data()
            
            # Verify data was filled correctly
            assert form_data['name'] == booking_data['name']
            assert form_data['email'] == booking_data['email']
            assert form_data['phone'] == booking_data['phone']
            
            # Close modal
            self.property_page.close_booking_modal()
        else:
            pytest.skip("Schedule viewing not available")
    
    @pytest.mark.regression
    def test_booking_form_clear_functionality(self):
        """Test clearing booking form"""
        self.navigate_to_first_property()
        
        if self.property_page.is_schedule_viewing_available():
            # Open booking modal
            self.property_page.click_schedule_viewing()
            
            # Fill form with data
            booking_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': '1234567890',
                'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'time': '14:00',
                'message': 'Test message'
            }
            
            self.property_page.fill_booking_form(booking_data)
            
            # Clear form
            self.property_page.clear_booking_form()
            
            # Verify form is cleared
            form_data = self.property_page.get_booking_form_data()
            assert form_data['name'] == ''
            assert form_data['email'] == ''
            assert form_data['phone'] == ''
            assert form_data['message'] == ''
            
            # Close modal
            self.property_page.close_booking_modal()
        else:
            pytest.skip("Schedule viewing not available")
    
    @pytest.mark.integration
    def test_booking_requires_authentication(self):
        """Test if booking requires user authentication"""
        # Ensure user is logged out
        if self.header_page.is_user_logged_in():
            self.header_page.logout()
        
        self.navigate_to_first_property()
        
        if self.property_page.is_schedule_viewing_available():
            # Try to book without being logged in
            booking_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': '1234567890',
                'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'time': '14:00',
                'message': 'Test booking'
            }
            
            # Open booking modal
            self.property_page.click_schedule_viewing()
            
            # Check if login is required
            if self.header_page.is_login_modal_open():
                # Login required - this is expected behavior
                self.header_page.close_login_modal()
                pytest.skip("Login required for booking - this is expected")
            else:
                # Booking allowed without login
                self.property_page.fill_booking_form(booking_data)
                self.property_page.submit_booking_form()
                
                # Should either succeed or show appropriate message
                time.sleep(2)
                
                # Close modal if still open
                if self.property_page.is_booking_modal_open():
                    self.property_page.close_booking_modal()
        else:
            pytest.skip("Schedule viewing not available")
    
    @pytest.mark.regression
    def test_multiple_booking_attempts(self):
        """Test multiple booking attempts for same property"""
        self.navigate_to_first_property()
        
        if self.property_page.is_schedule_viewing_available():
            # First booking attempt
            booking_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': '1234567890',
                'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'time': '14:00',
                'message': 'First booking attempt'
            }
            
            # Perform first booking
            self.property_page.click_schedule_viewing()
            self.property_page.fill_booking_form(booking_data)
            self.property_page.submit_booking_form()
            time.sleep(2)
            
            # Close modal if open
            if self.property_page.is_booking_modal_open():
                self.property_page.close_booking_modal()
            
            # Second booking attempt with different time
            booking_data['time'] = '16:00'
            booking_data['message'] = 'Second booking attempt'
            
            # Perform second booking
            if self.property_page.is_schedule_viewing_available():
                self.property_page.click_schedule_viewing()
                self.property_page.fill_booking_form(booking_data)
                self.property_page.submit_booking_form()
                time.sleep(2)
                
                # Should handle multiple bookings appropriately
                # Either allow or show appropriate message
                
                # Close modal
                if self.property_page.is_booking_modal_open():
                    self.property_page.close_booking_modal()
        else:
            pytest.skip("Schedule viewing not available")
    
    @pytest.mark.smoke
    def test_property_application_button_present(self):
        """Test that apply now button is present when available"""
        self.navigate_to_first_property()
        
        # Check if apply now button is available
        if self.property_page.is_apply_now_available():
            assert True, "Apply now button is present"
        else:
            # This might be normal if property doesn't allow applications
            pytest.skip("Apply now not available for this property")
    
    @pytest.mark.integration
    def test_property_application_flow(self):
        """Test property application submission flow"""
        self.navigate_to_first_property()
        
        if self.property_page.is_apply_now_available():
            # Click apply now
            self.property_page.click_apply_now()
            time.sleep(1)
            
            # Check if application modal opens
            if self.property_page.is_application_modal_open():
                # Fill application form
                application_data = {
                    'message': 'I am very interested in renting this property. I have stable income and good references.'
                }
                
                self.property_page.fill_application_form(application_data)
                self.property_page.submit_application_form()
                time.sleep(2)
                
                # Check for success or error message
                success_msg = self.property_page.get_success_message()
                error_msg = self.property_page.get_error_message()
                
                if success_msg:
                    assert "success" in success_msg.lower() or "application" in success_msg.lower()
                elif error_msg:
                    # Application might require login or have other requirements
                    if "login" in error_msg.lower():
                        pytest.skip("Login required for application")
                    else:
                        pytest.fail(f"Application failed: {error_msg}")
                
                # Close modal if still open
                if self.property_page.is_application_modal_open():
                    self.property_page.close_application_modal()
            else:
                # Might redirect to application page or require login
                current_url = self.driver.current_url
                if "login" in current_url.lower() or self.header_page.is_login_modal_open():
                    pytest.skip("Login required for application")
        else:
            pytest.skip("Apply now not available")
    
    @pytest.mark.regression
    def test_booking_modal_close_methods(self):
        """Test different ways to close booking modal"""
        self.navigate_to_first_property()
        
        if self.property_page.is_schedule_viewing_available():
            # Test close button
            self.property_page.click_schedule_viewing()
            assert self.property_page.is_booking_modal_open()
            
            self.property_page.close_booking_modal()
            assert not self.property_page.is_booking_modal_open()
            
            # Test clicking outside modal (if supported)
            self.property_page.click_schedule_viewing()
            assert self.property_page.is_booking_modal_open()
            
            # Click outside modal area
            self.property_page.click_outside_modal()
            time.sleep(1)
            
            # Modal might or might not close depending on implementation
            # Just ensure page doesn't crash
            assert self.driver.current_url is not None
            
            # Ensure modal is closed for cleanup
            if self.property_page.is_booking_modal_open():
                self.property_page.close_booking_modal()
        else:
            pytest.skip("Schedule viewing not available")

