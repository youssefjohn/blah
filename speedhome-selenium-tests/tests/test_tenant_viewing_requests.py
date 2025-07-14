"""
Test cases for tenant viewing request functionality
"""
import pytest
import time
from datetime import datetime, timedelta
from utils.base_test import BaseTest
from pages.header_page import HeaderPage
from pages.home_page import HomePage
from pages.property_detail_page import PropertyDetailPage
from pages.user_dashboard_page import UserDashboardPage
from utils.test_data_generator import TestDataGenerator
from config.test_config import TestConfig

class TestTenantViewingRequests(BaseTest):
    """Test tenant viewing request functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        super().setup_method()
        self.header_page = HeaderPage(self.driver)
        self.home_page = HomePage(self.driver)
        self.property_detail_page = PropertyDetailPage(self.driver)
        self.user_dashboard_page = UserDashboardPage(self.driver)
        self.data_generator = TestDataGenerator()
        
        # Login as tenant for tests
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
        assert self.header_page.is_user_logged_in(), "Should be logged in for viewing request tests"
    
    def test_schedule_viewing_success(self):
        """Test successful viewing request scheduling"""
        # Navigate to a property
        self.home_page.click_first_property()
        self.property_detail_page.wait_for_property_to_load()
        
        # Check if viewing can be scheduled (button should be enabled)
        if self.property_detail_page.is_viewing_requested():
            pytest.skip("Property already has viewing requested")
        
        # Generate booking data
        booking_data = self.data_generator.generate_booking_data()
        
        # Schedule viewing
        success = self.property_detail_page.schedule_viewing(booking_data)
        
        # Verify success
        assert success, "Viewing scheduling should be successful"
        
        # Verify button state changed
        assert self.property_detail_page.is_viewing_requested(), \
            "Button should show viewing requested state"
        
        # Verify viewing appears in dashboard
        self.header_page.click_tenant_button()
        self.user_dashboard_page.wait_for_dashboard_to_load()
        
        # Check viewing requests section
        self.user_dashboard_page.scroll_to_viewing_requests()
        assert self.user_dashboard_page.has_viewing_requests(), \
            "Should have viewing requests in dashboard"
        
        # Verify request details
        request_details = self.user_dashboard_page.get_viewing_request_details(0)
        assert request_details is not None, "Should get viewing request details"
        assert request_details['status'] == 'Pending', "Status should be Pending"
    
    def test_schedule_viewing_form_validation(self):
        """Test viewing request form validation"""
        # Navigate to a property
        self.home_page.click_first_property()
        self.property_detail_page.wait_for_property_to_load()
        
        if self.property_detail_page.is_viewing_requested():
            pytest.skip("Property already has viewing requested")
        
        # Open booking modal
        self.property_detail_page.click_schedule_viewing()
        
        # Try to submit with empty required fields
        self.property_detail_page.click_element(
            self.property_detail_page.BOOKING_SUBMIT_BUTTON
        )
        
        # Verify form doesn't submit (modal should still be open)
        assert self.property_detail_page.is_element_visible(
            self.property_detail_page.BOOKING_MODAL
        ), "Modal should remain open on validation error"
        
        # Test with invalid email
        invalid_booking_data = {
            'name': 'Test User',
            'email': 'invalid-email',
            'phone': '123456789',
            'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '14:00'
        }
        
        self.property_detail_page.fill_booking_form(invalid_booking_data)
        self.property_detail_page.click_element(
            self.property_detail_page.BOOKING_SUBMIT_BUTTON
        )
        
        # Should still be on modal due to validation
        assert self.property_detail_page.is_element_visible(
            self.property_detail_page.BOOKING_MODAL
        ), "Modal should remain open on email validation error"
        
        # Close modal
        self.property_detail_page.close_booking_modal()
    
    def test_schedule_viewing_past_date_validation(self):
        """Test that past dates are not allowed for viewing requests"""
        # Navigate to a property
        self.home_page.click_first_property()
        self.property_detail_page.wait_for_property_to_load()
        
        if self.property_detail_page.is_viewing_requested():
            pytest.skip("Property already has viewing requested")
        
        # Open booking modal
        self.property_detail_page.click_schedule_viewing()
        
        # Try to book with past date
        past_date_booking = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '123456789',
            'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '14:00'
        }
        
        self.property_detail_page.fill_booking_form(past_date_booking)
        success = self.property_detail_page.submit_booking()
        
        # Should fail validation
        assert not success, "Should not allow booking with past date"
        
        self.property_detail_page.close_booking_modal()
    
    def test_cancel_viewing_request_modal(self):
        """Test canceling viewing request from modal"""
        # Navigate to a property
        self.home_page.click_first_property()
        self.property_detail_page.wait_for_property_to_load()
        
        if self.property_detail_page.is_viewing_requested():
            pytest.skip("Property already has viewing requested")
        
        # Open booking modal
        self.property_detail_page.click_schedule_viewing()
        
        # Fill some data
        booking_data = self.data_generator.generate_booking_data()
        self.property_detail_page.fill_booking_form(booking_data)
        
        # Cancel booking
        self.property_detail_page.cancel_booking()
        
        # Verify modal is closed
        assert not self.property_detail_page.is_element_visible(
            self.property_detail_page.BOOKING_MODAL
        ), "Modal should be closed after cancel"
        
        # Verify no viewing was scheduled
        assert not self.property_detail_page.is_viewing_requested(), \
            "Should not show viewing requested after cancel"
    
    def test_viewing_request_with_optional_fields(self):
        """Test viewing request with all optional fields filled"""
        # Navigate to a property
        self.home_page.click_first_property()
        self.property_detail_page.wait_for_property_to_load()
        
        if self.property_detail_page.is_viewing_requested():
            pytest.skip("Property already has viewing requested")
        
        # Generate comprehensive booking data
        booking_data = self.data_generator.generate_booking_data()
        
        # Schedule viewing with all fields
        success = self.property_detail_page.schedule_viewing(booking_data)
        
        assert success, "Viewing scheduling with optional fields should be successful"
        assert self.property_detail_page.is_viewing_requested(), \
            "Should show viewing requested state"
    
    def test_multiple_viewing_requests_same_property(self):
        """Test that multiple viewing requests for same property are not allowed"""
        # Navigate to a property
        self.home_page.click_first_property()
        self.property_detail_page.wait_for_property_to_load()
        
        # If already requested, test is valid
        if self.property_detail_page.is_viewing_requested():
            # Try to click schedule viewing button (should be disabled)
            assert not self.property_detail_page.is_element_visible(
                self.property_detail_page.SCHEDULE_VIEWING_BUTTON
            ), "Schedule viewing button should not be available"
            return
        
        # Schedule first viewing
        booking_data = self.data_generator.generate_booking_data()
        success = self.property_detail_page.schedule_viewing(booking_data)
        assert success, "First viewing request should succeed"
        
        # Refresh page to ensure state is persisted
        self.property_detail_page.refresh_page()
        self.property_detail_page.wait_for_property_to_load()
        
        # Verify cannot schedule another viewing
        assert self.property_detail_page.is_viewing_requested(), \
            "Should show viewing already requested"
        assert not self.property_detail_page.is_element_visible(
            self.property_detail_page.SCHEDULE_VIEWING_BUTTON
        ), "Schedule viewing button should not be available"
    
    def test_viewing_request_dashboard_display(self):
        """Test viewing request display in tenant dashboard"""
        # First schedule a viewing if none exists
        self.home_page.click_first_property()
        self.property_detail_page.wait_for_property_to_load()
        
        property_title = self.property_detail_page.get_property_title()
        
        if not self.property_detail_page.is_viewing_requested():
            booking_data = self.data_generator.generate_booking_data()
            success = self.property_detail_page.schedule_viewing(booking_data)
            assert success, "Should schedule viewing for dashboard test"
        
        # Navigate to dashboard
        self.header_page.click_tenant_button()
        self.user_dashboard_page.wait_for_dashboard_to_load()
        
        # Check viewing requests section
        self.user_dashboard_page.scroll_to_viewing_requests()
        assert self.user_dashboard_page.has_viewing_requests(), \
            "Should have viewing requests"
        
        # Verify request details
        request_details = self.user_dashboard_page.get_viewing_request_details(0)
        assert request_details is not None, "Should get request details"
        assert property_title in request_details['property_title'], \
            "Property title should match"
        assert request_details['status'] in ['Pending', 'Confirmed', 'Declined'], \
            "Should have valid status"
        assert request_details['date'], "Should have date"
        assert request_details['time'], "Should have time"
    
    def test_reschedule_viewing_request(self):
        """Test rescheduling a viewing request"""
        # Navigate to dashboard
        self.header_page.click_tenant_button()
        self.user_dashboard_page.wait_for_dashboard_to_load()
        self.user_dashboard_page.scroll_to_viewing_requests()
        
        if not self.user_dashboard_page.has_viewing_requests():
            pytest.skip("No viewing requests to reschedule")
        
        # Get original request details
        original_details = self.user_dashboard_page.get_viewing_request_details(0)
        
        # Generate new date/time
        new_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        new_time = '15:30'
        
        # Reschedule the request
        success = self.user_dashboard_page.reschedule_viewing_request(0, new_date, new_time)
        
        if success:
            # Wait for update
            time.sleep(2)
            self.user_dashboard_page.refresh_page()
            self.user_dashboard_page.wait_for_dashboard_to_load()
            self.user_dashboard_page.scroll_to_viewing_requests()
            
            # Verify status changed to reschedule requested
            updated_details = self.user_dashboard_page.get_viewing_request_details(0)
            assert 'Reschedule' in updated_details['status'], \
                "Status should indicate reschedule requested"
    
    def test_cancel_viewing_request_from_dashboard(self):
        """Test canceling viewing request from dashboard"""
        # Navigate to dashboard
        self.header_page.click_tenant_button()
        self.user_dashboard_page.wait_for_dashboard_to_load()
        self.user_dashboard_page.scroll_to_viewing_requests()
        
        if not self.user_dashboard_page.has_viewing_requests():
            pytest.skip("No viewing requests to cancel")
        
        # Get initial count
        initial_count = self.user_dashboard_page.get_viewing_request_count()
        
        # Cancel first request
        success = self.user_dashboard_page.cancel_viewing_request(0)
        
        if success:
            # Wait for update
            time.sleep(2)
            self.user_dashboard_page.refresh_page()
            self.user_dashboard_page.wait_for_dashboard_to_load()
            self.user_dashboard_page.scroll_to_viewing_requests()
            
            # Verify request was removed
            new_count = self.user_dashboard_page.get_viewing_request_count()
            assert new_count == initial_count - 1, \
                "Viewing request count should decrease after cancellation"
    
    def test_viewing_request_status_updates(self):
        """Test that viewing request status updates are reflected"""
        # Navigate to dashboard
        self.header_page.click_tenant_button()
        self.user_dashboard_page.wait_for_dashboard_to_load()
        self.user_dashboard_page.scroll_to_viewing_requests()
        
        if not self.user_dashboard_page.has_viewing_requests():
            pytest.skip("No viewing requests to check status")
        
        # Get current status
        request_details = self.user_dashboard_page.get_viewing_request_details(0)
        current_status = request_details['status']
        
        # Verify status is one of expected values
        expected_statuses = ['Pending', 'Confirmed', 'Declined', 'Reschedule Requested', 'Reschedule Proposed']
        assert current_status in expected_statuses, \
            f"Status '{current_status}' should be one of {expected_statuses}"
        
        # Refresh and verify status persists
        self.user_dashboard_page.refresh_page()
        self.user_dashboard_page.wait_for_dashboard_to_load()
        self.user_dashboard_page.scroll_to_viewing_requests()
        
        refreshed_details = self.user_dashboard_page.get_viewing_request_details(0)
        assert refreshed_details['status'] == current_status, \
            "Status should persist after page refresh"
    
    def test_viewing_request_without_login(self):
        """Test that viewing request requires login"""
        # Logout first
        self.header_page.logout()
        assert self.header_page.is_user_logged_out(), "Should be logged out"
        
        # Navigate to a property
        self.home_page.click_first_property()
        self.property_detail_page.wait_for_property_to_load()
        
        # Try to schedule viewing
        if self.property_detail_page.is_element_visible(
            self.property_detail_page.SCHEDULE_VIEWING_BUTTON
        ):
            self.property_detail_page.click_schedule_viewing()
            
            # Should be prompted to login or button should be disabled
            # This depends on implementation
            assert not self.property_detail_page.is_element_visible(
                self.property_detail_page.BOOKING_MODAL
            ), "Should not open booking modal without login"
    
    def test_viewing_request_form_autofill(self):
        """Test that viewing request form auto-fills user information"""
        # Navigate to a property
        self.home_page.click_first_property()
        self.property_detail_page.wait_for_property_to_load()
        
        if self.property_detail_page.is_viewing_requested():
            pytest.skip("Property already has viewing requested")
        
        # Open booking modal
        self.property_detail_page.click_schedule_viewing()
        
        # Check if user information is pre-filled
        name_value = self.property_detail_page.get_element_attribute(
            self.property_detail_page.BOOKING_NAME_INPUT, 'value'
        )
        email_value = self.property_detail_page.get_element_attribute(
            self.property_detail_page.BOOKING_EMAIL_INPUT, 'value'
        )
        
        # Should have some user information pre-filled
        assert name_value or email_value, \
            "Some user information should be pre-filled"
        
        self.property_detail_page.close_booking_modal()

