"""Database queries tests - CRUD operations for all entities."""

import pytest
from database import queries
from models import (
    LoginCredentials,
    OrderCreate,
    OrderItemCreate,
    OrderUpdateStatus,
    ProductCreate,
    ProductUpdate,
    ServiceRequestCreate,
    ServiceRequestUpdateStatus,
    UserCreate,
    UserUpdate,
)


class TestAuthenticationQueries:
    """Test authentication-related queries."""

    def test_authenticate_user_valid_credentials(self, mock_db_path, hash_password):
        """Test authenticating a user with valid credentials."""
        # Create a user first
        password = "testpass123"
        password_hash = hash_password(password)
        user = UserCreate(
            name="Auth Test",
            email="auth_test@example.com",
            phone="09123456789",
            role="Customer",
            password=password,
        )
        created_user = queries.create_user(user, password_hash)

        # Authenticate
        credentials = LoginCredentials(email="auth_test@example.com", password=password)
        session_user = queries.authenticate_user(credentials)

        assert session_user is not None
        assert session_user.user_id == created_user.user_id
        assert session_user.name == "Auth Test"
        assert session_user.email == "auth_test@example.com"
        assert session_user.role == "Customer"

    def test_authenticate_user_invalid_email(self, mock_db_path):
        """Test authenticating with non-existent email."""
        credentials = LoginCredentials(
            email="nonexistent@example.com", password="password"
        )
        session_user = queries.authenticate_user(credentials)
        assert session_user is None

    def test_get_user_password_hash_existing_user(self, mock_db_path, hash_password):
        """Test getting password hash for existing user."""
        password_hash = hash_password("password123")
        user = UserCreate(
            name="Hash Test",
            email="hash_test@example.com",
            phone="09123456789",
            role="Customer",
            password="password123",
        )
        queries.create_user(user, password_hash)

        retrieved_hash = queries.get_user_password_hash("hash_test@example.com")
        assert retrieved_hash == password_hash

    def test_get_user_password_hash_nonexistent_user(self, mock_db_path):
        """Test getting password hash for non-existent user."""
        password_hash = queries.get_user_password_hash("nonexistent@example.com")
        assert password_hash is None


class TestUserQueries:
    """Test user CRUD operations."""

    def test_create_user(self, mock_db_path, hash_password):
        """Test creating a new user."""
        password_hash = hash_password("password123")
        user = UserCreate(
            name="John Doe",
            email="john@example.com",
            phone="09123456789",
            role="Customer",
            password="password123",
        )
        created = queries.create_user(user, password_hash)

        assert created.user_id is not None
        assert created.name == "John Doe"
        assert created.email == "john@example.com"
        assert created.phone == "09123456789"
        assert created.role == "Customer"
        assert created.password_hash == password_hash

    def test_get_user_by_id_existing(self, mock_db_path, hash_password):
        """Test getting user by ID."""
        password_hash = hash_password("password123")
        user = UserCreate(
            name="Jane Doe",
            email="jane@example.com",
            phone="09123456789",
            role="Specialist",
            password="password123",
        )
        created = queries.create_user(user, password_hash)

        retrieved = queries.get_user_by_id(created.user_id)
        assert retrieved is not None
        assert retrieved.user_id == created.user_id
        assert retrieved.name == "Jane Doe"

    def test_get_user_by_id_nonexistent(self, mock_db_path):
        """Test getting non-existent user by ID."""
        user = queries.get_user_by_id(99999)
        assert user is None

    def test_get_user_by_email_existing(self, mock_db_path, hash_password):
        """Test getting user by email."""
        password_hash = hash_password("password123")
        user = UserCreate(
            name="Bob Smith",
            email="bob@example.com",
            phone="09123456789",
            role="Admin",
            password="password123",
        )
        queries.create_user(user, password_hash)

        retrieved = queries.get_user_by_email("bob@example.com")
        assert retrieved is not None
        assert retrieved.email == "bob@example.com"
        assert retrieved.name == "Bob Smith"

    def test_get_user_by_email_nonexistent(self, mock_db_path):
        """Test getting non-existent user by email."""
        user = queries.get_user_by_email("nonexistent@example.com")
        assert user is None

    def test_list_users_all(self, mock_db_path):
        """Test listing all users."""
        users = queries.list_users()
        # Should have seed data users
        assert len(users) >= 6  # 1 admin + 2 specialists + 3 customers

    def test_list_users_filter_by_role(self, mock_db_path):
        """Test listing users filtered by role."""
        customers = queries.list_users(role="Customer")
        assert len(customers) >= 3
        for user in customers:
            assert user.role == "Customer"

        specialists = queries.list_users(role="Specialist")
        assert len(specialists) >= 2
        for user in specialists:
            assert user.role == "Specialist"

    def test_list_users_filter_by_search(self, mock_db_path):
        """Test listing users with search filter."""
        # Search by name
        users = queries.list_users(search="Mohammad")
        assert len(users) >= 1

        # Search by email
        users = queries.list_users(search="@ctrlmarket.com")
        assert len(users) >= 3  # admin + specialists

    def test_list_customers(self, mock_db_path):
        """Test listing customers specifically."""
        customers = queries.list_customers()
        assert len(customers) >= 3
        for customer in customers:
            assert customer.role == "Customer"

    def test_list_specialists(self, mock_db_path):
        """Test listing specialists specifically."""
        specialists = queries.list_specialists()
        assert len(specialists) >= 2
        for specialist in specialists:
            assert specialist.role == "Specialist"

    def test_update_user_all_fields(self, mock_db_path, hash_password):
        """Test updating all user fields."""
        password_hash = hash_password("password123")
        user = UserCreate(
            name="Update Test",
            email="update_test@example.com",
            phone="09123456789",
            role="Customer",
            password="password123",
        )
        created = queries.create_user(user, password_hash)

        update = UserUpdate(
            name="Updated Name",
            email="updated@example.com",
            phone="09987654321",
            role="Specialist",
        )
        updated = queries.update_user(created.user_id, update)

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.email == "updated@example.com"
        assert updated.phone == "09987654321"
        assert updated.role == "Specialist"

    def test_update_user_partial(self, mock_db_path, hash_password):
        """Test updating only some user fields."""
        password_hash = hash_password("password123")
        user = UserCreate(
            name="Partial Update",
            email="partial@example.com",
            phone="09123456789",
            role="Customer",
            password="password123",
        )
        created = queries.create_user(user, password_hash)

        update = UserUpdate(name="Only Name Updated")
        updated = queries.update_user(created.user_id, update)

        assert updated is not None
        assert updated.name == "Only Name Updated"
        assert updated.email == "partial@example.com"  # Unchanged

    def test_update_user_nonexistent(self, mock_db_path):
        """Test updating non-existent user."""
        update = UserUpdate(name="New Name")
        result = queries.update_user(99999, update)
        assert result is None

    def test_update_user_no_changes(self, mock_db_path, hash_password):
        """Test updating user with no changes."""
        password_hash = hash_password("password123")
        user = UserCreate(
            name="No Change",
            email="nochange@example.com",
            phone="09123456789",
            role="Customer",
            password="password123",
        )
        created = queries.create_user(user, password_hash)

        update = UserUpdate()  # No fields set
        updated = queries.update_user(created.user_id, update)

        assert updated is not None
        assert updated.name == "No Change"

    def test_delete_user_existing(self, mock_db_path, hash_password):
        """Test deleting existing user."""
        password_hash = hash_password("password123")
        user = UserCreate(
            name="Delete Test",
            email="delete_test@example.com",
            phone="09123456789",
            role="Customer",
            password="password123",
        )
        created = queries.create_user(user, password_hash)

        result = queries.delete_user(created.user_id)
        assert result is True

        # Verify user is gone
        retrieved = queries.get_user_by_id(created.user_id)
        assert retrieved is None

    def test_delete_user_nonexistent(self, mock_db_path):
        """Test deleting non-existent user."""
        result = queries.delete_user(99999)
        assert result is False


class TestProductQueries:
    """Test product CRUD operations."""

    def test_create_product(self, mock_db_path):
        """Test creating a new product."""
        product = ProductCreate(
            name="New Product",
            category="Electronics",
            price=199.99,
        )
        created = queries.create_product(product)

        assert created.product_id is not None
        assert created.name == "New Product"
        assert created.category == "Electronics"
        assert created.price == 199.99

    def test_get_product_by_id_existing(self, mock_db_path):
        """Test getting product by ID."""
        product = ProductCreate(
            name="Get Product",
            category="Test",
            price=99.99,
        )
        created = queries.create_product(product)

        retrieved = queries.get_product_by_id(created.product_id)
        assert retrieved is not None
        assert retrieved.product_id == created.product_id
        assert retrieved.name == "Get Product"

    def test_get_product_by_id_nonexistent(self, mock_db_path):
        """Test getting non-existent product."""
        product = queries.get_product_by_id(99999)
        assert product is None

    def test_list_products_all(self, mock_db_path):
        """Test listing all products."""
        products = queries.list_products()
        # Should have seed data products
        assert len(products) >= 8

    def test_list_products_filter_by_category(self, mock_db_path):
        """Test listing products filtered by category."""
        products = queries.list_products(category="Security")
        assert len(products) >= 2
        for product in products:
            assert product.category == "Security"

    def test_list_products_filter_by_search(self, mock_db_path):
        """Test listing products with search filter."""
        products = queries.list_products(search="Smart")
        assert len(products) >= 3

    def test_list_product_categories(self, mock_db_path):
        """Test listing all product categories."""
        categories = queries.list_product_categories()
        assert len(categories) >= 6
        assert "Security" in categories
        assert "Climate Control" in categories

    def test_update_product_all_fields(self, mock_db_path):
        """Test updating all product fields."""
        product = ProductCreate(
            name="Update Product",
            category="Old",
            price=50.0,
        )
        created = queries.create_product(product)

        update = ProductUpdate(
            name="Updated Product",
            category="New",
            price=75.0,
        )
        updated = queries.update_product(created.product_id, update)

        assert updated is not None
        assert updated.name == "Updated Product"
        assert updated.category == "New"
        assert updated.price == 75.0

    def test_update_product_partial(self, mock_db_path):
        """Test updating only some product fields."""
        product = ProductCreate(
            name="Partial Product",
            category="Test",
            price=100.0,
        )
        created = queries.create_product(product)

        update = ProductUpdate(price=150.0)
        updated = queries.update_product(created.product_id, update)

        assert updated is not None
        assert updated.price == 150.0
        assert updated.name == "Partial Product"  # Unchanged

    def test_update_product_nonexistent(self, mock_db_path):
        """Test updating non-existent product."""
        update = ProductUpdate(name="New Name")
        result = queries.update_product(99999, update)
        assert result is None

    def test_delete_product_existing(self, mock_db_path):
        """Test deleting existing product."""
        product = ProductCreate(
            name="Delete Product",
            category="Test",
            price=25.0,
        )
        created = queries.create_product(product)

        result = queries.delete_product(created.product_id)
        assert result is True

        # Verify product is gone
        retrieved = queries.get_product_by_id(created.product_id)
        assert retrieved is None

    def test_delete_product_nonexistent(self, mock_db_path):
        """Test deleting non-existent product."""
        result = queries.delete_product(99999)
        assert result is False


class TestOrderQueries:
    """Test order CRUD operations."""

    def test_create_order(self, mock_db_path):
        """Test creating a new order."""
        # Get existing customer and products
        users = queries.list_customers()
        user_id = users[0].user_id

        products = queries.list_products()
        product_id_1 = products[0].product_id
        product_id_2 = products[1].product_id

        order_data = OrderCreate(
            user_id=user_id,
            items=[
                OrderItemCreate(product_id=product_id_1, quantity=2),
                OrderItemCreate(product_id=product_id_2, quantity=1),
            ],
        )
        created = queries.create_order(order_data)

        assert created.order_id is not None
        assert created.user_id == user_id
        assert created.status == "Pending"
        assert len(created.items) == 2
        assert created.total_price > 0

    def test_create_order_invalid_product(self, mock_db_path):
        """Test creating order with invalid product."""
        users = queries.list_customers()
        user_id = users[0].user_id

        order_data = OrderCreate(
            user_id=user_id,
            items=[
                OrderItemCreate(product_id=99999, quantity=1),  # Non-existent product
            ],
        )

        with pytest.raises(ValueError, match="Product 99999 not found"):
            queries.create_order(order_data)

    def test_get_order_by_id_existing(self, mock_db_path):
        """Test getting order by ID."""
        # Get existing order from seed data
        orders = queries.list_orders()
        assert len(orders) > 0
        order_id = orders[0].order_id

        retrieved = queries.get_order_by_id(order_id)
        assert retrieved is not None
        assert retrieved.order_id == order_id
        assert retrieved.items is not None

    def test_get_order_by_id_nonexistent(self, mock_db_path):
        """Test getting non-existent order."""
        order = queries.get_order_by_id(99999)
        assert order is None

    def test_list_orders_all(self, mock_db_path):
        """Test listing all orders."""
        orders = queries.list_orders()
        # Should have seed data orders
        assert len(orders) >= 3

    def test_list_orders_filter_by_user(self, mock_db_path):
        """Test listing orders filtered by user."""
        users = queries.list_customers()
        user_id = users[0].user_id

        orders = queries.list_orders(user_id=user_id)
        for order in orders:
            assert order.user_id == user_id

    def test_list_orders_filter_by_status(self, mock_db_path):
        """Test listing orders filtered by status."""
        pending_orders = queries.list_orders(status="Pending")
        for order in pending_orders:
            assert order.status == "Pending"

        completed_orders = queries.list_orders(status="Completed")
        for order in completed_orders:
            assert order.status == "Completed"

    def test_list_orders_filter_by_search(self, mock_db_path):
        """Test listing orders with search filter."""
        orders = queries.list_orders(search="Mohammad")
        assert len(orders) >= 1

    def test_update_order_status(self, mock_db_path):
        """Test updating order status."""
        # Get a pending order
        orders = queries.list_orders(status="Pending")
        assert len(orders) > 0
        order_id = orders[0].order_id

        update = OrderUpdateStatus(status="Completed")
        updated = queries.update_order_status(order_id, update)

        assert updated is not None
        assert updated.status == "Completed"

    def test_update_order_status_nonexistent(self, mock_db_path):
        """Test updating status of non-existent order."""
        update = OrderUpdateStatus(status="Completed")
        result = queries.update_order_status(99999, update)
        assert result is None

    def test_cancel_order_pending(self, mock_db_path):
        """Test cancelling a pending order."""
        # Create a new order
        users = queries.list_customers()
        products = queries.list_products()

        order_data = OrderCreate(
            user_id=users[0].user_id,
            items=[
                OrderItemCreate(product_id=products[0].product_id, quantity=1),
            ],
        )
        created = queries.create_order(order_data)

        # Cancel it
        result = queries.cancel_order(created.order_id)
        assert result is True

        # Verify status changed
        cancelled = queries.get_order_by_id(created.order_id)
        assert cancelled.status == "Cancelled"

    def test_cancel_order_non_pending(self, mock_db_path):
        """Test cancelling a non-pending order fails."""
        # Get a completed order
        orders = queries.list_orders(status="Completed")
        if len(orders) > 0:
            order_id = orders[0].order_id
            result = queries.cancel_order(order_id)
            assert result is False


class TestServiceRequestQueries:
    """Test service request CRUD operations."""

    def test_create_service_request(self, mock_db_path):
        """Test creating a new service request."""
        users = queries.list_customers()
        customer_id = users[0].user_id

        request_data = ServiceRequestCreate(
            service_type="Installation",
            customer_id=customer_id,
        )
        created = queries.create_service_request(request_data)

        assert created.request_id is not None
        assert created.service_type == "Installation"
        assert created.status == "Pending"
        assert created.customer_id == customer_id
        assert created.specialist_id is None

    def test_get_service_request_by_id_existing(self, mock_db_path):
        """Test getting service request by ID."""
        # Get existing request from seed data
        requests = queries.list_service_requests()
        assert len(requests) > 0
        request_id = requests[0].request_id

        retrieved = queries.get_service_request_by_id(request_id)
        assert retrieved is not None
        assert retrieved.request_id == request_id
        assert retrieved.customer_name is not None

    def test_get_service_request_by_id_nonexistent(self, mock_db_path):
        """Test getting non-existent service request."""
        request = queries.get_service_request_by_id(99999)
        assert request is None

    def test_list_service_requests_all(self, mock_db_path):
        """Test listing all service requests."""
        requests = queries.list_service_requests()
        # Should have seed data requests
        assert len(requests) >= 4

    def test_list_service_requests_filter_by_status(self, mock_db_path):
        """Test listing service requests filtered by status."""
        pending = queries.list_service_requests(status="Pending")
        for req in pending:
            assert req.status == "Pending"

        in_progress = queries.list_service_requests(status="In Progress")
        for req in in_progress:
            assert req.status == "In Progress"

    def test_list_service_requests_filter_by_customer(self, mock_db_path):
        """Test listing service requests filtered by customer."""
        users = queries.list_customers()
        customer_id = users[0].user_id

        requests = queries.list_service_requests(customer_id=customer_id)
        for req in requests:
            assert req.customer_id == customer_id

    def test_list_service_requests_filter_by_specialist(self, mock_db_path):
        """Test listing service requests filtered by specialist."""
        specialists = queries.list_specialists()
        specialist_id = specialists[0].user_id

        requests = queries.list_service_requests(specialist_id=specialist_id)
        for req in requests:
            assert req.specialist_id == specialist_id

    def test_list_service_requests_filter_unassigned(self, mock_db_path):
        """Test listing unassigned service requests."""
        requests = queries.list_service_requests(specialist_id=0)
        for req in requests:
            assert req.specialist_id is None

    def test_list_service_requests_filter_by_search(self, mock_db_path):
        """Test listing service requests with search filter."""
        requests = queries.list_service_requests(search="Installation")
        for req in requests:
            assert "Installation" in req.service_type

    def test_update_service_request_status(self, mock_db_path):
        """Test updating service request status."""
        # Get a pending request
        requests = queries.list_service_requests(status="Pending")
        assert len(requests) > 0
        request_id = requests[0].request_id

        update = ServiceRequestUpdateStatus(status="In Progress")
        updated = queries.update_service_request_status(request_id, update)

        assert updated is not None
        assert updated.status == "In Progress"

    def test_update_service_request_status_nonexistent(self, mock_db_path):
        """Test updating status of non-existent request."""
        update = ServiceRequestUpdateStatus(status="Completed")
        result = queries.update_service_request_status(99999, update)
        assert result is None

    def test_assign_specialist(self, mock_db_path):
        """Test assigning a specialist to a request."""
        # Create a new unassigned request
        users = queries.list_customers()
        specialists = queries.list_specialists()

        request_data = ServiceRequestCreate(
            service_type="Support",
            customer_id=users[0].user_id,
        )
        created = queries.create_service_request(request_data)

        # Assign specialist
        assigned = queries.assign_specialist(created.request_id, specialists[0].user_id)

        assert assigned is not None
        assert assigned.specialist_id == specialists[0].user_id
        assert assigned.status == "In Progress"

    def test_assign_specialist_already_assigned(self, mock_db_path):
        """Test assigning to already assigned request fails."""
        # Get an assigned request
        requests = queries.list_service_requests()
        assigned_requests = [r for r in requests if r.specialist_id is not None]

        if len(assigned_requests) > 0:
            request_id = assigned_requests[0].request_id
            specialists = queries.list_specialists()

            result = queries.assign_specialist(request_id, specialists[0].user_id)
            assert result is None

    def test_delete_service_request_existing(self, mock_db_path):
        """Test deleting existing service request."""
        # Create a new request
        users = queries.list_customers()
        request_data = ServiceRequestCreate(
            service_type="Installation",
            customer_id=users[0].user_id,
        )
        created = queries.create_service_request(request_data)

        # Delete it
        result = queries.delete_service_request(created.request_id)
        assert result is True

        # Verify it's gone
        retrieved = queries.get_service_request_by_id(created.request_id)
        assert retrieved is None

    def test_delete_service_request_nonexistent(self, mock_db_path):
        """Test deleting non-existent service request."""
        result = queries.delete_service_request(99999)
        assert result is False

    def test_list_service_requests_for_specialist(self, mock_db_path):
        """Test listing requests available to a specialist."""
        specialists = queries.list_specialists()
        specialist_id = specialists[0].user_id

        requests = queries.list_service_requests_for_specialist(specialist_id)

        # Should include unassigned and assigned to this specialist
        for req in requests:
            assert req.specialist_id is None or req.specialist_id == specialist_id
