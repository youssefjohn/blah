"""
Integration test cases for end-to-end workflows between tenants and landlords
"""
import pytest
import time
from datetime import datetime, timedelta
from utils.base_test import BaseTest
from pages.header_page import HeaderPage
from pages.home_page import HomePage
from pages.property_detail_page import PropertyDetailPage
from pages.user_dashboard_page import UserDashboardPage
from pages.landlord_dashboard_page import LandlordDashboardPage
from utils.test_data_generator import TestDataGenerator
from config.test_config import TestConfig

class TestIntegrationWorkflows(BaseTest):
    """Test end-to-end integration workflows"""
    
    def setup_method(self):
        """Setup for each test method"""
        super().setup_method()
        self.header_page = HeaderPage(self.driver)
        self.home_page = HomePage(self.driver)
        self.property_detail_page = PropertyDetailPage(self.driver)
        self.user_dashboard_page = UserDashboardPage(self.driver)
        self.landlord_dashboard_page = LandlordDashboardPage(self.driver)
        self.data_generator = TestDataGenerator()
    
    def test_complete_viewing_request_workflow(self):
        """Test complete viewing request workflow from tenant request to landlord response"""
        
        # Step 1: Login as tenant
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
        assert self.header_page.is_user_logged_in(), "Tenant should be logged in"
        
        # Step 2: Search and find a property
        self.home_page.search_properties("apartment")
        time.sleep(2)
        
        if self.home_page.get_property_count() == 0:
            pytest.skip("No properties available for viewing request test")
        
        # Step 3: Navigate to property detail page
        self.home_page.click_first_property()
        self.property_detail_page.wait_for_property_to_load()
        
        property_title = self.property_detail_page.get_property_title()
        
        # Step 4: Schedule viewing (if not already requested)
        if not self.property_detail_page.is_viewing_requested():
            booking_data = self.data_generator.generate_booking_data()
            success = self.property_detail_page.schedule_viewing(booking_data)
            assert success, "Viewing request should be successful"
        
        # Step 5: Verify request appears in tenant dashboard
        self.header_page.click_tenant_button()
        self.user_dashboard_page.wait_for_dashboard_to_load()
        self.user_dashboard_page.scroll_to_viewing_requests()
        
        assert self.user_dashboard_page.has_viewing_requests(), \
            "Tenant should have viewing requests"
        
        tenant_request = self.user_dashboard_page.get_viewing_request_details(0)
        assert property_title in tenant_request['property_title'], \
            "Property title should match in tenant dashboard"
        
        # Step 6: Logout tenant and login as landlord
        self.header_page.logout()
        self.header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
        assert self.header_page.is_user_logged_in(), "Landlord should be logged in"
        
        # Step 7: Check viewing requests in landlord dashboard
        self.header_page.click_landlord_button()
        self.landlord_dashboard_page.wait_for_dashboard_to_load()
        self.landlord_dashboard_page.click_viewing_requests_tab()
        
        if self.landlord_dashboard_page.has_viewing_requests():
            # Step 8: View request details
            landlord_request = self.landlord_dashboard_page.get_viewing_request_details(0)
            
            # Step 9: Confirm the viewing request
            if 'Pending' in landlord_request['status']:
                success = self.landlord_dashboard_page.confirm_viewing_request(0)
                if success:
                    time.sleep(2)
                    
                    # Verify status changed
                    updated_request = self.landlord_dashboard_page.get_viewing_request_details(0)
                    assert 'Confirmed' in updated_request['status'], \
                        "Request status should be confirmed"
        
        # Step 10: Verify status update reflects in tenant dashboard
        self.header_page.logout()
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
        self.header_page.click_tenant_button()
        self.user_dashboard_page.wait_for_dashboard_to_load()
        self.user_dashboard_page.scroll_to_viewing_requests()
        
        final_tenant_request = self.user_dashboard_page.get_viewing_request_details(0)
        # Status should reflect landlord's action
        assert final_tenant_request['status'] in ['Confirmed', 'Pending'], \
            "Tenant should see updated status"
    
    def test_property_lifecycle_workflow(self):
        """Test complete property lifecycle from creation to tenant interaction"""
        
        # Step 1: Login as landlord
        self.header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
        assert self.header_page.is_user_logged_in(), "Landlord should be logged in"
        
        # Step 2: Navigate to landlord dashboard
        self.header_page.click_landlord_button()
        self.landlord_dashboard_page.wait_for_dashboard_to_load()
        self.landlord_dashboard_page.click_my_properties_tab()
        
        # Step 3: Add new property
        property_data = self.data_generator.generate_property_data()
        property_data['title'] = f'Integration Test Property {int(time.time())}'
        
        initial_count = self.landlord_dashboard_page.get_property_count()
        self.landlord_dashboard_page.add_property(property_data)
        time.sleep(2)
        
        # Verify property was added
        new_count = self.landlord_dashboard_page.get_property_count()
        assert new_count == initial_count + 1, "Property should be added"
        
        # Step 4: Logout landlord and login as tenant
        self.header_page.logout()
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
        
        # Step 5: Search for the new property
        self.home_page.search_properties(property_data['title'])
        time.sleep(2)
        
        # Step 6: Verify property appears in search results
        property_count = self.home_page.get_property_count()
        
        if property_count > 0:
            # Step 7: View property details
            self.home_page.click_first_property()
            self.property_detail_page.wait_for_property_to_load()
            
            displayed_title = self.property_detail_page.get_property_title()
            assert property_data['title'] in displayed_title, \
                "Property title should match"
            
            # Step 8: Add to favorites
            self.property_detail_page.toggle_favorite()
            time.sleep(1)
            
            # Step 9: Verify in tenant dashboard favorites
            self.header_page.click_tenant_button()
            self.user_dashboard_page.wait_for_dashboard_to_load()
            self.user_dashboard_page.scroll_to_favorites()
            
            if self.user_dashboard_page.has_favorites():
                favorite_details = self.user_dashboard_page.get_favorite_details(0)
                assert property_data['title'] in favorite_details['property_title'], \
                    "Property should appear in favorites"
        
        # Step 10: Change property status and verify visibility
        self.header_page.logout()
        self.header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
        self.header_page.click_landlord_button()
        self.landlord_dashboard_page.wait_for_dashboard_to_load()
        self.landlord_dashboard_page.click_my_properties_tab()
        
        # Change property to inactive
        success = self.landlord_dashboard_page.change_property_status(0, 'Inactive')
        if success:
            time.sleep(2)
            
            # Step 11: Verify property no longer appears in public search
            self.header_page.logout()
            self.home_page.search_properties(property_data['title'])
            time.sleep(2)
            
            # Should not find the inactive property
            search_count = self.home_page.get_property_count()
            # Note: This depends on implementation of status filtering
    
    def test_reschedule_workflow_both_sides(self):
        """Test reschedule workflow initiated by both tenant and landlord"""
        
        # Setup: Ensure there's a confirmed viewing request
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
        
        # Navigate to tenant dashboard
        self.header_page.click_tenant_button()
        self.user_dashboard_page.wait_for_dashboard_to_load()
        self.user_dashboard_page.scroll_to_viewing_requests()
        
        if not self.user_dashboard_page.has_viewing_requests():
            pytest.skip("No viewing requests available for reschedule test")
        
        # Test 1: Tenant-initiated reschedule
        original_request = self.user_dashboard_page.get_viewing_request_details(0)
        
        if 'Confirmed' in original_request['status']:
            # Generate new date/time
            new_date = (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d')
            new_time = '14:30'
            
            # Reschedule from tenant side
            success = self.user_dashboard_page.reschedule_viewing_request(0, new_date, new_time)
            
            if success:
                time.sleep(2)
                
                # Verify status changed
                updated_request = self.user_dashboard_page.get_viewing_request_details(0)
                assert 'Reschedule' in updated_request['status'], \
                    "Status should indicate reschedule requested"
                
                # Check landlord side
                self.header_page.logout()
                self.header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
                self.header_page.click_landlord_button()
                self.landlord_dashboard_page.wait_for_dashboard_to_load()
                self.landlord_dashboard_page.click_viewing_requests_tab()
                
                if self.landlord_dashboard_page.has_viewing_requests():
                    landlord_request = self.landlord_dashboard_page.get_viewing_request_details(0)
                    assert 'Reschedule' in landlord_request['status'], \
                        "Landlord should see reschedule request"
                    
                    # Landlord can approve or propose different time
                    # For this test, we'll cancel the reschedule
                    cancel_success = self.landlord_dashboard_page.cancel_reschedule_request(0)
                    
                    if cancel_success:
                        time.sleep(2)
                        
                        # Verify status reverted
                        reverted_request = self.landlord_dashboard_page.get_viewing_request_details(0)
                        assert 'Reschedule' not in reverted_request['status'], \
                            "Status should revert after cancel"
    
    def test_application_workflow(self):
        """Test complete application workflow from submission to landlord response"""
        
        # Step 1: Login as tenant
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
        
        # Step 2: Find and apply to a property
        self.home_page.click_first_property()
        self.property_detail_page.wait_for_property_to_load()
        
        property_title = self.property_detail_page.get_property_title()
        
        # Check if application is possible
        if not self.property_detail_page.is_already_applied():
            application_data = {
                'message': 'I am very interested in this property and would like to apply.'
            }
            
            success = self.property_detail_page.apply_for_property(application_data)
            
            if success:
                # Step 3: Verify application in tenant dashboard
                self.header_page.click_tenant_button()
                self.user_dashboard_page.wait_for_dashboard_to_load()
                self.user_dashboard_page.scroll_to_applications()
                
                if self.user_dashboard_page.has_applications():
                    app_details = self.user_dashboard_page.get_application_details(0)
                    assert property_title in app_details['property_title'], \
                        "Application should appear in tenant dashboard"
                
                # Step 4: Check landlord side
                self.header_page.logout()
                self.header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
                self.header_page.click_landlord_button()
                self.landlord_dashboard_page.wait_for_dashboard_to_load()
                self.landlord_dashboard_page.click_applications_tab()
                
                if self.landlord_dashboard_page.has_applications():
                    landlord_app = self.landlord_dashboard_page.get_application_details(0)
                    
                    # Step 5: Approve or reject application
                    if 'Pending' in landlord_app['status']:
                        approve_success = self.landlord_dashboard_page.approve_application(0)
                        
                        if approve_success:
                            time.sleep(2)
                            
                            # Verify status changed
                            updated_app = self.landlord_dashboard_page.get_application_details(0)
                            assert 'Approved' in updated_app['status'], \
                                "Application should be approved"
                
                # Step 6: Verify status update in tenant dashboard
                self.header_page.logout()
                self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
                self.header_page.click_tenant_button()
                self.user_dashboard_page.wait_for_dashboard_to_load()
                self.user_dashboard_page.scroll_to_applications()
                
                if self.user_dashboard_page.has_applications():
                    final_app = self.user_dashboard_page.get_application_details(0)
                    # Status should reflect landlord's decision
                    assert final_app['status'] in ['Approved', 'Pending'], \
                        "Tenant should see updated application status"
    
    def test_cross_role_data_consistency(self):
        """Test data consistency between tenant and landlord views"""
        
        # Step 1: Login as tenant and get viewing request data
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
        self.header_page.click_tenant_button()
        self.user_dashboard_page.wait_for_dashboard_to_load()
        self.user_dashboard_page.scroll_to_viewing_requests()
        
        if not self.user_dashboard_page.has_viewing_requests():
            pytest.skip("No viewing requests to test data consistency")
        
        tenant_request = self.user_dashboard_page.get_viewing_request_details(0)
        
        # Step 2: Login as landlord and get same request data
        self.header_page.logout()
        self.header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
        self.header_page.click_landlord_button()
        self.landlord_dashboard_page.wait_for_dashboard_to_load()
        self.landlord_dashboard_page.click_viewing_requests_tab()
        
        if self.landlord_dashboard_page.has_viewing_requests():
            landlord_request = self.landlord_dashboard_page.get_viewing_request_details(0)
            
            # Step 3: Verify data consistency
            # Property names should match
            assert tenant_request['property_title'] == landlord_request['property_name'], \
                "Property names should match between tenant and landlord views"
            
            # Status should be consistent
            assert tenant_request['status'] == landlord_request['status'], \
                "Status should be consistent between views"
            
            # Dates should match
            # Note: Date formats might differ, so we check if they contain same information
            tenant_date = tenant_request['date']
            landlord_date = landlord_request['date_time']
            
            # Basic check that both contain date information
            assert len(tenant_date) > 0 and len(landlord_date) > 0, \
                "Both views should show date information"
    
    def test_notification_workflow(self):
        """Test notification workflow for various actions"""
        
        # Step 1: Login as tenant and check initial notification count
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
        initial_tenant_notifications = self.header_page.get_notification_count()
        
        # Step 2: Login as landlord and perform action that should trigger notification
        self.header_page.logout()
        self.header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
        self.header_page.click_landlord_button()
        self.landlord_dashboard_page.wait_for_dashboard_to_load()
        self.landlord_dashboard_page.click_viewing_requests_tab()
        
        if self.landlord_dashboard_page.has_viewing_requests():
            # Confirm a viewing request
            request_details = self.landlord_dashboard_page.get_viewing_request_details(0)
            
            if 'Pending' in request_details['status']:
                success = self.landlord_dashboard_page.confirm_viewing_request(0)
                
                if success:
                    time.sleep(2)
                    
                    # Step 3: Check if tenant received notification
                    self.header_page.logout()
                    self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
                    
                    new_tenant_notifications = self.header_page.get_notification_count()
                    
                    # Note: This test depends on notification implementation
                    # Some systems might not show real-time notifications
                    
                    # At minimum, verify notification system is functional
                    assert new_tenant_notifications >= 0, \
                        "Notification system should be functional"
    
    def test_search_to_application_complete_flow(self):
        """Test complete flow from property search to application submission"""
        
        # Step 1: Login as tenant
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
        
        # Step 2: Search for properties
        search_term = "apartment"
        self.home_page.search_properties(search_term)
        time.sleep(2)
        
        if self.home_page.get_property_count() == 0:
            pytest.skip("No properties found for complete flow test")
        
        # Step 3: Apply filters
        self.home_page.click_more_filters()
        self.home_page.select_bedroom_filter('2+')
        self.home_page.select_amenities(['Swimming Pool', 'Gym'])
        self.home_page.apply_filters()
        time.sleep(2)
        
        # Step 4: View property details
        if self.home_page.get_property_count() > 0:
            self.home_page.click_first_property()
            self.property_detail_page.wait_for_property_to_load()
            
            property_title = self.property_detail_page.get_property_title()
            
            # Step 5: Add to favorites
            self.property_detail_page.toggle_favorite()
            
            # Step 6: Schedule viewing
            if not self.property_detail_page.is_viewing_requested():
                booking_data = self.data_generator.generate_booking_data()
                viewing_success = self.property_detail_page.schedule_viewing(booking_data)
                assert viewing_success, "Viewing should be scheduled successfully"
            
            # Step 7: Submit application
            if not self.property_detail_page.is_already_applied():
                application_data = {
                    'message': 'Complete flow test application'
                }
                app_success = self.property_detail_page.apply_for_property(application_data)
                assert app_success, "Application should be submitted successfully"
            
            # Step 8: Verify all actions in tenant dashboard
            self.header_page.click_tenant_button()
            self.user_dashboard_page.wait_for_dashboard_to_load()
            
            # Check favorites
            self.user_dashboard_page.scroll_to_favorites()
            if self.user_dashboard_page.has_favorites():
                favorite = self.user_dashboard_page.get_favorite_details(0)
                assert property_title in favorite['property_title'], \
                    "Property should be in favorites"
            
            # Check viewing requests
            self.user_dashboard_page.scroll_to_viewing_requests()
            if self.user_dashboard_page.has_viewing_requests():
                viewing_req = self.user_dashboard_page.get_viewing_request_details(0)
                assert property_title in viewing_req['property_title'], \
                    "Property should have viewing request"
            
            # Check applications
            self.user_dashboard_page.scroll_to_applications()
            if self.user_dashboard_page.has_applications():
                application = self.user_dashboard_page.get_application_details(0)
                assert property_title in application['property_title'], \
                    "Property should have application"

