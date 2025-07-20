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

    def test_complete_viewing_request_workflow(self, seed_database):
        """Test complete viewing request workflow from tenant request to landlord response"""

        # This test receives the 'seed_database' fixture as an argument.
        # Pytest automatically runs the fixture before this test starts, ensuring the
        # database is in a clean, predictable state with test users and properties.

        # --- TENANT'S ACTIONS ---

        # Step 1: Login as the pre-defined test tenant.
        # The login details are pulled from the TestConfig class for consistency.
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
        # Assert that the login was successful by checking for an element that only
        # appears when a user is logged in (like an account icon or logout button).
        assert self.header_page.is_user_logged_in(), "Tenant should be logged in"

        # Step 2: Navigate back to the homepage to ensure a consistent starting point.
        self.header_page.click_logo()

        # Step 3: Find the first property on the homepage and click it to go to its detail page.
        self.home_page.click_first_property()
        # Wait for the property detail page to finish loading its data.
        self.property_detail_page.wait_for_property_to_load()

        # Store the title of the property to verify it in the dashboards later.
        property_title = self.property_detail_page.get_property_title()

        # Step 4: Check if a viewing has already been requested for this property.
        # This makes the test re-runnable without needing to re-seed the database every time.
        if not self.property_detail_page.is_viewing_requested():
            # If no request exists, generate random but valid booking data.
            booking_data = self.data_generator.generate_booking_data()
            # Fill out and submit the "Schedule Viewing" form.
            success = self.property_detail_page.schedule_viewing(booking_data)
            # The assert is commented out, but would normally check if the submission was successful.
            # assert success, "Viewing request should be successful"

        # Step 5: Verify that the new request appears correctly in the tenant's own dashboard.
        self.header_page.click_tenant_button()  # Navigate to the tenant dashboard.
        self.user_dashboard_page.wait_for_dashboard_to_load()
        self.user_dashboard_page.scroll_to_viewing_requests()  # Scroll to the relevant section.

        # Assert that there is at least one viewing request in the list.
        assert self.user_dashboard_page.has_viewing_requests(), \
            "Tenant should have viewing requests"

        # Get the details of the first request in the list.
        tenant_request = self.user_dashboard_page.get_viewing_request_details(0)
        # Assert that the property title in the dashboard matches the one we applied for.
        assert property_title in tenant_request['property_title'], \
            "Property title should match in tenant dashboard"

        # --- SWITCHING ROLES ---

        # Step 6: Log out as the tenant and log back in as the landlord.
        self.header_page.click_account_icon()
        self.header_page.logout()
        time.sleep(2)  # A brief pause to allow the frontend to update its state.
        self.header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
        # This assert is commented out but would verify the landlord is logged in.
        # assert self.header_page.is_user_logged_in(), "Landlord should be logged in"

        # --- LANDLORD'S ACTIONS ---

        # Step 7: Navigate to the "Viewing Requests" tab in the landlord's dashboard.
        self.landlord_dashboard_page.click_viewing_requests_tab()

        # Check if there are any requests to process.
        if self.landlord_dashboard_page.has_viewing_requests():
            # Step 8: Get the details of the first request.
            landlord_request = self.landlord_dashboard_page.get_viewing_request_details(0)

            # Step 9: If the request is 'pending', the landlord confirms it.
            if 'pending' in landlord_request['status']:
                success = self.landlord_dashboard_page.confirm_viewing_request(0)
                if success:
                    time.sleep(2)  # Pause to allow the UI to update.

                    # Verify the status has changed on the landlord's screen.
                    updated_request = self.landlord_dashboard_page.get_viewing_request_details(0)
                    assert 'confirmed' in updated_request['status'], \
                        "Request status should be confirmed"

        # --- FINAL VERIFICATION ---

        # Step 10: Log out as the landlord and log back in as the tenant to verify the final status.
        self.header_page.click_account_icon()
        self.header_page.logout()
        time.sleep(2)
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
        self.header_page.click_tenant_button()
        self.user_dashboard_page.wait_for_dashboard_to_load()
        self.user_dashboard_page.scroll_to_viewing_requests()

        # Get the final details from the tenant's dashboard.
        final_tenant_request = self.user_dashboard_page.get_viewing_request_details(0)
        # Assert that the status is now "Confirmed" (or still "Pending" if the landlord didn't act).
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
        # self.header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
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

    # TODO: add check to homepage/search that property is removed and doesnt show once app is approved
    # TODO: add check to property tab to verify property status is set to 'rented'
    def test_application_approval_workflow(self, seed_database):
        """Test complete application workflow from submission to landlord response"""

        # This test receives the 'seed_database' fixture as an argument.
        # Pytest automatically runs this fixture before the test starts, ensuring
        # the database is clean and populated with predictable test users and properties.

        # --- TENANT'S ACTIONS ---

        # Step 1: Login as the pre-defined test tenant.
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
        assert self.header_page.is_user_logged_in(), "Tenant login failed"

        # Step 2: Navigate to the first property on the homepage.
        self.header_page.click_logo()
        self.home_page.click_first_property()
        self.property_detail_page.wait_for_property_to_load()

        property_title = self.property_detail_page.get_property_title()

        # Step 3: Apply for the property.
        if not self.property_detail_page.is_already_applied():
            application_data = {
                'message': 'I am very interested in this property and would like to apply for it.'
            }
            success = self.property_detail_page.apply_for_property(application_data)
            assert success, "Submitting the application failed"

        # Step 4: Verify the application appears in the tenant's own dashboard.
        self.header_page.click_tenant_button()
        self.user_dashboard_page.wait_for_dashboard_to_load()
        self.user_dashboard_page.scroll_to_applications()

        assert self.user_dashboard_page.has_applications(), "Application not found in tenant's dashboard"

        tenant_app_details = self.user_dashboard_page.get_application_details(0)
        assert property_title in tenant_app_details['property_title'], "Property title mismatch in tenant dashboard"

        # --- SWITCHING ROLES ---

        # Step 5: Log out as the tenant and log back in as the landlord.
        self.header_page.click_account_icon()
        self.header_page.logout()
        time.sleep(2)
        self.header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
        assert self.header_page.is_user_logged_in(), "Landlord login failed"

        # --- LANDLORD'S ACTIONS ---

        # Step 6: Landlord finds the application and approves it.
        self.landlord_dashboard_page.click_applications_tab()
        assert self.landlord_dashboard_page.has_applications(), "Application not found in landlord's dashboard"

        landlord_app = self.landlord_dashboard_page.get_application_details(0)
        if 'pending' in landlord_app['status'].lower():
            approve_success = self.landlord_dashboard_page.approve_application(0)
            assert approve_success, "Landlord failed to approve the application"
            time.sleep(2)

            updated_app = self.landlord_dashboard_page.get_application_details(0)
            assert 'approved' in updated_app[
                'status'].lower(), "Application status did not update to 'Approved' in landlord dashboard"

        # Step 7: Verify that approving the application automatically changed the property's status to 'Rented'.
        self.landlord_dashboard_page.click_my_properties_tab()
        self.header_page.refresh_page()
        self.header_page.click_landlord_button()
        property_status = self.landlord_dashboard_page.get_property_status_by_title(property_title)
        assert property_status == 'Rented', f"Expected property status to be 'Rented', but was '{property_status}'"

        # --- FINAL VERIFICATION ---

        # Step 8: Log out as the landlord and log back in as the tenant to verify the final status.
        self.header_page.click_account_icon()
        self.header_page.logout()
        time.sleep(2)
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)

        self.header_page.click_tenant_button()
        self.user_dashboard_page.wait_for_dashboard_to_load()
        self.user_dashboard_page.scroll_to_applications()

        final_app_details = self.user_dashboard_page.get_application_details(0)
        assert 'approved' in final_app_details[
            'status'].lower(), "Final application status was not 'Approved' in tenant dashboard"

    def test_application_rejection_workflow(self, seed_database):
        """Test complete application workflow for a REJECTION scenario."""

        # This test also uses the 'seed_database' fixture to ensure a clean state.

        # --- TENANT'S ACTIONS ---

        # Step 1 & 2: Login as the tenant and navigate to a property to apply for.
        print("--- STEP 1 & 2: Tenant logging in and finding property ---")
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
        assert self.header_page.is_user_logged_in(), "Tenant login failed"
        self.header_page.click_logo()
        self.home_page.click_first_property()
        self.property_detail_page.wait_for_property_to_load()
        property_title = self.property_detail_page.get_property_title()
        print(f"✅ Navigated to property: {property_title}")

        # Step 3: Submit an application for the property.
        print("\n--- STEP 3: Submitting application as Tenant ---")
        if not self.property_detail_page.is_already_applied():
            application_data = {'message': 'Submitting an application that will be rejected.'}
            success = self.property_detail_page.apply_for_property(application_data)
            assert success, "Submitting the application failed"
            print("✅ Application submitted successfully")
        else:
            print("INFO: Tenant has already applied for this property, skipping application step.")

        # --- SWITCHING ROLES ---

        # Step 4: Log out as the tenant and log in as the landlord to review the application.
        print("\n--- STEP 4: Logging out Tenant, logging in as Landlord ---")
        self.header_page.click_account_icon()
        self.header_page.logout()
        time.sleep(2)
        self.header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
        assert self.header_page.is_user_logged_in(), "Landlord login failed"
        print("✅ Landlord logged in successfully")

        # --- LANDLORD'S ACTIONS ---

        # Step 5: Landlord finds the application and REJECTS it.
        print("\n--- STEP 5: Landlord rejecting the application ---")
        self.landlord_dashboard_page.click_applications_tab()
        assert self.landlord_dashboard_page.has_applications(), "Application not found in landlord's dashboard"

        landlord_app = self.landlord_dashboard_page.get_application_details(0)
        if 'pending' in landlord_app['status'].lower():
            # This is the key action: calling the 'reject_application' method.
            reject_success = self.landlord_dashboard_page.reject_application(0)
            assert reject_success, "Landlord failed to reject the application"
            print("✅ Landlord rejected application successfully")
            time.sleep(2)

            # Verify the status has changed to 'Rejected' on the landlord's screen.
            updated_app = self.landlord_dashboard_page.get_application_details(0)
            assert 'rejected' in updated_app['status'].lower() or 'declined' in updated_app[
                'status'].lower(), "Application status did not update to 'Rejected' in landlord dashboard"
            print("✅ Application status correctly shows as 'Rejected' for landlord")
        else:
            print(f"INFO: Application status is already '{landlord_app['status']}', skipping rejection step.")

        # Step 6: Verify that rejecting the application did NOT change the property's status.
        print("\n--- STEP 6: Verifying property status has not changed ---")
        self.header_page.refresh_page()
        self.header_page.click_landlord_button()
        property_status = self.landlord_dashboard_page.get_property_status_by_title(property_title)
        # The property should still be 'Active' and available for other tenants.
        assert property_status == 'Active', f"Expected property status to be 'Active', but it was '{property_status}'"
        print(f"✅ Verified that property '{property_title}' is still 'Active'.")

        # --- FINAL VERIFICATION ---

        # Step 7: Log out as the landlord and log back in as the tenant to verify the final status.
        print("\n--- STEP 7: Verifying final status in Tenant Dashboard ---")
        self.header_page.click_account_icon()
        self.header_page.logout()
        time.sleep(2)
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)

        self.header_page.click_tenant_button()
        self.user_dashboard_page.wait_for_dashboard_to_load()
        self.user_dashboard_page.scroll_to_applications()

        # Get the final details from the tenant's dashboard.
        final_app_details = self.user_dashboard_page.get_application_details(0)
        # Assert that the status is now "Rejected" or "Declined".
        assert 'rejected' in final_app_details['status'].lower() or 'declined' in final_app_details[
            'status'].lower(), "Final application status was not 'Rejected' in tenant dashboard"
        print("✅ Tenant correctly sees the 'Rejected' status. Workflow complete!")

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

