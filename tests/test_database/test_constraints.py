"""Database constraint tests - foreign keys, check constraints, etc."""

import sqlite3

import pytest

from database.connection import get_db_connection


class TestForeignKeyConstraints:
    """Test foreign key constraint enforcement."""

    def test_order_cascade_delete_on_user_delete(self, mock_db_path):
        """Test that orders are deleted when user is deleted (CASCADE)."""
        with get_db_connection() as conn:
            # Create a customer
            conn.execute(
                "INSERT INTO User (name, email, phone, role, password_hash) VALUES (?, ?, ?, ?, ?)",
                (
                    "Temp Customer",
                    "temp_cust@example.com",
                    "09123456789",
                    "Customer",
                    "hash",
                ),
            )
            cursor = conn.execute(
                "SELECT user_id FROM User WHERE email = ?", ("temp_cust@example.com",)
            )
            user_id = cursor.fetchone()["user_id"]

            # Create an order for this customer
            conn.execute(
                'INSERT INTO "Order" (total_price, status, user_id) VALUES (?, ?, ?)',
                (100.0, "Pending", user_id),
            )
            cursor = conn.execute(
                'SELECT order_id FROM "Order" WHERE user_id = ?', (user_id,)
            )
            order_id = cursor.fetchone()["order_id"]

            # Delete the user
            conn.execute("DELETE FROM User WHERE user_id = ?", (user_id,))

            # Verify order was also deleted
            cursor = conn.execute(
                'SELECT * FROM "Order" WHERE order_id = ?', (order_id,)
            )
            assert cursor.fetchone() is None

    def test_order_item_cascade_delete_on_order_delete(self, mock_db_path):
        """Test that order items are deleted when order is deleted (CASCADE)."""
        with get_db_connection() as conn:
            # Get existing customer
            cursor = conn.execute(
                "SELECT user_id FROM User WHERE role = 'Customer' LIMIT 1"
            )
            user_id = cursor.fetchone()["user_id"]

            # Get existing product
            cursor = conn.execute("SELECT product_id FROM Product LIMIT 1")
            product_id = cursor.fetchone()["product_id"]

            # Create an order
            conn.execute(
                'INSERT INTO "Order" (total_price, status, user_id) VALUES (?, ?, ?)',
                (100.0, "Pending", user_id),
            )
            cursor = conn.execute(
                'SELECT order_id FROM "Order" WHERE user_id = ?', (user_id,)
            )
            order_id = cursor.fetchone()["order_id"]

            # Create an order item
            conn.execute(
                "INSERT INTO OrderItem (quantity, unit_price, order_id, product_id) VALUES (?, ?, ?, ?)",
                (1, 50.0, order_id, product_id),
            )
            cursor = conn.execute(
                "SELECT order_item_id FROM OrderItem WHERE order_id = ?", (order_id,)
            )
            order_item_id = cursor.fetchone()["order_item_id"]

            # Delete the order
            conn.execute('DELETE FROM "Order" WHERE order_id = ?', (order_id,))

            # Verify order item was also deleted
            cursor = conn.execute(
                "SELECT * FROM OrderItem WHERE order_item_id = ?", (order_item_id,)
            )
            assert cursor.fetchone() is None

    def test_product_delete_restricted_when_in_order(self, mock_db_path):
        """Test that product cannot be deleted when referenced in order (RESTRICT)."""
        with get_db_connection() as conn:
            # Get existing customer
            cursor = conn.execute(
                "SELECT user_id FROM User WHERE role = 'Customer' LIMIT 1"
            )
            user_id = cursor.fetchone()["user_id"]

            # Create a product
            conn.execute(
                "INSERT INTO Product (name, category, price) VALUES (?, ?, ?)",
                ("Temp Product", "Test", 99.99),
            )
            cursor = conn.execute(
                "SELECT product_id FROM Product WHERE name = ?", ("Temp Product",)
            )
            product_id = cursor.fetchone()["product_id"]

            # Create an order with this product
            conn.execute(
                'INSERT INTO "Order" (total_price, status, user_id) VALUES (?, ?, ?)',
                (99.99, "Pending", user_id),
            )
            cursor = conn.execute(
                'SELECT order_id FROM "Order" WHERE user_id = ? ORDER BY order_id DESC LIMIT 1',
                (user_id,),
            )
            order_id = cursor.fetchone()["order_id"]

            conn.execute(
                "INSERT INTO OrderItem (quantity, unit_price, order_id, product_id) VALUES (?, ?, ?, ?)",
                (1, 99.99, order_id, product_id),
            )

            # Try to delete the product - should fail
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute("DELETE FROM Product WHERE product_id = ?", (product_id,))

    def test_order_fk_requires_valid_user(self, mock_db_path):
        """Test that orders require a valid user_id."""
        with get_db_connection() as conn:
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    'INSERT INTO "Order" (total_price, status, user_id) VALUES (?, ?, ?)',
                    (100.0, "Pending", 99999),  # Non-existent user
                )

    def test_order_item_fk_requires_valid_order(self, mock_db_path):
        """Test that order items require a valid order_id."""
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT product_id FROM Product LIMIT 1")
            product_id = cursor.fetchone()["product_id"]

            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO OrderItem (quantity, unit_price, order_id, product_id) VALUES (?, ?, ?, ?)",
                    (1, 50.0, 99999, product_id),  # Non-existent order
                )

    def test_order_item_fk_requires_valid_product(self, mock_db_path):
        """Test that order items require a valid product_id."""
        with get_db_connection() as conn:
            cursor = conn.execute('SELECT order_id FROM "Order" LIMIT 1')
            order_id = cursor.fetchone()["order_id"]

            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO OrderItem (quantity, unit_price, order_id, product_id) VALUES (?, ?, ?, ?)",
                    (1, 50.0, order_id, 99999),  # Non-existent product
                )

    def test_service_request_fk_requires_valid_customer(self, mock_db_path):
        """Test that service requests require a valid customer_id."""
        with get_db_connection() as conn:
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO ServiceRequest (service_type, status, customer_id) VALUES (?, ?, ?)",
                    ("Installation", "Pending", 99999),  # Non-existent customer
                )

    def test_service_request_fk_requires_valid_specialist(self, mock_db_path):
        """Test that service requests require a valid specialist_id if set."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT user_id FROM User WHERE role = 'Customer' LIMIT 1"
            )
            customer_id = cursor.fetchone()["user_id"]

            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO ServiceRequest (service_type, status, customer_id, specialist_id) VALUES (?, ?, ?, ?)",
                    (
                        "Installation",
                        "Pending",
                        customer_id,
                        99999,
                    ),  # Non-existent specialist
                )


class TestCheckConstraints:
    """Test CHECK constraint enforcement."""

    def test_user_role_must_be_valid(self, mock_db_path):
        """Test that user role must be Customer, Specialist, or Admin."""
        with get_db_connection() as conn:
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO User (name, email, phone, role, password_hash) VALUES (?, ?, ?, ?, ?)",
                    ("Test", "test@example.com", "09123456789", "InvalidRole", "hash"),
                )

    def test_product_price_must_be_non_negative(self, mock_db_path):
        """Test that product price must be >= 0."""
        with get_db_connection() as conn:
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO Product (name, category, price) VALUES (?, ?, ?)",
                    ("Test", "Category", -10.0),
                )

    def test_order_status_must_be_valid(self, mock_db_path):
        """Test that order status must be Pending, Completed, or Cancelled."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT user_id FROM User WHERE role = 'Customer' LIMIT 1"
            )
            user_id = cursor.fetchone()["user_id"]

            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    'INSERT INTO "Order" (total_price, status, user_id) VALUES (?, ?, ?)',
                    (100.0, "InvalidStatus", user_id),
                )

    def test_order_total_price_must_be_non_negative(self, mock_db_path):
        """Test that order total_price must be >= 0."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT user_id FROM User WHERE role = 'Customer' LIMIT 1"
            )
            user_id = cursor.fetchone()["user_id"]

            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    'INSERT INTO "Order" (total_price, status, user_id) VALUES (?, ?, ?)',
                    (-100.0, "Pending", user_id),
                )

    def test_order_item_quantity_must_be_positive(self, mock_db_path):
        """Test that order item quantity must be > 0."""
        with get_db_connection() as conn:
            cursor = conn.execute('SELECT order_id FROM "Order" LIMIT 1')
            order_id = cursor.fetchone()["order_id"]

            cursor = conn.execute("SELECT product_id FROM Product LIMIT 1")
            product_id = cursor.fetchone()["product_id"]

            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO OrderItem (quantity, unit_price, order_id, product_id) VALUES (?, ?, ?, ?)",
                    (0, 50.0, order_id, product_id),
                )

    def test_order_item_unit_price_must_be_non_negative(self, mock_db_path):
        """Test that order item unit_price must be >= 0."""
        with get_db_connection() as conn:
            cursor = conn.execute('SELECT order_id FROM "Order" LIMIT 1')
            order_id = cursor.fetchone()["order_id"]

            cursor = conn.execute("SELECT product_id FROM Product LIMIT 1")
            product_id = cursor.fetchone()["product_id"]

            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO OrderItem (quantity, unit_price, order_id, product_id) VALUES (?, ?, ?, ?)",
                    (1, -50.0, order_id, product_id),
                )

    def test_service_request_type_must_be_valid(self, mock_db_path):
        """Test that service request type must be Installation or Support."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT user_id FROM User WHERE role = 'Customer' LIMIT 1"
            )
            customer_id = cursor.fetchone()["user_id"]

            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO ServiceRequest (service_type, status, customer_id) VALUES (?, ?, ?)",
                    ("InvalidType", "Pending", customer_id),
                )

    def test_service_request_status_must_be_valid(self, mock_db_path):
        """Test that service request status must be valid enum value."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT user_id FROM User WHERE role = 'Customer' LIMIT 1"
            )
            customer_id = cursor.fetchone()["user_id"]

            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO ServiceRequest (service_type, status, customer_id) VALUES (?, ?, ?)",
                    ("Installation", "InvalidStatus", customer_id),
                )

    def test_service_request_customer_not_specialist(self, mock_db_path):
        """Test that customer_id != specialist_id in service requests."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT user_id FROM User WHERE role = 'Customer' LIMIT 1"
            )
            customer_id = cursor.fetchone()["user_id"]

            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO ServiceRequest (service_type, status, customer_id, specialist_id) VALUES (?, ?, ?, ?)",
                    ("Installation", "Pending", customer_id, customer_id),
                )


class TestUniqueConstraints:
    """Test UNIQUE constraint enforcement."""

    def test_user_email_must_be_unique(self, mock_db_path):
        """Test that user email must be unique."""
        with get_db_connection() as conn:
            # Insert first user
            conn.execute(
                "INSERT INTO User (name, email, phone, role, password_hash) VALUES (?, ?, ?, ?, ?)",
                ("User1", "unique@example.com", "09123456789", "Customer", "hash1"),
            )

            # Try to insert another user with same email
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO User (name, email, phone, role, password_hash) VALUES (?, ?, ?, ?, ?)",
                    (
                        "User2",
                        "unique@example.com",
                        "09987654321",
                        "Specialist",
                        "hash2",
                    ),
                )
