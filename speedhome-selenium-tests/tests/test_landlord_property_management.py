"""
Test cases for landlord property management functionality
"""
import pytest
import time
from utils.base_test import BaseTest
from pages.header_page import HeaderPage
from pages.landlord_dashboard_page import LandlordDashboardPage
from utils.test_data_generator import TestDataGenerator
from config.test_config import TestConfig

class TestLandlordPropertyManagement(BaseTest):
    """Test landlord property management functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        super().setup_method()
        self.header_page = HeaderPage(self.driver)
        self.landlord_dashboard_page = LandlordDashboardPage(self.driver)
        self.data_generator = TestDataGenerator()
        
        # Login as landlord for tests
        self.header_page.login(TestConfig.LANDLORD_EMAIL, TestConfig.LANDLORD_PASSWORD)
        assert self.header_page.is_user_logged_in(), "Should be logged in for property management tests"
        
        # Navigate to landlord dashboard
        self.header_page.click_landlord_button()
        self.landlord_dashboard_page.wait_for_dashboard_to_load()
        self.landlord_dashboard_page.click_my_properties_tab()
    
    def test_add_new_property_success(self):
        """Test successful property addition"""
        # Generate property data
        property_data = self.data_generator.generate_property_data()
        
        # Get initial property count
        initial_count = self.landlord_dashboard_page.get_property_count()
        
        # Add new property
        self.landlord_dashboard_page.add_property(property_data)
        
        # Wait for update
        time.sleep(2)
        
        # Verify property was added
        new_count = self.landlord_dashboard_page.get_property_count()
        assert new_count == initial_count + 1, "Property count should increase after adding"
        
        # Verify property details
        latest_property = self.landlord_dashboard_page.get_property_details(0)
        assert property_data['title'] in latest_property['title'], "Property title should match"
        assert property_data['location'] in latest_property['location'], "Property location should match"
        assert str(property_data['price']) in latest_property['price'], "Property price should match"
    
    def test_add_property_form_validation(self):
        """Test property form validation"""
        # Open add property modal
        self.landlord_dashboard_page.click_add_property()
        
        # Try to submit with empty required fields
        self.landlord_dashboard_page.click_element(
            self.landlord_dashboard_page.SAVE_PROPERTY_BUTTON
        )
        
        # Verify form doesn't submit (modal should still be open)
        assert self.landlord_dashboard_page.is_element_visible(
            self.landlord_dashboard_page.PROPERTY_MODAL
        ), "Modal should remain open on validation error"
        
        # Test with invalid price (negative number)
        invalid_property_data = {
            'title': 'Test Property',
            'location': 'Test Location',
            'price': -1000,
            'bedrooms': 2,
            'bathrooms': 1
        }
        
        self.landlord_dashboard_page.fill_property_form(invalid_property_data)
        self.landlord_dashboard_page.click_element(
            self.landlord_dashboard_page.SAVE_PROPERTY_BUTTON
        )
        
        # Should still be on modal due to validation
        assert self.landlord_dashboard_page.is_element_visible(
            self.landlord_dashboard_page.PROPERTY_MODAL
        ), "Modal should remain open on price validation error"
        
        # Close modal
        self.landlord_dashboard_page.close_property_modal()
    
    def test_edit_property_success(self):
        """Test successful property editing"""
        # Ensure there's at least one property
        if self.landlord_dashboard_page.get_property_count() == 0:
            # Add a property first
            property_data = self.data_generator.generate_property_data()
            self.landlord_dashboard_page.add_property(property_data)
            time.sleep(2)
        
        # Get original property details
        original_property = self.landlord_dashboard_page.get_property_details(0)
        
        # Generate updated property data
        updated_data = {
            'title': 'Updated Property Title',
            'price': 2500,
            'description': 'Updated property description'
        }
        
        # Edit the property
        success = self.landlord_dashboard_page.edit_property(0, updated_data)
        assert success, "Property editing should be successful"
        
        # Wait for update
        time.sleep(2)
        
        # Verify changes were applied
        updated_property = self.landlord_dashboard_page.get_property_details(0)
        assert updated_data['title'] in updated_property['title'], "Title should be updated"
        assert str(updated_data['price']) in updated_property['price'], "Price should be updated"
    
    def test_property_status_change(self):
        """Test changing property status"""
        # Ensure there's at least one property
        if self.landlord_dashboard_page.get_property_count() == 0:
            property_data = self.data_generator.generate_property_data()
            self.landlord_dashboard_page.add_property(property_data)
            time.sleep(2)
        
        # Get original status
        original_property = self.landlord_dashboard_page.get_property_details(0)
        original_status = original_property['status']
        
        # Change status
        new_status = 'Inactive' if original_status == 'Active' else 'Active'
        success = self.landlord_dashboard_page.change_property_status(0, new_status)
        
        if success:
            # Wait for update
            time.sleep(2)
            
            # Verify status changed
            updated_property = self.landlord_dashboard_page.get_property_details(0)
            assert new_status in updated_property['status'], f"Status should be changed to {new_status}"
    
    def test_property_status_persistence(self):
        """Test that property status changes persist after page refresh"""
        # Ensure there's at least one property
        if self.landlord_dashboard_page.get_property_count() == 0:
            property_data = self.data_generator.generate_property_data()
            self.landlord_dashboard_page.add_property(property_data)
            time.sleep(2)
        
        # Change status to Inactive
        success = self.landlord_dashboard_page.change_property_status(0, 'Inactive')
        
        if success:
            time.sleep(2)
            
            # Refresh page
            self.landlord_dashboard_page.refresh_page()
            self.landlord_dashboard_page.wait_for_dashboard_to_load()
            self.landlord_dashboard_page.click_my_properties_tab()
            
            # Verify status persisted
            property_details = self.landlord_dashboard_page.get_property_details(0)
            assert 'Inactive' in property_details['status'], "Status should persist after refresh"
    
    def test_delete_property(self):
        """Test property deletion"""
        # Add a property to delete
        property_data = self.data_generator.generate_property_data()
        property_data['title'] = 'Property to Delete'
        self.landlord_dashboard_page.add_property(property_data)
        time.sleep(2)
        
        # Get initial count
        initial_count = self.landlord_dashboard_page.get_property_count()
        
        # Delete the property
        success = self.landlord_dashboard_page.delete_property(0)
        
        if success:
            # Wait for update
            time.sleep(2)
            
            # Verify property was deleted
            new_count = self.landlord_dashboard_page.get_property_count()
            assert new_count == initial_count - 1, "Property count should decrease after deletion"
    
    def test_cancel_property_form(self):
        """Test canceling property form"""
        # Open add property modal
        self.landlord_dashboard_page.click_add_property()
        
        # Fill some data
        partial_data = {
            'title': 'Cancelled Property',
            'location': 'Test Location'
        }
        self.landlord_dashboard_page.fill_property_form(partial_data)
        
        # Cancel form
        self.landlord_dashboard_page.cancel_property_form()
        
        # Verify modal is closed
        assert not self.landlord_dashboard_page.is_element_visible(
            self.landlord_dashboard_page.PROPERTY_MODAL
        ), "Modal should be closed after cancel"
        
        # Verify no property was added
        # This would require checking that the partial data doesn't appear in properties
    
    def test_property_form_with_all_fields(self):
        """Test property form with all fields filled"""
        # Generate comprehensive property data
        property_data = self.data_generator.generate_property_data()
        property_data.update({
            'zero_deposit': True,
            'cooking_ready': True,
            'hot_property': False,
            'description': 'Comprehensive property description with all amenities'
        })
        
        # Add property with all fields
        self.landlord_dashboard_page.add_property(property_data)
        time.sleep(2)
        
        # Verify property was added successfully
        latest_property = self.landlord_dashboard_page.get_property_details(0)
        assert property_data['title'] in latest_property['title'], "Property should be added with all fields"
    
    def test_property_type_selection(self):
        """Test different property type selections"""
        property_types = ['Apartment', 'Condominium', 'House', 'Studio']
        
        for prop_type in property_types:
            property_data = self.data_generator.generate_property_data()
            property_data['property_type'] = prop_type
            property_data['title'] = f'{prop_type} Property'
            
            # Add property with specific type
            self.landlord_dashboard_page.add_property(property_data)
            time.sleep(1)
            
            # Verify property was added
            latest_property = self.landlord_dashboard_page.get_property_details(0)
            assert prop_type in latest_property['title'], f"Should add {prop_type} property"
    
    def test_property_furnishing_options(self):
        """Test different furnishing options"""
        furnishing_options = ['Fully Furnished', 'Partially Furnished', 'Unfurnished']
        
        for furnishing in furnishing_options:
            property_data = self.data_generator.generate_property_data()
            property_data['furnishing'] = furnishing
            property_data['title'] = f'{furnishing} Property'
            
            # Add property with specific furnishing
            self.landlord_dashboard_page.add_property(property_data)
            time.sleep(1)
            
            # Verify property was added
            latest_property = self.landlord_dashboard_page.get_property_details(0)
            assert furnishing.split()[0] in latest_property['title'], f"Should add {furnishing} property"
    
    def test_property_price_validation(self):
        """Test property price validation"""
        # Test with various price formats
        price_tests = [
            {'price': 1500, 'should_work': True},
            {'price': 0, 'should_work': False},
            {'price': -500, 'should_work': False},
            {'price': 999999, 'should_work': True}
        ]
        
        for test_case in price_tests:
            property_data = self.data_generator.generate_property_data()
            property_data['price'] = test_case['price']
            property_data['title'] = f'Price Test {test_case["price"]}'
            
            # Try to add property
            self.landlord_dashboard_page.click_add_property()
            self.landlord_dashboard_page.fill_property_form(property_data)
            
            # Try to save
            self.landlord_dashboard_page.click_element(
                self.landlord_dashboard_page.SAVE_PROPERTY_BUTTON
            )
            
            if test_case['should_work']:
                # Should close modal
                try:
                    self.landlord_dashboard_page.wait_for_element_to_disappear(
                        self.landlord_dashboard_page.PROPERTY_MODAL, timeout=3
                    )
                    success = True
                except:
                    success = False
                    self.landlord_dashboard_page.close_property_modal()
                
                assert success, f"Price {test_case['price']} should be valid"
            else:
                # Should keep modal open
                assert self.landlord_dashboard_page.is_element_visible(
                    self.landlord_dashboard_page.PROPERTY_MODAL
                ), f"Price {test_case['price']} should be invalid"
                self.landlord_dashboard_page.close_property_modal()
    
    def test_property_bedroom_bathroom_validation(self):
        """Test bedroom and bathroom count validation"""
        # Test with various room counts
        room_tests = [
            {'bedrooms': 1, 'bathrooms': 1, 'should_work': True},
            {'bedrooms': 0, 'bathrooms': 1, 'should_work': False},
            {'bedrooms': 1, 'bathrooms': 0, 'should_work': False},
            {'bedrooms': 5, 'bathrooms': 3, 'should_work': True}
        ]
        
        for test_case in room_tests:
            property_data = self.data_generator.generate_property_data()
            property_data.update(test_case)
            property_data['title'] = f'Room Test {test_case["bedrooms"]}BR {test_case["bathrooms"]}BA'
            
            # Try to add property
            self.landlord_dashboard_page.click_add_property()
            self.landlord_dashboard_page.fill_property_form(property_data)
            
            # Try to save
            self.landlord_dashboard_page.click_element(
                self.landlord_dashboard_page.SAVE_PROPERTY_BUTTON
            )
            
            if test_case['should_work']:
                # Should close modal
                try:
                    self.landlord_dashboard_page.wait_for_element_to_disappear(
                        self.landlord_dashboard_page.PROPERTY_MODAL, timeout=3
                    )
                    success = True
                except:
                    success = False
                    self.landlord_dashboard_page.close_property_modal()
                
                assert success, f"Rooms {test_case['bedrooms']}BR {test_case['bathrooms']}BA should be valid"
            else:
                # Should keep modal open
                assert self.landlord_dashboard_page.is_element_visible(
                    self.landlord_dashboard_page.PROPERTY_MODAL
                ), f"Rooms {test_case['bedrooms']}BR {test_case['bathrooms']}BA should be invalid"
                self.landlord_dashboard_page.close_property_modal()
    
    def test_property_special_features(self):
        """Test property special features (checkboxes)"""
        # Test different combinations of special features
        feature_combinations = [
            {'zero_deposit': True, 'cooking_ready': False, 'hot_property': False},
            {'zero_deposit': False, 'cooking_ready': True, 'hot_property': False},
            {'zero_deposit': False, 'cooking_ready': False, 'hot_property': True},
            {'zero_deposit': True, 'cooking_ready': True, 'hot_property': True}
        ]
        
        for features in feature_combinations:
            property_data = self.data_generator.generate_property_data()
            property_data.update(features)
            
            # Create descriptive title
            feature_names = []
            if features['zero_deposit']:
                feature_names.append('ZeroDeposit')
            if features['cooking_ready']:
                feature_names.append('CookingReady')
            if features['hot_property']:
                feature_names.append('HotProperty')
            
            property_data['title'] = f'Features Test {"-".join(feature_names) if feature_names else "None"}'
            
            # Add property with features
            self.landlord_dashboard_page.add_property(property_data)
            time.sleep(1)
            
            # Verify property was added
            latest_property = self.landlord_dashboard_page.get_property_details(0)
            assert 'Features Test' in latest_property['title'], "Property with features should be added"
    
    def test_no_properties_empty_state(self):
        """Test empty state when no properties exist"""
        # This test would require a clean landlord account or ability to delete all properties
        # For now, we'll check if the empty state message exists when appropriate
        
        if self.landlord_dashboard_page.get_property_count() == 0:
            assert not self.landlord_dashboard_page.has_properties(), \
                "Should show no properties message when empty"
    
    def test_property_list_pagination(self):
        """Test property list pagination if implemented"""
        # Add multiple properties to test pagination
        for i in range(5):
            property_data = self.data_generator.generate_property_data()
            property_data['title'] = f'Pagination Test Property {i+1}'
            self.landlord_dashboard_page.add_property(property_data)
            time.sleep(1)
        
        # Verify all properties are displayed or pagination works
        property_count = self.landlord_dashboard_page.get_property_count()
        assert property_count >= 5, "Should display multiple properties"

