"""
Fixed reschedule workflow test
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

class TestRescheduleWorkflow(BaseTest):
    """Test reschedule workflow functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        super().setup_method()
        self.header_page = HeaderPage(self.driver)
        self.home_page = HomePage(self.driver)
        self.property_detail_page = PropertyDetailPage(self.driver)
        self.user_dashboard_page = UserDashboardPage(self.driver)
        self.landlord_dashboard_page = LandlordDashboardPage(self.driver)
        self.data_generator = TestDataGenerator()

    def test_reschedule_workflow_both_sides(self, seed_database):
        """Test reschedule workflow initiated by both tenant and landlord"""
        
        # This test uses the seed_database fixture to ensure we have confirmed viewing requests
        
        # === PART 1: TENANT-INITIATED RESCHEDULE ===
        print("\n=== TESTING TENANT-INITIATED RESCHEDULE ===")
        
        # Step 1: Login as tenant and check for confirmed viewing requests
        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
        assert self.header_page.is_user_logged_in(), "Tenant should be logged in"
        
        # Navigate to tenant dashboard
        self.header_page.click_tenant_button()
        self.user_dashboard_page.wait_for_dashboard_to_load()
        self.user_dashboard_page.scroll_to_viewing_requests()
        
        if not self.user_dashboard_page.has_viewing_requests():
            pytest.skip("No viewing requests available for reschedule test")
        
        # Step 2: Get original request details and initiate reschedule
        original_request = self.user_dashboard_page.get_viewing_request_details(0)
        print(f"Original request status: {original_request['status']}")
        
        if 'Confirmed' in original_request['status']:
            # Generate new date/time for reschedule
            new_date = (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d')
            new_time = '14:30'
            
            print(f"Tenant requesting reschedule to {new_date} at {new_time}")
            
            # Reschedule from tenant side
            success = self.user_dashboard_page.reschedule_viewing_request(0, new_date, new_time)
            
            if success:
                time.sleep(2)
                
                # Step 3: Verify status changed on tenant side
                updated_request = self.user_dashboard_page.get_viewing_request_details(0)
                print(f"Updated tenant status: {updated_request['status']}")
                assert 'Reschedule' in updated_request['status'], \
                    "Status should indicate reschedule requested"
                
                # Step 4: Check landlord side sees the reschedule request
                self.header_page.click_account_icon()
                self.header_page.logout()
                time.sleep(2)
                self.header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
                assert self.header_page.is_user_logged_in(), "Landlord should be logged in"
                
                self.header_page.click_landlord_button()
                self.landlord_dashboard_page.wait_for_dashboard_to_load()
                self.landlord_dashboard_page.click_viewing_requests_tab()
                
                if self.landlord_dashboard_page.has_viewing_requests():
                    landlord_request = self.landlord_dashboard_page.get_viewing_request_details(0)
                    print(f"Landlord sees status: {landlord_request['status']}")
                    assert 'Reschedule' in landlord_request['status'], \
                        "Landlord should see reschedule request"
                    
                    # Step 5: Landlord cancels the reschedule request
                    print("Landlord canceling reschedule request...")
                    cancel_success = self.landlord_dashboard_page.cancel_reschedule_request(0)
                    
                    if cancel_success:
                        time.sleep(2)
                        
                        # Verify status reverted on landlord side
                        reverted_request = self.landlord_dashboard_page.get_viewing_request_details(0)
                        print(f"Reverted landlord status: {reverted_request['status']}")
                        assert 'Reschedule' not in reverted_request['status'], \
                            "Status should revert after cancel"
                        
                        # Step 6: Verify tenant also sees the reverted status
                        self.header_page.click_account_icon()
                        self.header_page.logout()
                        time.sleep(2)
                        self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
                        
                        self.header_page.click_tenant_button()
                        self.user_dashboard_page.wait_for_dashboard_to_load()
                        self.user_dashboard_page.scroll_to_viewing_requests()
                        
                        final_tenant_request = self.user_dashboard_page.get_viewing_request_details(0)
                        print(f"Final tenant status: {final_tenant_request['status']}")
                        assert 'Reschedule' not in final_tenant_request['status'], \
                            "Tenant should see reverted status"
        
        # === PART 2: LANDLORD-INITIATED RESCHEDULE ===
        print("\n=== TESTING LANDLORD-INITIATED RESCHEDULE ===")
        
        # Step 7: Switch to landlord and initiate reschedule
        self.header_page.click_account_icon()
        self.header_page.logout()
        time.sleep(2)
        self.header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
        
        self.header_page.click_landlord_button()
        self.landlord_dashboard_page.wait_for_dashboard_to_load()
        self.landlord_dashboard_page.click_viewing_requests_tab()
        
        if self.landlord_dashboard_page.has_viewing_requests():
            current_request = self.landlord_dashboard_page.get_viewing_request_details(0)
            print(f"Current landlord request status: {current_request['status']}")
            
            if 'Confirmed' in current_request['status']:
                # Generate new date/time for landlord reschedule
                landlord_new_date = (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d')
                landlord_new_time = '16:00'
                
                print(f"Landlord proposing reschedule to {landlord_new_date} at {landlord_new_time}")
                
                # Landlord initiates reschedule
                reschedule_success = self.landlord_dashboard_page.reschedule_viewing_request(0, landlord_new_date, landlord_new_time)
                
                if reschedule_success:
                    time.sleep(2)
                    
                    # Step 8: Verify landlord sees reschedule status
                    updated_landlord_request = self.landlord_dashboard_page.get_viewing_request_details(0)
                    print(f"Updated landlord status: {updated_landlord_request['status']}")
                    assert 'Reschedule' in updated_landlord_request['status'], \
                        "Landlord should see reschedule proposed status"
                    
                    # Step 9: Check tenant side sees the landlord's reschedule proposal
                    self.header_page.click_account_icon()
                    self.header_page.logout()
                    time.sleep(2)
                    self.header_page.login(TestConfig.TENANT_EMAIL, TestConfig.TENANT_PASSWORD)
                    
                    self.header_page.click_tenant_button()
                    self.user_dashboard_page.wait_for_dashboard_to_load()
                    self.user_dashboard_page.scroll_to_viewing_requests()
                    
                    tenant_sees_reschedule = self.user_dashboard_page.get_viewing_request_details(0)
                    print(f"Tenant sees landlord reschedule: {tenant_sees_reschedule['status']}")
                    assert 'Reschedule' in tenant_sees_reschedule['status'], \
                        "Tenant should see landlord's reschedule proposal"
                    
                    # Step 10: Tenant cancels the landlord's reschedule
                    print("Tenant canceling landlord's reschedule...")
                    tenant_cancel_success = self.user_dashboard_page.cancel_reschedule_request(0)
                    
                    if tenant_cancel_success:
                        time.sleep(2)
                        
                        # Final verification: both sides should see original confirmed status
                        final_tenant_status = self.user_dashboard_page.get_viewing_request_details(0)
                        print(f"Final tenant status after cancel: {final_tenant_status['status']}")
                        assert 'Reschedule' not in final_tenant_status['status'], \
                            "Final status should not show reschedule"
        
        print("\n✅ RESCHEDULE WORKFLOW BOTH SIDES TEST COMPLETED SUCCESSFULLY")

