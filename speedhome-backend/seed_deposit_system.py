import sys
import os
from datetime import datetime, timedelta, date, time
import random

# This path addition tells the script where its own project root is,
# allowing it to find the 'config' module.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# This adds the backend project to Python's path.
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'speedhome-backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Now we can import from your Flask app
from src.main import app, db
from src.models.user import User
from src.models.property import Property, PropertyStatus
from src.models.booking import Booking
from src.models.application import Application
from src.models.viewing_slot import ViewingSlot
from src.models.tenancy_agreement import TenancyAgreement
from src.models.notification import Notification, NotificationType
from src.models.deposit_transaction import DepositTransaction, DepositTransactionStatus
from src.models.deposit_claim import DepositClaim, DepositClaimStatus, DepositClaimType
from src.models.deposit_dispute import DepositDispute, DepositDisputeStatus, DepositDisputeResponse

# Import test config if available, otherwise use defaults
try:
    from config.test_config import TestConfig
except ImportError:
    class TestConfig:
        LANDLORD_EMAIL = 'landlord@test.com'
        LANDLORD_PASSWORD = 'password123'
        TENANT_EMAIL = 'tenant@test.com'
        TENANT_PASSWORD = 'password123'


def seed_deposit_system():
    """
    Enhanced seed script that creates a complete deposit system test environment.
    """
    with app.app_context():
        print("🌱 Starting enhanced database seed for deposit system...")
        print("Ensuring all tables are created...")
        db.create_all()

        # 1. Clear existing data to ensure a clean slate
        print("🧹 Clearing old data...")
        db.session.query(DepositDispute).delete()
        db.session.query(DepositClaim).delete()
        db.session.query(DepositTransaction).delete()
        db.session.query(TenancyAgreement).delete()
        db.session.query(Application).delete()
        db.session.query(Booking).delete()
        db.session.query(ViewingSlot).delete()
        db.session.query(Notification).delete()
        db.session.query(Property).delete()
        db.session.query(User).delete()
        db.session.commit()

        # 2. Create multiple landlords and tenants
        print("👥 Creating users...")
        
        # Main test landlord
        landlord1 = User(
            username='testlandlord',
            email=TestConfig.LANDLORD_EMAIL,
            first_name='John',
            last_name='Smith',
            role='landlord',
            phone='0123456789',
            is_verified=True
        )
        landlord1.set_password(TestConfig.LANDLORD_PASSWORD)
        db.session.add(landlord1)

        # Additional landlord
        landlord2 = User(
            username='landlord2',
            email='landlord2@test.com',
            first_name='Sarah',
            last_name='Johnson',
            role='landlord',
            phone='0123456790',
            is_verified=True
        )
        landlord2.set_password('password123')
        db.session.add(landlord2)

        # Main test tenant
        tenant1 = User(
            username='testtenant',
            email=TestConfig.TENANT_EMAIL,
            first_name='Alice',
            last_name='Wong',
            role='tenant',
            phone='0123456791',
            is_verified=True
        )
        tenant1.set_password(TestConfig.TENANT_PASSWORD)
        db.session.add(tenant1)

        # Additional tenants
        tenant2 = User(
            username='tenant2',
            email='tenant2@test.com',
            first_name='Bob',
            last_name='Lee',
            role='tenant',
            phone='0123456792',
            is_verified=True
        )
        tenant2.set_password('password123')
        db.session.add(tenant2)

        tenant3 = User(
            username='tenant3',
            email='tenant3@test.com',
            first_name='Carol',
            last_name='Tan',
            role='tenant',
            phone='0123456793',
            is_verified=True
        )
        tenant3.set_password('password123')
        db.session.add(tenant3)

        db.session.commit()
        print(f"✅ Created {User.query.count()} users")

        # 3. Create properties
        print("🏠 Creating properties...")
        
        properties_data = [
            {
                'title': 'Luxury Condo in Cyberjaya',
                'location': 'Cyberjaya',
                'price': 3132,
                'sqft': 1200,
                'bedrooms': 3,
                'bathrooms': 2,
                'parking': 2,
                'property_type': 'Condominium',
                'furnished': 'Fully Furnished',
                'owner': landlord1
            },
            {
                'title': 'Modern Apartment in Petaling Jaya',
                'location': 'Petaling Jaya',
                'price': 3894,
                'sqft': 1461,
                'bedrooms': 1,
                'bathrooms': 1,
                'parking': 1,
                'property_type': 'Terrace House',
                'furnished': 'Partially Furnished',
                'owner': landlord1
            },
            {
                'title': 'Spacious House in Subang Jaya',
                'location': 'Subang Jaya',
                'price': 2800,
                'sqft': 1800,
                'bedrooms': 4,
                'bathrooms': 3,
                'parking': 2,
                'property_type': 'Terrace House',
                'furnished': 'Unfurnished',
                'owner': landlord2
            },
            {
                'title': 'Cozy Studio in KL City',
                'location': 'Kuala Lumpur',
                'price': 1500,
                'sqft': 600,
                'bedrooms': 1,
                'bathrooms': 1,
                'parking': 1,
                'property_type': 'Studio',
                'furnished': 'Fully Furnished',
                'owner': landlord2
            }
        ]

        properties = []
        for prop_data in properties_data:
            property_obj = Property(
                title=prop_data['title'],
                location=prop_data['location'],
                price=prop_data['price'],
                sqft=prop_data['sqft'],
                bedrooms=prop_data['bedrooms'],
                bathrooms=prop_data['bathrooms'],
                parking=prop_data['parking'],
                property_type=prop_data['property_type'],
                furnished=prop_data['furnished'],
                description=f"A wonderful and well-maintained {prop_data['property_type'].lower()} in {prop_data['location']}. Perfect for professionals and families.",
                owner_id=prop_data['owner'].id,
                status=PropertyStatus.ACTIVE
            )
            properties.append(property_obj)
            db.session.add(property_obj)

        db.session.commit()
        print(f"✅ Created {len(properties)} properties")

        # 4. Create tenancy agreements with different statuses
        print("📋 Creating tenancy agreements...")
        
        agreements_data = [
            {
                'property': properties[0],
                'tenant': tenant1,
                'status': 'active',
                'lease_start': date.today() - timedelta(days=30),
                'lease_end': date.today() + timedelta(days=150),  # Not ending soon
                'monthly_rent': properties[0].price,
                'deposit_paid': True
            },
            {
                'property': properties[1],
                'tenant': tenant2,
                'status': 'active',
                'lease_start': date.today() - timedelta(days=60),
                'lease_end': date.today() + timedelta(days=3),  # Ending soon!
                'monthly_rent': properties[1].price,
                'deposit_paid': True
            },
            {
                'property': properties[2],
                'tenant': tenant3,
                'status': 'active',
                'lease_start': date.today() - timedelta(days=90),
                'lease_end': date.today() + timedelta(days=5),  # Ending soon!
                'monthly_rent': properties[2].price,
                'deposit_paid': True
            },
            {
                'property': properties[3],
                'tenant': tenant1,
                'status': 'website_fee_paid',
                'lease_start': date.today() + timedelta(days=30),
                'lease_end': date.today() + timedelta(days=395),
                'monthly_rent': properties[3].price,
                'deposit_paid': False
            }
        ]

        agreements = []
        for i, agreement_data in enumerate(agreements_data):
            # Get landlord info
            landlord = User.query.get(agreement_data['property'].owner_id)
            
            agreement = TenancyAgreement(
                application_id=i + 1,  # Unique application ID for each agreement
                property_id=agreement_data['property'].id,
                property_address=agreement_data['property'].title,
                property_type=agreement_data['property'].property_type,
                property_bedrooms=agreement_data['property'].bedrooms,
                property_bathrooms=agreement_data['property'].bathrooms,
                property_sqft=agreement_data['property'].sqft,
                landlord_id=agreement_data['property'].owner_id,
                landlord_full_name=f"{landlord.first_name} {landlord.last_name}",
                landlord_phone=landlord.phone,
                landlord_email=landlord.email,
                tenant_id=agreement_data['tenant'].id,
                tenant_full_name=f"{agreement_data['tenant'].first_name} {agreement_data['tenant'].last_name}",
                tenant_phone=agreement_data['tenant'].phone,
                tenant_email=agreement_data['tenant'].email,
                monthly_rent=agreement_data['monthly_rent'],
                lease_start_date=agreement_data['lease_start'],
                lease_end_date=agreement_data['lease_end'],
                lease_duration_months=6,
                status=agreement_data['status'],
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 90)),
                landlord_signed_at=datetime.utcnow() - timedelta(days=random.randint(25, 85)),
                tenant_signed_at=datetime.utcnow() - timedelta(days=random.randint(20, 80)),
                payment_completed_at=datetime.utcnow() - timedelta(days=random.randint(15, 75)) if agreement_data['status'] in ['active', 'website_fee_paid'] else None
            )
            agreements.append(agreement)
            db.session.add(agreement)

        db.session.commit()
        print(f"✅ Created {len(agreements)} tenancy agreements")

        # 5. Create deposit transactions for active agreements
        print("💰 Creating deposit transactions...")
        
        deposits = []
        for agreement in agreements:
            if agreement.status == 'active':
                # Calculate deposit amount (2.5 months rent)
                from decimal import Decimal
                deposit_amount = agreement.monthly_rent * Decimal('2.5')
                
                deposit = DepositTransaction(
                    tenancy_agreement_id=agreement.id,
                    property_id=agreement.property_id,
                    tenant_id=agreement.tenant_id,
                    landlord_id=agreement.landlord_id,
                    amount=deposit_amount,
                    calculation_base=agreement.monthly_rent,
                    calculation_multiplier=Decimal('2.5'),
                    adjustments={
                        'security_deposit': float(agreement.monthly_rent * Decimal('2')),
                        'utility_deposit': float(agreement.monthly_rent * Decimal('0.5')),
                        'total': float(deposit_amount)
                    },
                    status=DepositTransactionStatus.HELD_IN_ESCROW,
                    payment_intent_id=f"pi_test_{random.randint(100000, 999999)}",
                    paid_at=datetime.utcnow() - timedelta(days=random.randint(10, 60)),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(15, 65))
                )
                deposits.append(deposit)
                db.session.add(deposit)

        db.session.commit()
        print(f"✅ Created {len(deposits)} deposit transactions")

        # 6. Create some deposit claims and disputes for testing
        print("📋 Creating test claims and disputes...")
        
        # Create a claim for the second deposit (ending soon agreement)
        if len(deposits) >= 2:
            test_deposit = deposits[1]  # Second deposit
            
            claim_items = [
                {
                    'id': 1,
                    'reason': 'cleaning_fees',
                    'reason_display': 'Cleaning Fees',
                    'amount': 200.00,
                    'description': 'Professional cleaning required for kitchen and bathroom areas due to excessive stains and odors.',
                    'evidence_photos': ['kitchen_before.jpg', 'bathroom_stains.jpg'],
                    'evidence_documents': ['cleaning_quote.pdf']
                },
                {
                    'id': 2,
                    'reason': 'repair_damages',
                    'reason_display': 'Repair Damages',
                    'amount': 350.00,
                    'description': 'Repair of damaged wall in living room and replacement of broken cabinet door.',
                    'evidence_photos': ['wall_damage.jpg', 'cabinet_broken.jpg'],
                    'evidence_documents': ['repair_estimate.pdf']
                }
            ]
            
            total_claimed = sum(item['amount'] for item in claim_items)
            
            claim = DepositClaim(
                deposit_transaction_id=test_deposit.id,
                tenancy_agreement_id=test_deposit.tenancy_agreement_id,
                property_id=test_deposit.property_id,
                tenant_id=test_deposit.tenant_id,
                landlord_id=test_deposit.landlord_id,
                claim_type=DepositClaimType.DAMAGE,
                title='Property Damage and Cleaning Claims',
                description='Claims for property damages and required cleaning after tenancy end.',
                claimed_amount=total_claimed,
                status=DepositClaimStatus.SUBMITTED,
                evidence_photos=['kitchen_before.jpg', 'bathroom_stains.jpg', 'wall_damage.jpg', 'cabinet_broken.jpg'],
                evidence_documents=['cleaning_quote.pdf', 'repair_estimate.pdf'],
                tenant_response_deadline=datetime.utcnow() + timedelta(days=7),
                submitted_at=datetime.utcnow() - timedelta(days=2),
                created_at=datetime.utcnow() - timedelta(days=2)
            )
            db.session.add(claim)
            
            # Update deposit status to disputed
            test_deposit.status = DepositTransactionStatus.DISPUTED
            
            db.session.commit()
            print("✅ Created test claim for deposit system testing")

        # 7. Create viewing slots for landlords
        print("📅 Creating viewing slots...")
        
        landlords = [landlord1, landlord2]
        for landlord in landlords:
            for days_ahead in range(1, 15):  # Next 14 days
                slot_date = (datetime.now() + timedelta(days=days_ahead)).date()
                for hour in range(9, 17):  # 9am to 4:30pm
                    for minute in [0, 30]:
                        start_time = time(hour, minute)
                        end_time = (datetime.combine(date.today(), start_time) + timedelta(minutes=30)).time()
                        available_slot = ViewingSlot(
                            landlord_id=landlord.id,
                            date=slot_date,
                            start_time=start_time,
                            end_time=end_time,
                            is_available=True
                        )
                        db.session.add(available_slot)
        
        db.session.commit()
        print(f"✅ Created viewing slots for landlords")

        # 8. Create some sample notifications
        print("🔔 Creating sample notifications...")
        
        notifications_data = [
            {
                'user': tenant1,
                'title': 'Deposit Claim Submitted',
                'message': 'Your landlord has submitted a claim for deductions from your security deposit. Please review and respond within 7 days.',
                'type': 'deposit_claim',
                'is_read': False
            },
            {
                'user': tenant2,
                'title': 'Tenancy Ending Soon',
                'message': 'Your tenancy agreement is ending in 3 days. Your landlord will initiate the deposit release process soon.',
                'type': 'tenancy_ending',
                'is_read': False
            },
            {
                'user': landlord1,
                'title': 'Deposit Ready for Release',
                'message': 'The tenancy for Cyberjaya property is ending soon. You can now release the deposit or make deduction claims.',
                'type': 'deposit_release',
                'is_read': False
            }
        ]

        for notif_data in notifications_data:
            notification = Notification(
                recipient_id=notif_data['user'].id,
                message=notif_data['message'],
                notification_type=NotificationType.DEPOSIT_CLAIM_SUBMITTED if notif_data['type'] == 'deposit_claim' else NotificationType.GENERAL,
                is_read=notif_data['is_read'],
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            )
            db.session.add(notification)

        db.session.commit()
        print(f"✅ Created sample notifications")

        # Final summary
        print("\n🎉 Enhanced database seeding complete!")
        print("=" * 50)
        print(f"📊 Summary:")
        print(f"   👥 Users: {User.query.count()}")
        print(f"   🏠 Properties: {Property.query.count()}")
        print(f"   📋 Tenancy Agreements: {TenancyAgreement.query.count()}")
        print(f"   💰 Deposit Transactions: {DepositTransaction.query.count()}")
        print(f"   📄 Deposit Claims: {DepositClaim.query.count()}")
        print(f"   ⚖️ Deposit Disputes: {DepositDispute.query.count()}")
        print(f"   📅 Viewing Slots: {ViewingSlot.query.count()}")
        print(f"   🔔 Notifications: {Notification.query.count()}")
        print("=" * 50)
        
        print("\n🧪 Test Scenarios Available:")
        print("1. 🟢 Normal deposit (Cyberjaya) - Ready for testing full release")
        print("2. 🟡 Ending tenancy (Petaling Jaya) - Has active claim, ready for dispute testing")
        print("3. 🟡 Ending tenancy (Subang Jaya) - Ready for landlord actions")
        print("4. 🔵 Pending deposit payment (KL City) - Ready for payment testing")
        
        print("\n🔑 Test Credentials:")
        print(f"   Landlord: {TestConfig.LANDLORD_EMAIL} / {TestConfig.LANDLORD_PASSWORD}")
        print(f"   Tenant: {TestConfig.TENANT_EMAIL} / {TestConfig.TENANT_PASSWORD}")
        print(f"   Additional users: tenant2@test.com, tenant3@test.com / password123")
        
        print("\n🚀 Ready for deposit system testing!")
        print("   Navigate to: /deposit-testing")


if __name__ == "__main__":
    seed_deposit_system()

