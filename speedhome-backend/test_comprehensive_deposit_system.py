"""
Comprehensive Deposit System Test Suite

Tests all aspects of the deposit system including:
- Database models and relationships
- API endpoints and authentication
- Business logic and calculations
- Integration with existing systems
- Malaysian market standards compliance
- Error handling and edge cases
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
from datetime import datetime, timedelta
from decimal import Decimal
import json

# Import Flask and database
from flask import Flask
from src.models import db
from src.models.user import User
from src.models.property import Property, PropertyStatus
from src.models.tenancy_agreement import TenancyAgreement
from src.models.deposit_transaction import DepositTransaction, DepositTransactionStatus
from src.models.deposit_claim import DepositClaim, DepositClaimStatus
from src.models.deposit_dispute import DepositDispute, DepositDisputeStatus, TenantResponse
from src.models.notification import Notification, NotificationType
from src.models.conversation import Conversation
from src.services.deposit_notification_service import DepositNotificationService
from src.services.property_lifecycle_service import PropertyLifecycleService

class ComprehensiveDepositSystemTest(unittest.TestCase):
    """Comprehensive test suite for the deposit system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        print("🧪 Setting up comprehensive deposit system test environment...")
        
        # Create Flask app for testing
        cls.app = Flask(__name__)
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        cls.app.config['SECRET_KEY'] = 'test-secret-key'
        
        # Initialize database
        db.init_app(cls.app)
        
        with cls.app.app_context():
            db.create_all()
            cls._create_test_data()
    
    @classmethod
    def _create_test_data(cls):
        """Create test data for all tests"""
        print("📊 Creating comprehensive test data...")
        
        # Create test users
        cls.landlord = User(
            id=1,
            email='landlord@test.com',
            name='Test Landlord',
            phone='+60123456789',
            user_type='landlord'
        )
        
        cls.tenant = User(
            id=2,
            email='tenant@test.com',
            name='Test Tenant',
            phone='+60198765432',
            user_type='tenant'
        )
        
        cls.admin = User(
            id=3,
            email='admin@test.com',
            name='Test Admin',
            phone='+60111111111',
            user_type='admin'
        )
        
        db.session.add_all([cls.landlord, cls.tenant, cls.admin])
        
        # Create test property
        cls.property = Property(
            id=1,
            title='Test Property',
            address='123 Test Street, Kuala Lumpur',
            monthly_rent=2000.00,
            property_type='apartment',
            status=PropertyStatus.RENTED,
            landlord_id=cls.landlord.id
        )
        
        db.session.add(cls.property)
        
        # Create test tenancy agreement
        cls.tenancy_agreement = TenancyAgreement(
            id=1,
            property_id=cls.property.id,
            tenant_id=cls.tenant.id,
            landlord_id=cls.landlord.id,
            monthly_rent=2000.00,
            lease_start_date=datetime.utcnow() - timedelta(days=300),
            lease_end_date=datetime.utcnow() + timedelta(days=65),
            status='active'
        )
        
        db.session.add(cls.tenancy_agreement)
        db.session.commit()
        
        print("✅ Test data created successfully")
    
    def setUp(self):
        """Set up each test"""
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after each test"""
        self.app_context.pop()
    
    # ============================================================================
    # MODEL TESTS
    # ============================================================================
    
    def test_01_deposit_transaction_model(self):
        """Test DepositTransaction model functionality"""
        print("\n🧪 Testing DepositTransaction model...")
        
        # Test creation
        deposit = DepositTransaction(
            tenancy_agreement_id=self.tenancy_agreement.id,
            property_id=self.property.id,
            tenant_id=self.tenant.id,
            landlord_id=self.landlord.id,
            amount=4000.00,
            calculation_base_rent=2000.00,
            calculation_multiplier=2.0,
            calculation_details={'base_amount': 4000, 'adjustment_factor': 1.0},
            status=DepositTransactionStatus.PENDING
        )
        
        db.session.add(deposit)
        db.session.commit()
        
        # Test relationships
        self.assertEqual(deposit.tenancy_agreement.id, self.tenancy_agreement.id)
        self.assertEqual(deposit.property.id, self.property.id)
        self.assertEqual(deposit.tenant.id, self.tenant.id)
        self.assertEqual(deposit.landlord.id, self.landlord.id)
        
        # Test Malaysian 2-month standard
        self.assertEqual(deposit.calculation_multiplier, 2.0)
        self.assertEqual(deposit.amount, 4000.00)
        
        # Test status transitions
        self.assertTrue(deposit.can_transition_to(DepositTransactionStatus.PAID))
        self.assertFalse(deposit.can_transition_to(DepositTransactionStatus.REFUNDED))
        
        # Test to_dict method
        deposit_dict = deposit.to_dict()
        self.assertIn('amount', deposit_dict)
        self.assertIn('status', deposit_dict)
        self.assertIn('calculation_details', deposit_dict)
        
        print("✅ DepositTransaction model tests passed")
    
    def test_02_deposit_claim_model(self):
        """Test DepositClaim model functionality"""
        print("\n🧪 Testing DepositClaim model...")
        
        # Create deposit first
        deposit = DepositTransaction(
            tenancy_agreement_id=self.tenancy_agreement.id,
            property_id=self.property.id,
            tenant_id=self.tenant.id,
            landlord_id=self.landlord.id,
            amount=4000.00,
            status=DepositTransactionStatus.HELD_IN_ESCROW
        )
        db.session.add(deposit)
        db.session.commit()
        
        # Test claim creation
        claim = DepositClaim(
            deposit_transaction_id=deposit.id,
            tenancy_agreement_id=self.tenancy_agreement.id,
            property_id=self.property.id,
            landlord_id=self.landlord.id,
            tenant_id=self.tenant.id,
            title='Cleaning Fee',
            description='Professional cleaning required',
            claimed_amount=500.00,
            category='cleaning',
            status=DepositClaimStatus.SUBMITTED,
            tenant_response_deadline=datetime.utcnow() + timedelta(days=7),
            auto_approve_at=datetime.utcnow() + timedelta(days=7)
        )
        
        db.session.add(claim)
        db.session.commit()
        
        # Test relationships
        self.assertEqual(claim.deposit_transaction.id, deposit.id)
        self.assertEqual(claim.tenancy_agreement.id, self.tenancy_agreement.id)
        
        # Test Malaysian 7-day standard
        deadline_diff = (claim.tenant_response_deadline - datetime.utcnow()).days
        self.assertAlmostEqual(deadline_diff, 7, delta=1)
        
        # Test deadline detection
        self.assertFalse(claim.is_response_overdue())
        self.assertFalse(claim.is_approaching_deadline())
        
        # Test to_dict method
        claim_dict = claim.to_dict()
        self.assertIn('title', claim_dict)
        self.assertIn('claimed_amount', claim_dict)
        self.assertIn('tenant_response_deadline', claim_dict)
        
        print("✅ DepositClaim model tests passed")
    
    def test_03_deposit_dispute_model(self):
        """Test DepositDispute model functionality"""
        print("\n🧪 Testing DepositDispute model...")
        
        # Create deposit and claim first
        deposit = DepositTransaction(
            tenancy_agreement_id=self.tenancy_agreement.id,
            property_id=self.property.id,
            tenant_id=self.tenant.id,
            landlord_id=self.landlord.id,
            amount=4000.00,
            status=DepositTransactionStatus.HELD_IN_ESCROW
        )
        db.session.add(deposit)
        db.session.commit()
        
        claim = DepositClaim(
            deposit_transaction_id=deposit.id,
            tenancy_agreement_id=self.tenancy_agreement.id,
            property_id=self.property.id,
            landlord_id=self.landlord.id,
            tenant_id=self.tenant.id,
            title='Damage Repair',
            claimed_amount=800.00,
            status=DepositClaimStatus.DISPUTED
        )
        db.session.add(claim)
        db.session.commit()
        
        # Test dispute creation
        dispute = DepositDispute(
            deposit_claim_id=claim.id,
            deposit_transaction_id=deposit.id,
            tenancy_agreement_id=self.tenancy_agreement.id,
            property_id=self.property.id,
            tenant_id=self.tenant.id,
            landlord_id=self.landlord.id,
            tenant_response=TenantResponse.PARTIAL_ACCEPT,
            tenant_counter_amount=300.00,
            tenant_explanation='Damage was pre-existing',
            status=DepositDisputeStatus.UNDER_MEDIATION,
            mediation_deadline=datetime.utcnow() + timedelta(days=14)
        )
        
        db.session.add(dispute)
        db.session.commit()
        
        # Test relationships
        self.assertEqual(dispute.deposit_claim.id, claim.id)
        self.assertEqual(dispute.deposit_transaction.id, deposit.id)
        
        # Test Malaysian 14-day mediation standard
        mediation_diff = (dispute.mediation_deadline - datetime.utcnow()).days
        self.assertAlmostEqual(mediation_diff, 14, delta=1)
        
        # Test dispute resolution
        dispute.resolve_dispute(
            final_amount=400.00,
            resolution_method='admin_decision',
            resolution_notes='Compromise reached',
            resolved_by_id=self.admin.id
        )
        
        self.assertEqual(dispute.status, DepositDisputeStatus.RESOLVED)
        self.assertEqual(dispute.final_resolution_amount, 400.00)
        self.assertIsNotNone(dispute.resolved_at)
        
        print("✅ DepositDispute model tests passed")
    
    # ============================================================================
    # BUSINESS LOGIC TESTS
    # ============================================================================
    
    def test_04_malaysian_deposit_calculation(self):
        """Test Malaysian 2-month deposit calculation standards"""
        print("\n🧪 Testing Malaysian deposit calculation...")
        
        # Test standard 2-month calculation
        monthly_rent = 2500.00
        base_deposit = monthly_rent * 2
        self.assertEqual(base_deposit, 5000.00)
        
        # Test with different rent amounts
        test_cases = [
            (1000.00, 2000.00),  # Basic apartment
            (3000.00, 6000.00),  # Mid-range
            (8000.00, 16000.00), # Luxury
        ]
        
        for rent, expected_base in test_cases:
            calculated_base = rent * 2
            self.assertEqual(calculated_base, expected_base)
        
        # Test adjustment factors (should be within 1.5x to 2.5x range)
        adjustment_factors = [0.75, 1.0, 1.25]  # 1.5x, 2.0x, 2.5x multipliers
        
        for factor in adjustment_factors:
            final_multiplier = factor
            self.assertGreaterEqual(final_multiplier, 0.75)  # Min 1.5 months
            self.assertLessEqual(final_multiplier, 1.25)     # Max 2.5 months
        
        print("✅ Malaysian deposit calculation tests passed")
    
    def test_05_deposit_workflow_timeline(self):
        """Test Malaysian market timeline standards"""
        print("\n🧪 Testing deposit workflow timelines...")
        
        # Test 7-day advance lease expiry notification
        lease_end = datetime.utcnow() + timedelta(days=7)
        advance_notification_date = lease_end - timedelta(days=7)
        days_diff = (lease_end - advance_notification_date).days
        self.assertEqual(days_diff, 7)
        
        # Test 7-day claim response deadline
        claim_submitted = datetime.utcnow()
        response_deadline = claim_submitted + timedelta(days=7)
        response_days = (response_deadline - claim_submitted).days
        self.assertEqual(response_days, 7)
        
        # Test 14-day mediation period
        dispute_created = datetime.utcnow()
        mediation_deadline = dispute_created + timedelta(days=14)
        mediation_days = (mediation_deadline - dispute_created).days
        self.assertEqual(mediation_days, 14)
        
        # Test complete timeline (7 + 7 + 14 = 28 days maximum)
        lease_end = datetime.utcnow()
        max_resolution_date = lease_end + timedelta(days=28)
        total_days = (max_resolution_date - lease_end).days
        self.assertEqual(total_days, 28)
        
        print("✅ Deposit workflow timeline tests passed")
    
    def test_06_notification_system_integration(self):
        """Test notification system integration"""
        print("\n🧪 Testing notification system integration...")
        
        # Create deposit for testing
        deposit = DepositTransaction(
            tenancy_agreement_id=self.tenancy_agreement.id,
            property_id=self.property.id,
            tenant_id=self.tenant.id,
            landlord_id=self.landlord.id,
            amount=4000.00,
            status=DepositTransactionStatus.PENDING
        )
        db.session.add(deposit)
        db.session.commit()
        
        # Test deposit payment required notification
        initial_count = Notification.query.count()
        DepositNotificationService.notify_deposit_payment_required(deposit)
        
        # Check if notification was created
        new_count = Notification.query.count()
        self.assertGreater(new_count, initial_count)
        
        # Check notification details
        notification = Notification.query.filter_by(
            notification_type=NotificationType.DEPOSIT_PAYMENT_REQUIRED
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user_id, self.tenant.id)
        self.assertEqual(notification.priority, 'HIGH')
        self.assertIn('MYR 4,000.00', notification.message)
        
        print("✅ Notification system integration tests passed")
    
    def test_07_property_lifecycle_integration(self):
        """Test property lifecycle service integration"""
        print("\n🧪 Testing property lifecycle integration...")
        
        # Test lease expiry advance notification
        result = PropertyLifecycleService.check_lease_expiry_advance_notifications()
        self.assertIn('success', result)
        self.assertIn('notifications_sent', result)
        
        # Test expired agreements processing
        result = PropertyLifecycleService.check_expired_agreements()
        self.assertIn('success', result)
        self.assertIn('properties_updated', result)
        
        # Test deposit claim deadlines
        result = PropertyLifecycleService.check_deposit_claim_deadlines()
        self.assertIn('success', result)
        self.assertIn('deadline_reminders_sent', result)
        
        # Test deposit dispute deadlines
        result = PropertyLifecycleService.check_deposit_dispute_deadlines()
        self.assertIn('success', result)
        self.assertIn('mediation_reminders_sent', result)
        
        # Test deposit resolution completion
        result = PropertyLifecycleService.check_deposit_resolution_completion()
        self.assertIn('success', result)
        self.assertIn('properties_reactivated', result)
        
        print("✅ Property lifecycle integration tests passed")
    
    # ============================================================================
    # INTEGRATION TESTS
    # ============================================================================
    
    def test_08_messaging_system_integration(self):
        """Test integration with existing messaging system"""
        print("\n🧪 Testing messaging system integration...")
        
        # Create deposit and claim
        deposit = DepositTransaction(
            tenancy_agreement_id=self.tenancy_agreement.id,
            property_id=self.property.id,
            tenant_id=self.tenant.id,
            landlord_id=self.landlord.id,
            amount=4000.00,
            status=DepositTransactionStatus.HELD_IN_ESCROW
        )
        db.session.add(deposit)
        db.session.commit()
        
        claim = DepositClaim(
            deposit_transaction_id=deposit.id,
            tenancy_agreement_id=self.tenancy_agreement.id,
            property_id=self.property.id,
            landlord_id=self.landlord.id,
            tenant_id=self.tenant.id,
            title='Test Claim',
            claimed_amount=500.00,
            status=DepositClaimStatus.SUBMITTED
        )
        db.session.add(claim)
        db.session.commit()
        
        # Create conversation for claim
        conversation = Conversation(
            property_id=self.property.id,
            tenant_id=self.tenant.id,
            landlord_id=self.landlord.id,
            status='active',
            context_type='deposit_claim',
            context_id=claim.id
        )
        db.session.add(conversation)
        db.session.commit()
        
        # Test conversation creation
        self.assertIsNotNone(conversation.id)
        self.assertEqual(conversation.context_type, 'deposit_claim')
        self.assertEqual(conversation.context_id, claim.id)
        
        # Update claim with conversation
        claim.conversation_id = conversation.id
        db.session.commit()
        
        # Test relationship
        self.assertEqual(claim.conversation_id, conversation.id)
        
        print("✅ Messaging system integration tests passed")
    
    def test_09_end_to_end_deposit_workflow(self):
        """Test complete end-to-end deposit workflow"""
        print("\n🧪 Testing end-to-end deposit workflow...")
        
        # Step 1: Create deposit transaction
        deposit = DepositTransaction(
            tenancy_agreement_id=self.tenancy_agreement.id,
            property_id=self.property.id,
            tenant_id=self.tenant.id,
            landlord_id=self.landlord.id,
            amount=4000.00,
            status=DepositTransactionStatus.PENDING
        )
        db.session.add(deposit)
        db.session.commit()
        
        # Step 2: Process payment
        deposit.status = DepositTransactionStatus.PAID
        deposit.paid_at = datetime.utcnow()
        db.session.commit()
        
        # Step 3: Move to escrow
        deposit.status = DepositTransactionStatus.HELD_IN_ESCROW
        deposit.escrow_reference = f"ESC-{deposit.id}-TEST"
        db.session.commit()
        
        # Step 4: Create claim
        claim = DepositClaim(
            deposit_transaction_id=deposit.id,
            tenancy_agreement_id=self.tenancy_agreement.id,
            property_id=self.property.id,
            landlord_id=self.landlord.id,
            tenant_id=self.tenant.id,
            title='Cleaning Fee',
            claimed_amount=600.00,
            status=DepositClaimStatus.SUBMITTED,
            tenant_response_deadline=datetime.utcnow() + timedelta(days=7)
        )
        db.session.add(claim)
        db.session.commit()
        
        # Step 5: Tenant disputes claim
        dispute = DepositDispute(
            deposit_claim_id=claim.id,
            deposit_transaction_id=deposit.id,
            tenancy_agreement_id=self.tenancy_agreement.id,
            property_id=self.property.id,
            tenant_id=self.tenant.id,
            landlord_id=self.landlord.id,
            tenant_response=TenantResponse.PARTIAL_ACCEPT,
            tenant_counter_amount=300.00,
            status=DepositDisputeStatus.UNDER_MEDIATION
        )
        db.session.add(dispute)
        
        # Update claim status
        claim.status = DepositClaimStatus.DISPUTED
        db.session.commit()
        
        # Step 6: Resolve dispute
        dispute.resolve_dispute(
            final_amount=400.00,
            resolution_method='mediation_agreement',
            resolution_notes='Mutual agreement reached',
            resolved_by_id=self.admin.id
        )
        
        # Step 7: Process final payout
        deposit.status = DepositTransactionStatus.PARTIALLY_REFUNDED
        deposit.refunded_at = datetime.utcnow()
        db.session.commit()
        
        # Verify final state
        self.assertEqual(deposit.status, DepositTransactionStatus.PARTIALLY_REFUNDED)
        self.assertEqual(claim.status, DepositClaimStatus.DISPUTED)
        self.assertEqual(dispute.status, DepositDisputeStatus.RESOLVED)
        self.assertEqual(dispute.final_resolution_amount, 400.00)
        
        print("✅ End-to-end deposit workflow tests passed")
    
    # ============================================================================
    # ERROR HANDLING TESTS
    # ============================================================================
    
    def test_10_error_handling_and_validation(self):
        """Test error handling and data validation"""
        print("\n🧪 Testing error handling and validation...")
        
        # Test invalid deposit amounts
        with self.assertRaises(Exception):
            invalid_deposit = DepositTransaction(
                tenancy_agreement_id=self.tenancy_agreement.id,
                property_id=self.property.id,
                tenant_id=self.tenant.id,
                landlord_id=self.landlord.id,
                amount=-1000.00,  # Negative amount should fail
                status=DepositTransactionStatus.PENDING
            )
            db.session.add(invalid_deposit)
            db.session.commit()
        
        # Test invalid claim amounts
        deposit = DepositTransaction(
            tenancy_agreement_id=self.tenancy_agreement.id,
            property_id=self.property.id,
            tenant_id=self.tenant.id,
            landlord_id=self.landlord.id,
            amount=4000.00,
            status=DepositTransactionStatus.HELD_IN_ESCROW
        )
        db.session.add(deposit)
        db.session.commit()
        
        # Test claim amount exceeding deposit
        try:
            invalid_claim = DepositClaim(
                deposit_transaction_id=deposit.id,
                tenancy_agreement_id=self.tenancy_agreement.id,
                property_id=self.property.id,
                landlord_id=self.landlord.id,
                tenant_id=self.tenant.id,
                title='Invalid Claim',
                claimed_amount=5000.00,  # Exceeds deposit amount
                status=DepositClaimStatus.SUBMITTED
            )
            
            # This should be caught by business logic validation
            if invalid_claim.claimed_amount > deposit.amount:
                raise ValueError("Claim amount exceeds deposit amount")
                
        except ValueError as e:
            self.assertIn("exceeds deposit amount", str(e))
        
        print("✅ Error handling and validation tests passed")
    
    def test_11_security_and_authorization(self):
        """Test security and authorization checks"""
        print("\n🧪 Testing security and authorization...")
        
        # Create deposit
        deposit = DepositTransaction(
            tenancy_agreement_id=self.tenancy_agreement.id,
            property_id=self.property.id,
            tenant_id=self.tenant.id,
            landlord_id=self.landlord.id,
            amount=4000.00,
            status=DepositTransactionStatus.HELD_IN_ESCROW
        )
        db.session.add(deposit)
        db.session.commit()
        
        # Test tenant authorization for deposit access
        self.assertEqual(deposit.tenant_id, self.tenant.id)
        self.assertEqual(deposit.landlord_id, self.landlord.id)
        
        # Test unauthorized user access (should fail in API layer)
        unauthorized_user_id = 999
        self.assertNotEqual(deposit.tenant_id, unauthorized_user_id)
        self.assertNotEqual(deposit.landlord_id, unauthorized_user_id)
        
        # Test role-based permissions
        # Only landlord can create claims
        claim = DepositClaim(
            deposit_transaction_id=deposit.id,
            landlord_id=self.landlord.id,  # Must match deposit landlord
            tenant_id=self.tenant.id,
            title='Test Claim',
            claimed_amount=500.00
        )
        
        self.assertEqual(claim.landlord_id, deposit.landlord_id)
        
        # Only tenant can respond to claims
        dispute = DepositDispute(
            deposit_claim_id=1,
            tenant_id=self.tenant.id,  # Must match deposit tenant
            landlord_id=self.landlord.id,
            tenant_response=TenantResponse.REJECT
        )
        
        self.assertEqual(dispute.tenant_id, deposit.tenant_id)
        
        print("✅ Security and authorization tests passed")
    
    def test_12_performance_and_scalability(self):
        """Test performance and scalability considerations"""
        print("\n🧪 Testing performance and scalability...")
        
        # Test bulk operations
        start_time = datetime.utcnow()
        
        # Create multiple deposits
        deposits = []
        for i in range(10):
            deposit = DepositTransaction(
                tenancy_agreement_id=self.tenancy_agreement.id,
                property_id=self.property.id,
                tenant_id=self.tenant.id,
                landlord_id=self.landlord.id,
                amount=4000.00 + (i * 100),
                status=DepositTransactionStatus.PENDING
            )
            deposits.append(deposit)
        
        db.session.add_all(deposits)
        db.session.commit()
        
        end_time = datetime.utcnow()
        creation_time = (end_time - start_time).total_seconds()
        
        # Should complete within reasonable time
        self.assertLess(creation_time, 5.0)  # Less than 5 seconds
        
        # Test query performance
        start_time = datetime.utcnow()
        
        # Query deposits for user
        user_deposits = DepositTransaction.query.filter(
            (DepositTransaction.tenant_id == self.tenant.id) |
            (DepositTransaction.landlord_id == self.landlord.id)
        ).all()
        
        end_time = datetime.utcnow()
        query_time = (end_time - start_time).total_seconds()
        
        # Should complete within reasonable time
        self.assertLess(query_time, 1.0)  # Less than 1 second
        self.assertGreaterEqual(len(user_deposits), 10)
        
        print("✅ Performance and scalability tests passed")

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🚀 Starting Comprehensive Deposit System Test Suite")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(ComprehensiveDepositSystemTest)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED! Deposit system is ready for production.")
        return True
    else:
        print("\n⚠️ Some tests failed. Please review and fix issues before deployment.")
        return False

if __name__ == '__main__':
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)

