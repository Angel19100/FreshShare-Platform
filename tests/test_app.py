"""
Test suite for Fresh-Share Platform
Run with: pytest tests/ -v
"""
import pytest
from datetime import datetime, timedelta, timezone
from src.app import create_app
from src.models import db, User, FoodListing, UserRole, FoodType, ListingStatus
from src.observers.notification_observer import NotificationService, EmailNotifier


@pytest.fixture
def app():
    """Create and configure test application"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture
def vendor_user(app):
    """Create test vendor user"""
    with app.app_context():
        user = User(
            email="vendor@test.com",
            name="Test Vendor",
            role=UserRole.VENDOR,
            latitude=40.7128,
            longitude=-74.0060
        )
        user.set_password("password123")
        user.location = f"POINT({user.longitude} {user.latitude})"
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def charity_user(app):
    """Create test charity user"""
    with app.app_context():
        user = User(
            email="charity@test.com",
            name="Test Charity",
            role=UserRole.CHARITY,
            latitude=40.7138,  # Nearby location
            longitude=-74.0070,
            verified=True
        )
        user.set_password("password123")
        user.location = f"POINT({user.longitude} {user.latitude})"
        db.session.add(user)
        db.session.commit()
        return user


class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_register_user(self, client):
        """Test user registration"""
        response = client.post('/api/auth/register', json={
            "email": "newvendor@test.com",
            "password": "password123",
            "name": "New Vendor",
            "role": "vendor",
            "latitude": 40.7128,
            "longitude": -74.0060
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == "User registered successfully"
        assert data['user']['email'] == "newvendor@test.com"
    
    def test_register_duplicate_user(self, client, vendor_user):
        """Test registering duplicate email"""
        response = client.post('/api/auth/register', json={
            "email": "vendor@test.com",
            "password": "password123",
            "name": "Duplicate Vendor",
            "role": "vendor"
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert "already exists" in data['error']
    
    def test_login_success(self, client, vendor_user):
        """Test successful login"""
        response = client.post('/api/auth/login', json={
            "email": "vendor@test.com",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == "vendor@test.com"
    
    def test_login_invalid_credentials(self, client, vendor_user):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login', json={
            "email": "vendor@test.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401


class TestListings:
    """Test listing endpoints"""
    
    @pytest.fixture
    def auth_headers(self, client, vendor_user):
        """Get authentication headers"""
        response = client.post('/api/auth/login', json={
            "email": "vendor@test.com",
            "password": "password123"
        })
        token = response.get_json()['access_token']
        return {'Authorization': f'Bearer {token}'}


class TestObserverPattern:
    """Test Observer pattern implementation"""
    
    def test_notification_service_attach(self):
        """Test attaching observers"""
        service = NotificationService()
        observer = EmailNotifier()
        
        initial_count = service.get_observer_count()
        service.attach(observer)
        
        assert service.get_observer_count() == initial_count + 1
    
    def test_notification_service_detach(self):
        """Test detaching observers"""
        service = NotificationService()
        observer = EmailNotifier()
        
        service.attach(observer)
        initial_count = service.get_observer_count()
        service.detach(observer)
        
        assert service.get_observer_count() == initial_count - 1
    
    def test_notification_service_notify(self):
        """Test notifying observers"""
        service = NotificationService()
        service.attach(EmailNotifier())
        
        listing_data = {
            'id': 1,
            'vendor_id': 1,
            'title': 'Test Food',
            'quantity': 10,
            'unit': 'kg',
            'pickup_address': 'Test Address',
            'expiry_time': datetime.now(timezone.utc).isoformat()
        }
        
        users_data = [
            {
                'id': 2,
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': '+1234567890'
            }
        ]
        
        # Should not raise any exceptions
        notification_count = service.notify(listing_data, users_data)
        assert notification_count >= 0


class TestModels:
    """Test database models"""
    
    def test_user_password_hashing(self, app):
        """Test password hashing and verification"""
        with app.app_context():
            user = User(
                email="test@test.com",
                name="Test User",
                role=UserRole.VENDOR
            )
            user.set_password("testpassword")
            
            assert user.password_hash != "testpassword"
            assert user.check_password("testpassword")
            assert not user.check_password("wrongpassword")
    
    def test_user_to_dict(self, vendor_user, app):
        """Test user to_dict method"""
        with app.app_context():
            user = User.query.filter_by(email="vendor@test.com").first()
            user_dict = user.to_dict()
            
            assert user_dict['email'] == "vendor@test.com"
            assert user_dict['role'] == "vendor"
            assert 'password_hash' not in user_dict
    
    def test_listing_to_dict(self, app, vendor_user):
        """Test listing to_dict method"""
        with app.app_context():
            vendor = User.query.filter_by(email="vendor@test.com").first()
            listing = FoodListing(
                vendor_id=vendor.id,
                title="Test Listing",
                quantity=5,
                unit="kg",
                food_type=FoodType.BAKERY,
                expiry_time=datetime.now(timezone.utc) + timedelta(hours=6),
                pickup_address="123 Test St",
                latitude=40.7128,
                longitude=-74.0060
            )
            db.session.add(listing)
            db.session.commit()
            
            listing_dict = listing.to_dict()
            
            assert listing_dict['title'] == "Test Listing"
            assert listing_dict['vendor_name'] == "Test Vendor"
            assert listing_dict['food_type'] == "bakery"


if __name__ == '__main__':
    pytest.main(['-v', 'tests/'])
