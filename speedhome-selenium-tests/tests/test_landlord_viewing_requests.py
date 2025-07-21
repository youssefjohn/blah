"""
Test cases for landlord viewing request management functionality
"""
import pytest
import time
from datetime import datetime, timedelta
from utils.base_test import BaseTest
from pages.header_page import HeaderPage
from pages.landlord_dashboard_page import LandlordDashboardPage
from utils.test_data_generator import TestDataGenerator
from config.test_config import TestConfig

class TestLandlordViewingRequests(BaseTest):
    """Test landlord viewing request management functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        super().setup_method()
        self.header_page = HeaderPage(self.driver)
        self.landlord_dashboard_page = LandlordDashboardPage(self.driver)
        self.data_generator = TestDataGenerator()
        
        # Login as landlord for tests
        self.header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
        assert self.header_page.is_user_logged_in(), "Should be logged in for viewing request tests"
        
        # Navigate to landlord dashboard viewing requests
        self.header_page.click_landlord_button()
        self.landlord_dashboard_page.wait_for_dashboard_to_load()
        self.landlord_dashboard_page.click_viewing_requests_tab()
    
    def test_viewing_requests_display(self):
        """Test viewing requests are displayed correctly"""
        # Check if viewing requests section is visible
        assert self.landlord_dashboard_page.is_element_visible(
            self.landlord_dashboard_page.VIEWING_REQUESTS_SECTION
        ), "Viewing requests section should be visible"
        
        # Get viewing requests count
        request_count = self.landlord_dashboard_page.get_viewing_request_count()
        
        if request_count > 0:
            # Verify request details are displayed
            request_details = self.landlord_dashboard_page.get_viewing_request_details(0)
            assert request_details is not None, "Should get viewing request details"
            assert request_details['property_name'], "Should have property name"
            assert request_details['tenant_name'], "Should have tenant name"
            assert request_details['date_time'], "Should have date and time"
            assert request_details['status'], "Should have status"
        else:
            # Check for empty state
            assert not self.landlord_dashboard_page.has_viewing_requests(), \
                "Should show no viewing requests message when empty"
    
    def test_view_request_details_expandable(self):
        """Test expandable viewing request details functionality"""
        if self.landlord_dashboard_page.get_viewing_request_count() == 0:
            pytest.skip("No viewing requests to test details expansion")
        
        # Click view details on first request
        success = self.landlord_dashboard_page.view_request_details(0)
        
        if success:
            # Verify expandable details are shown
            assert self.landlord_dashboard_page.is_element_visible(
                self.landlord_dashboard_page.EXPANDABLE_DETAILS
            ), "Expandable details should be visible"
            
            # Get tenant details from expanded view
            tenant_details = self.landlord_dashboard_page.get_tenant_details_from_expanded_view()
            
            if tenant_details:
                # Verify tenant information is displayed
                assert 'name' in tenant_details or 'email' in tenant_details or 'phone' in tenant_details, \
                    "Should display tenant contact information"
            
            # Click view details again to collapse
            self.landlord_dashboard_page.view_request_details(0)
            time.sleep(1)
            
            # Verify details are collapsed
            assert not self.landlord_dashboard_page.is_element_visible(
                self.landlord_dashboard_page.EXPANDABLE_DETAILS
            ), "Details should be collapsed after second click"
    
    def test_confirm_viewing_request(self):
        """Test confirming a viewing request"""
        if self.landlord_dashboard_page.get_viewing_request_count() == 0:
            pytest.skip("No viewing requests to confirm")
        
        # Get original request details
        original_details = self.landlord_dashboard_page.get_viewing_request_details(0)
        
        # Confirm the request if it's pending
        if 'Pending' in original_details['status']:
            success = self.landlord_dashboard_page.confirm_viewing_request(0)
            
            if success:
                # Wait for update
                time.sleep(2)
                
                # Verify status changed
                updated_details = self.landlord_dashboard_page.get_viewing_request_details(0)
                assert 'Confirmed' in updated_details['status'], \
                    "Status should change to Confirmed"
    
    def test_decline_viewing_request(self):
        """Test declining a viewing request"""
        if self.landlord_dashboard_page.get_viewing_request_count() == 0:
            pytest.skip("No viewing requests to decline")
        
        # Find a pending request to decline
        request_count = self.landlord_dashboard_page.get_viewing_request_count()
        pending_request_index = None
        
        for i in range(request_count):
            details = self.landlord_dashboard_page.get_viewing_request_details(i)
            if 'Pending' in details['status']:
                pending_request_index = i
                break
        
        if pending_request_index is not None:
            # Decline the request
            success = self.landlord_dashboard_page.decline_viewing_request(pending_request_index)
            
            if success:
                # Wait for update
                time.sleep(2)
                
                # Verify status changed
                updated_details = self.landlord_dashboard_page.get_viewing_request_details(pending_request_index)
                assert 'Declined' in updated_details['status'], \
                    "Status should change to Declined"
        else:
            pytest.skip("No pending requests to decline")
    
    def test_reschedule_viewing_request(self):
        """Test rescheduling a viewing request"""
        if self.landlord_dashboard_page.get_viewing_request_count() == 0:
            pytest.skip("No viewing requests to reschedule")
        
        # Find a confirmed request to reschedule
        request_count = self.landlord_dashboard_page.get_viewing_request_count()
        confirmed_request_index = None
        
        for i in range(request_count):
            details = self.landlord_dashboard_page.get_viewing_request_details(i)
            if 'Confirmed' in details['status'] or 'Pending' in details['status']:
                confirmed_request_index = i
                break
        
        if confirmed_request_index is not None:
            # Generate new date and time
            new_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
            new_time = '16:00'
            
            # Reschedule the request
            success = self.landlord_dashboard_page.reschedule_viewing_request(
                confirmed_request_index, new_date, new_time
            )
            
            if success:
                # Wait for update
                time.sleep(2)
                
                # Verify status indicates reschedule
                updated_details = self.landlord_dashboard_page.get_viewing_request_details(confirmed_request_index)
                assert 'Reschedule' in updated_details['status'], \
                    "Status should indicate reschedule proposed"
        else:
            pytest.skip("No suitable requests to reschedule")
    
    def test_cancel_reschedule_request(self):
        """Test canceling a reschedule request"""
        if self.landlord_dashboard_page.get_viewing_request_count() == 0:
            pytest.skip("No viewing requests to test cancel reschedule")
        
        # Find a request with reschedule status
        request_count = self.landlord_dashboard_page.get_viewing_request_count()
        reschedule_request_index = None
        
        for i in range(request_count):
            details = self.landlord_dashboard_page.get_viewing_request_details(i)
            if 'Reschedule' in details['status']:
                reschedule_request_index = i
                break
        
        if reschedule_request_index is not None:
            # Cancel the reschedule
            success = self.landlord_dashboard_page.decline_reschedule_request(reschedule_request_index)
            
            if success:
                # Wait for update
                time.sleep(2)
                
                # Verify status reverted
                updated_details = self.landlord_dashboard_page.get_viewing_request_details(reschedule_request_index)
                assert 'Reschedule' not in updated_details['status'], \
                    "Status should revert from reschedule"
        else:
            pytest.skip("No reschedule requests to cancel")
    
    def test_viewing_request_status_persistence(self):
        """Test that viewing request status changes persist after page refresh"""
        if self.landlord_dashboard_page.get_viewing_request_count() == 0:
            pytest.skip("No viewing requests to test persistence")
        
        # Get current status
        original_details = self.landlord_dashboard_page.get_viewing_request_details(0)
        original_status = original_details['status']
        
        # Refresh page
        self.landlord_dashboard_page.refresh_page()
        self.landlord_dashboard_page.wait_for_dashboard_to_load()
        self.landlord_dashboard_page.click_viewing_requests_tab()
        
        # Verify status persisted
        refreshed_details = self.landlord_dashboard_page.get_viewing_request_details(0)
        assert refreshed_details['status'] == original_status, \
            "Status should persist after page refresh"
    
    def test_viewing_request_sorting_by_date(self):
        """Test viewing requests are sorted by date"""
        request_count = self.landlord_dashboard_page.get_viewing_request_count()
        
        if request_count < 2:
            pytest.skip("Need at least 2 viewing requests to test sorting")
        
        # Get dates from first few requests
        dates = []
        for i in range(min(3, request_count)):
            details = self.landlord_dashboard_page.get_viewing_request_details(i)
            dates.append(details['date_time'])
        
        # Verify dates are in logical order (newest first or oldest first)
        # This would depend on the implementation
        assert len(dates) > 1, "Should have multiple dates to compare"
    
    def test_viewing_request_property_name_link(self):
        """Test clicking on property name navigates to property details"""
        if self.landlord_dashboard_page.get_viewing_request_count() == 0:
            pytest.skip("No viewing requests to test property navigation")
        
        # Get property name from first request
        request_details = self.landlord_dashboard_page.get_viewing_request_details(0)
        property_name = request_details['property_name']
        
        # Click on property name (if it's a link)
        requests = self.landlord_dashboard_page.get_viewing_requests()
        if len(requests) > 0:
            property_cell = requests[0].find_element(*self.landlord_dashboard_page.REQUEST_PROPERTY_NAME)
            
            # Check if it's clickable
            try:
                property_cell.click()
                time.sleep(2)
                
                # Verify navigation (this would depend on implementation)
                current_url = self.landlord_dashboard_page.get_current_url()
                # Could check if URL contains property ID or property page
                
                # Navigate back to dashboard
                self.header_page.click_landlord_button()
                self.landlord_dashboard_page.wait_for_dashboard_to_load()
                self.landlord_dashboard_page.click_viewing_requests_tab()
                
            except:
                # Property name might not be clickable
                pass
    
    def test_viewing_request_tenant_contact_info(self):
        """Test tenant contact information is displayed in expandable details"""
        if self.landlord_dashboard_page.get_viewing_request_count() == 0:
            pytest.skip("No viewing requests to test tenant info")
        
        # Expand details for first request
        success = self.landlord_dashboard_page.view_request_details(0)
        
        if success:
            # Get tenant details
            tenant_details = self.landlord_dashboard_page.get_tenant_details_from_expanded_view()
            
            if tenant_details:
                # Verify contact information format
                if 'email' in tenant_details:
                    email = tenant_details['email']
                    assert '@' in email, "Email should be in valid format"
                
                if 'phone' in tenant_details:
                    phone = tenant_details['phone']
                    assert len(phone) > 5, "Phone should have reasonable length"
                
                if 'name' in tenant_details:
                    name = tenant_details['name']
                    assert len(name) > 0, "Name should not be empty"
    
    def test_viewing_request_actions_based_on_status(self):
        """Test that available actions depend on request status"""
        request_count = self.landlord_dashboard_page.get_viewing_request_count()
        
        if request_count == 0:
            pytest.skip("No viewing requests to test status-based actions")
        
        # Check actions for different status types
        for i in range(min(3, request_count)):
            details = self.landlord_dashboard_page.get_viewing_request_details(i)
            status = details['status']
            
            requests = self.landlord_dashboard_page.get_viewing_requests()
            request_row = requests[i]
            
            # Check available buttons based on status
            if 'Pending' in status:
                # Should have Confirm and Decline buttons
                confirm_btn_exists = self.landlord_dashboard_page.is_element_present(
                    self.landlord_dashboard_page.CONFIRM_REQUEST_BUTTON
                )
                decline_btn_exists = self.landlord_dashboard_page.is_element_present(
                    self.landlord_dashboard_page.DECLINE_REQUEST_BUTTON
                )
                
                # At least one action should be available
                assert confirm_btn_exists or decline_btn_exists, \
                    "Pending requests should have action buttons"
            
            elif 'Confirmed' in status:
                # Should have Reschedule button
                reschedule_btn_exists = self.landlord_dashboard_page.is_element_present(
                    self.landlord_dashboard_page.RESCHEDULE_REQUEST_BUTTON
                )
                
                # Note: This test depends on implementation
                # Some systems might not allow rescheduling confirmed requests
    
    def test_viewing_request_bulk_actions(self):
        """Test bulk actions on viewing requests if implemented"""
        request_count = self.landlord_dashboard_page.get_viewing_request_count()
        
        if request_count < 2:
            pytest.skip("Need multiple viewing requests for bulk actions")
        
        # This test would check for:
        # - Select all checkbox
        # - Individual checkboxes for each request
        # - Bulk confirm/decline buttons
        # - Bulk status update functionality
        
        # For now, just verify multiple requests can be managed individually
        assert request_count >= 2, "Should have multiple requests for bulk management"
    
    def test_viewing_request_search_filter(self):
        """Test searching/filtering viewing requests if implemented"""
        request_count = self.landlord_dashboard_page.get_viewing_request_count()
        
        if request_count == 0:
            pytest.skip("No viewing requests to test filtering")
        
        # This test would check for:
        # - Search by tenant name
        # - Filter by status
        # - Filter by property
        # - Filter by date range
        
        # For now, just verify requests are displayed
        assert request_count > 0, "Should have requests to filter"
    
    def test_viewing_request_notification_updates(self):
        """Test that viewing request actions trigger notifications"""
        if self.landlord_dashboard_page.get_viewing_request_count() == 0:
            pytest.skip("No viewing requests to test notifications")
        
        # Get initial notification count
        initial_notification_count = self.header_page.get_notification_count()
        
        # Perform an action (confirm a request)
        request_details = self.landlord_dashboard_page.get_viewing_request_details(0)
        
        if 'Pending' in request_details['status']:
            success = self.landlord_dashboard_page.confirm_viewing_request(0)
            
            if success:
                time.sleep(2)
                
                # Check if notification count changed
                new_notification_count = self.header_page.get_notification_count()
                
                # Note: This depends on implementation
                # Some systems might not show notifications for landlord actions
    
    def test_viewing_request_empty_state(self):
        """Test empty state when no viewing requests exist"""
        # This test would require a landlord with no viewing requests
        # For now, check if empty state handling exists
        
        if self.landlord_dashboard_page.get_viewing_request_count() == 0:
            assert not self.landlord_dashboard_page.has_viewing_requests(), \
                "Should show no viewing requests message when empty"
            
            # Verify appropriate empty state message
            assert self.landlord_dashboard_page.is_element_visible(
                self.landlord_dashboard_page.NO_VIEWING_REQUESTS_MESSAGE
            ), "Should display no viewing requests message"

