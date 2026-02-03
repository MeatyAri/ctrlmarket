"""Pydantic model validation tests."""

import pytest
from pydantic import ValidationError

from models import (
    LoginCredentials,
    OrderCreate,
    OrderItemCreate,
    OrderUpdateStatus,
    ProductCreate,
    ProductUpdate,
    ServiceRequestCreate,
    ServiceRequestUpdateStatus,
    SessionUser,
    User,
    UserCreate,
    UserUpdate,
)


class TestUserModels:
    """Test User model validation."""

    def test_user_create_valid(self):
        """Test creating a valid user."""
        user = UserCreate(
            name="John Doe",
            email="john@example.com",
            phone="09123456789",
            role="Customer",
            password="password123",
        )
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.role == "Customer"

    def test_user_create_invalid_role(self):
        """Test that invalid role is rejected."""
        with pytest.raises(ValidationError):
            UserCreate(
                name="John Doe",
                email="john@example.com",
                phone="09123456789",
                role="InvalidRole",
                password="password123",
            )

    def test_user_create_password_too_short(self):
        """Test that short password is rejected."""
        with pytest.raises(ValidationError):
            UserCreate(
                name="John Doe",
                email="john@example.com",
                phone="09123456789",
                role="Customer",
                password="short",
            )

    def test_user_create_name_too_long(self):
        """Test that long name is rejected."""
        with pytest.raises(ValidationError):
            UserCreate(
                name="A" * 101,  # Over 100 chars
                email="john@example.com",
                phone="09123456789",
                role="Customer",
                password="password123",
            )

    def test_user_create_empty_name(self):
        """Test that empty name is rejected."""
        with pytest.raises(ValidationError):
            UserCreate(
                name="",
                email="john@example.com",
                phone="09123456789",
                role="Customer",
                password="password123",
            )

    def test_user_update_partial(self):
        """Test partial user update."""
        update = UserUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.email is None
        assert update.role is None

    def test_user_update_invalid_role(self):
        """Test that invalid role in update is rejected."""
        with pytest.raises(ValidationError):
            UserUpdate(role="InvalidRole")


class TestProductModels:
    """Test Product model validation."""

    def test_product_create_valid(self):
        """Test creating a valid product."""
        product = ProductCreate(
            name="Smart Device",
            category="Electronics",
            price=199.99,
        )
        assert product.name == "Smart Device"
        assert product.category == "Electronics"
        assert product.price == 199.99

    def test_product_create_negative_price(self):
        """Test that negative price is rejected."""
        with pytest.raises(ValidationError):
            ProductCreate(
                name="Smart Device",
                category="Electronics",
                price=-10.0,
            )

    def test_product_create_zero_price(self):
        """Test that zero price is accepted."""
        product = ProductCreate(
            name="Free Item",
            category="Promo",
            price=0.0,
        )
        assert product.price == 0.0

    def test_product_create_empty_name(self):
        """Test that empty name is rejected."""
        with pytest.raises(ValidationError):
            ProductCreate(
                name="",
                category="Electronics",
                price=99.99,
            )

    def test_product_update_partial(self):
        """Test partial product update."""
        update = ProductUpdate(price=149.99)
        assert update.price == 149.99
        assert update.name is None
        assert update.category is None

    def test_product_update_negative_price(self):
        """Test that negative price in update is rejected."""
        with pytest.raises(ValidationError):
            ProductUpdate(price=-5.0)


class TestOrderModels:
    """Test Order model validation."""

    def test_order_create_valid(self):
        """Test creating a valid order."""
        order = OrderCreate(
            user_id=1,
            items=[
                OrderItemCreate(product_id=1, quantity=2),
                OrderItemCreate(product_id=2, quantity=1),
            ],
        )
        assert order.user_id == 1
        assert len(order.items) == 2

    def test_order_item_create_valid(self):
        """Test creating a valid order item."""
        item = OrderItemCreate(product_id=1, quantity=3)
        assert item.product_id == 1
        assert item.quantity == 3

    def test_order_item_create_zero_quantity(self):
        """Test that zero quantity is rejected."""
        with pytest.raises(ValidationError):
            OrderItemCreate(product_id=1, quantity=0)

    def test_order_item_create_negative_quantity(self):
        """Test that negative quantity is rejected."""
        with pytest.raises(ValidationError):
            OrderItemCreate(product_id=1, quantity=-1)

    def test_order_update_status_valid(self):
        """Test valid status update."""
        update = OrderUpdateStatus(status="Completed")
        assert update.status == "Completed"

    def test_order_update_status_invalid(self):
        """Test that invalid status is rejected."""
        with pytest.raises(ValidationError):
            OrderUpdateStatus(status="InvalidStatus")


class TestServiceRequestModels:
    """Test ServiceRequest model validation."""

    def test_service_request_create_valid(self):
        """Test creating a valid service request."""
        request = ServiceRequestCreate(
            service_type="Installation",
            customer_id=1,
        )
        assert request.service_type == "Installation"
        assert request.customer_id == 1

    def test_service_request_create_support_type(self):
        """Test creating support type request."""
        request = ServiceRequestCreate(
            service_type="Support",
            customer_id=1,
        )
        assert request.service_type == "Support"

    def test_service_request_create_invalid_type(self):
        """Test that invalid service type is rejected."""
        with pytest.raises(ValidationError):
            ServiceRequestCreate(
                service_type="InvalidType",
                customer_id=1,
            )

    def test_service_request_update_status_valid(self):
        """Test valid status update."""
        for status in ["Pending", "In Progress", "Completed", "Cancelled"]:
            update = ServiceRequestUpdateStatus(status=status)
            assert update.status == status

    def test_service_request_update_status_invalid(self):
        """Test that invalid status is rejected."""
        with pytest.raises(ValidationError):
            ServiceRequestUpdateStatus(status="InvalidStatus")


class TestLoginCredentials:
    """Test LoginCredentials model."""

    def test_login_credentials_valid(self):
        """Test valid login credentials."""
        creds = LoginCredentials(
            email="user@example.com",
            password="password123",
        )
        assert creds.email == "user@example.com"
        assert creds.password == "password123"

    def test_login_credentials_empty_email(self):
        """Test that empty email is accepted (validation happens elsewhere)."""
        creds = LoginCredentials(
            email="",
            password="password123",
        )
        assert creds.email == ""


class TestSessionUser:
    """Test SessionUser model."""

    def test_session_user_valid(self):
        """Test creating a valid session user."""
        user = SessionUser(
            user_id=1,
            name="John Doe",
            email="john@example.com",
            role="Customer",
        )
        assert user.user_id == 1
        assert user.name == "John Doe"
        assert user.role == "Customer"

    def test_session_user_invalid_role(self):
        """Test that invalid role is rejected."""
        with pytest.raises(ValidationError):
            SessionUser(
                user_id=1,
                name="John Doe",
                email="john@example.com",
                role="InvalidRole",
            )


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_user_from_dict(self):
        """Test creating User from dict."""
        data = {
            "user_id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "09123456789",
            "role": "Customer",
            "password_hash": "hashed_password",
        }
        user = User(**data)
        assert user.user_id == 1
        assert user.name == "John Doe"

    def test_user_to_dict(self):
        """Test converting User to dict."""
        user = User(
            user_id=1,
            name="John Doe",
            email="john@example.com",
            phone="09123456789",
            role="Customer",
            password_hash="hashed",
        )
        data = user.model_dump()
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"

    def test_product_from_dict(self):
        """Test creating Product from dict."""
        data = {
            "product_id": 1,
            "name": "Smart Device",
            "category": "Electronics",
            "price": 199.99,
        }
        product = ProductCreate(**data)
        assert product.name == "Smart Device"
        assert product.price == 199.99
