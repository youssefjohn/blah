"""
Test data generator for creating realistic test data
"""
from faker import Faker
import random
import string
from datetime import datetime, timedelta

class TestDataGenerator:
    """Generate realistic test data for SpeedHome tests"""
    
    def __init__(self):
        self.fake = Faker()
    
    def generate_user_data(self, role='tenant'):
        """Generate user registration data"""
        first_name = self.fake.first_name()
        last_name = self.fake.last_name()
        
        return {
            'email': f"{first_name.lower()}.{last_name.lower()}@test.com",
            'password': 'TestPassword123!',
            'first_name': first_name,
            'last_name': last_name,
            'phone': self.fake.phone_number()[:15],  # Limit phone number length
            'role': role
        }
    
    def generate_property_data(self):
        """Generate property listing data"""
        property_types = ['Apartment', 'Condominium', 'House', 'Townhouse', 'Studio']
        furnishing_types = ['Fully Furnished', 'Partially Furnished', 'Unfurnished']
        locations = ['Kuala Lumpur', 'Petaling Jaya', 'Cyberjaya', 'Puchong', 'Cheras', 'Bangsar']
        
        return {
            'title': f"{self.fake.catch_phrase()} - {random.choice(property_types)}",
            'location': random.choice(locations),
            'price': str(random.randint(800, 5000)),
            'sqft': str(random.randint(500, 2000)),
            'bedrooms': str(random.randint(1, 4)),
            'bathrooms': str(random.randint(1, 3)),
            'parking': str(random.randint(0, 3)),
            'property_type': random.choice(property_types),
            'furnished': random.choice(furnishing_types),
            'description': self.fake.text(max_nb_chars=500),
            'amenities': random.sample([
                'Swimming Pool', 'Gym', 'Security', 'Parking', 'Playground',
                'BBQ Area', 'Laundry', 'Concierge', 'Private Lift', 'Cooking Allowed',
                'Air Conditioning', 'Balcony', 'Water Heater', 'Internet'
            ], k=random.randint(3, 8))
        }
    
    def generate_booking_data(self):
        """Generate viewing request booking data"""
        # Generate future date (1-30 days from now)
        future_date = datetime.now() + timedelta(days=random.randint(1, 30))
        
        # Generate time between 9 AM and 6 PM
        hour = random.randint(9, 18)
        minute = random.choice([0, 30])
        
        return {
            'name': self.fake.name(),
            'email': self.fake.email(),
            'phone': self.fake.phone_number()[:15],
            'date': future_date.strftime('%Y-%m-%d'),
            'time': f"{hour:02d}:{minute:02d}",
            'message': self.fake.text(max_nb_chars=200),
            'occupation': self.fake.job(),
            'monthly_income': str(random.randint(3000, 15000)),
            'number_of_occupants': str(random.randint(1, 4))
        }
    
    def generate_application_data(self):
        """Generate property application data"""
        return {
            'message': f"Hello, I am interested in renting this property. {self.fake.text(max_nb_chars=300)}",
            'occupation': self.fake.job(),
            'company_name': self.fake.company(),
            'monthly_income': str(random.randint(4000, 20000)),
            'move_in_date': (datetime.now() + timedelta(days=random.randint(7, 60))).strftime('%Y-%m-%d'),
            'number_of_occupants': str(random.randint(1, 5)),
            'pets': random.choice(['Yes', 'No']),
            'smoking': random.choice(['Yes', 'No'])
        }
    
    def generate_search_terms(self):
        """Generate search terms for testing"""
        return [
            'luxury',
            'condo',
            'apartment',
            'furnished',
            'KL',
            'Petaling Jaya',
            'swimming pool',
            'parking',
            'security'
        ]
    
    def generate_random_string(self, length=10):
        """Generate random string"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def generate_random_email(self):
        """Generate random email"""
        return f"{self.generate_random_string(8)}@test.com"
    
    def generate_invalid_data(self):
        """Generate invalid data for negative testing"""
        return {
            'invalid_email': 'invalid-email',
            'short_password': '123',
            'empty_string': '',
            'special_chars': '!@#$%^&*()',
            'very_long_string': 'a' * 1000,
            'negative_number': '-100',
            'zero': '0',
            'past_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        }
    
    def generate_filter_combinations(self):
        """Generate different filter combinations for testing"""
        locations = ['All Locations', 'Kuala Lumpur', 'Petaling Jaya', 'Cyberjaya']
        price_ranges = ['all', 'under1000', '1000-2000', '2000-3000', '3000-5000', 'above5000']
        property_types = ['all', 'apartment', 'condo', 'house']
        furnishing = ['all', 'furnished', 'unfurnished']
        
        return {
            'location': random.choice(locations),
            'price': random.choice(price_ranges),
            'type': random.choice(property_types),
            'furnishing': random.choice(furnishing),
            'bedrooms': random.randint(0, 4),
            'bathrooms': random.randint(0, 3),
            'parking': random.randint(0, 3),
            'zero_deposit': random.choice([True, False]),
            'pet_friendly': random.choice([True, False])
        }

