"""Database query operations - Raw SQL with parameterized queries."""

import sqlite3
from datetime import datetime
from typing import Optional

from database.connection import get_db_connection
from models import (
    LoginCredentials,
    OrderCreate,
    OrderItemWithProduct,
    OrderUpdateStatus,
    OrderWithItems,
    Product,
    ProductCreate,
    ProductUpdate,
    ServiceRequest,
    ServiceRequestCreate,
    ServiceRequestUpdateStatus,
    ServiceRequestWithDetails,
    SessionUser,
    User,
    UserCreate,
    UserUpdate,
)


# =============================================================================
# Authentication Queries
# =============================================================================
def authenticate_user(credentials: LoginCredentials) -> Optional[SessionUser]:
    """Authenticate user by email and return user data with role."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            SELECT user_id, name, email, role, password_hash
            FROM User
            WHERE email = ?
            """,
            (credentials.email,),
        )
        row = cursor.fetchone()

        if row:
            return SessionUser(
                user_id=row["user_id"],
                name=row["name"],
                email=row["email"],
                role=row["role"],
            )
        return None


def get_user_password_hash(email: str) -> Optional[str]:
    """Get password hash for email verification."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT password_hash FROM User WHERE email = ?", (email,)
        )
        row = cursor.fetchone()
        return row["password_hash"] if row else None


# =============================================================================
# User Queries
# =============================================================================
def create_user(user: UserCreate, password_hash: str) -> User:
    """Create a new user."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO User (name, email, phone, role, password_hash)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user.name, user.email, user.phone, user.role, password_hash),
        )
        user_id = cursor.lastrowid

        return User(
            user_id=user_id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            role=user.role,
            password_hash=password_hash,
        )


def get_user_by_id(
    user_id: int, conn: Optional[sqlite3.Connection] = None
) -> Optional[User]:
    """Get user by ID."""
    if conn is None:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT * FROM User WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return User(**dict(row)) if row else None
    else:
        cursor = conn.execute("SELECT * FROM User WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return User(**dict(row)) if row else None


def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM User WHERE email = ?", (email,))
        row = cursor.fetchone()
        return User(**dict(row)) if row else None


def list_users(role: Optional[str] = None, search: Optional[str] = None) -> list[User]:
    """List all users with optional filtering."""
    with get_db_connection() as conn:
        query = "SELECT * FROM User WHERE 1=1"
        params = []

        if role:
            query += " AND role = ?"
            params.append(role)

        if search:
            query += " AND (name LIKE ? OR email LIKE ? OR phone LIKE ?)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        query += " ORDER BY name"

        cursor = conn.execute(query, params)
        return [User(**dict(row)) for row in cursor.fetchall()]


def update_user(user_id: int, user: UserUpdate) -> Optional[User]:
    """Update user data."""
    with get_db_connection() as conn:
        # Build dynamic update query
        fields = []
        params = []

        if user.name is not None:
            fields.append("name = ?")
            params.append(user.name)
        if user.email is not None:
            fields.append("email = ?")
            params.append(user.email)
        if user.phone is not None:
            fields.append("phone = ?")
            params.append(user.phone)
        if user.role is not None:
            fields.append("role = ?")
            params.append(user.role)
        if user.password is not None:
            # Note: password should be hashed before calling this
            fields.append("password_hash = ?")
            params.append(user.password)

        if not fields:
            return get_user_by_id(user_id, conn)

        query = f"UPDATE User SET {', '.join(fields)} WHERE user_id = ?"
        params.append(user_id)

        cursor = conn.execute(query, params)
        if cursor.rowcount == 0:
            return None

        return get_user_by_id(user_id, conn)


def delete_user(user_id: int) -> bool:
    """Delete user by ID."""
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM User WHERE user_id = ?", (user_id,))
        return cursor.rowcount > 0


def list_customers(search: Optional[str] = None) -> list[User]:
    """List all customers."""
    return list_users(role="Customer", search=search)


def list_specialists(search: Optional[str] = None) -> list[User]:
    """List all specialists."""
    return list_users(role="Specialist", search=search)


# =============================================================================
# Product Queries
# =============================================================================
def create_product(product: ProductCreate) -> Product:
    """Create a new product."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO Product (name, category, price)
            VALUES (?, ?, ?)
            """,
            (product.name, product.category, product.price),
        )
        product_id = cursor.lastrowid

        return Product(
            product_id=product_id,
            name=product.name,
            category=product.category,
            price=product.price,
        )


def get_product_by_id(
    product_id: int, conn: Optional[sqlite3.Connection] = None
) -> Optional[Product]:
    """Get product by ID."""

    def _fetch_product(connection: sqlite3.Connection) -> Optional[Product]:
        cursor = connection.execute(
            "SELECT * FROM Product WHERE product_id = ?", (product_id,)
        )
        row = cursor.fetchone()
        return Product(**dict(row)) if row else None

    if conn is None:
        with get_db_connection() as conn:
            return _fetch_product(conn)
    else:
        return _fetch_product(conn)


def list_products(
    category: Optional[str] = None, search: Optional[str] = None
) -> list[Product]:
    """List all products with optional filtering."""
    with get_db_connection() as conn:
        query = "SELECT * FROM Product WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if search:
            query += " AND (name LIKE ? OR category LIKE ?)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern])

        query += " ORDER BY name"

        cursor = conn.execute(query, params)
        return [Product(**dict(row)) for row in cursor.fetchall()]


def list_product_categories() -> list[str]:
    """List all unique product categories."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT DISTINCT category FROM Product ORDER BY category")
        return [row["category"] for row in cursor.fetchall()]


def update_product(product_id: int, product: ProductUpdate) -> Optional[Product]:
    """Update product data."""
    with get_db_connection() as conn:
        fields = []
        params = []

        if product.name is not None:
            fields.append("name = ?")
            params.append(product.name)
        if product.category is not None:
            fields.append("category = ?")
            params.append(product.category)
        if product.price is not None:
            fields.append("price = ?")
            params.append(product.price)

        if not fields:
            return get_product_by_id(product_id, conn)

        query = f"UPDATE Product SET {', '.join(fields)} WHERE product_id = ?"
        params.append(product_id)

        cursor = conn.execute(query, params)
        if cursor.rowcount == 0:
            return None

        return get_product_by_id(product_id, conn)


def delete_product(product_id: int) -> bool:
    """Delete product by ID."""
    with get_db_connection() as conn:
        try:
            cursor = conn.execute(
                "DELETE FROM Product WHERE product_id = ?", (product_id,)
            )
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            # Product is referenced in OrderItem (ON DELETE RESTRICT)
            return False


# =============================================================================
# Order Queries
# =============================================================================
def create_order(order_data: OrderCreate) -> Optional[OrderWithItems]:
    """Create a new order with multiple items."""
    with get_db_connection() as conn:
        # Calculate total price from items
        total_price = 0.0
        order_items_data = []

        for item in order_data.items:
            product = get_product_by_id(item.product_id, conn)
            if not product:
                raise ValueError(f"Product {item.product_id} not found")

            unit_price = product.price
            total_price += unit_price * item.quantity
            order_items_data.append(
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": unit_price,
                }
            )

        # Insert order with Pending status
        cursor = conn.execute(
            """
            INSERT INTO "Order" (order_date, total_price, status, user_id)
            VALUES (CURRENT_TIMESTAMP, ?, 'Pending', ?)
            """,
            (total_price, order_data.user_id),
        )
        order_id = cursor.lastrowid

        if order_id is None:
            return None

        # Insert order items
        for item_data in order_items_data:
            conn.execute(
                """
                INSERT INTO OrderItem (quantity, unit_price, order_id, product_id)
                VALUES (?, ?, ?, ?)
                """,
                (
                    item_data["quantity"],
                    item_data["unit_price"],
                    order_id,
                    item_data["product_id"],
                ),
            )

        return get_order_by_id(order_id, conn)


def get_order_by_id(
    order_id: int, conn: Optional[sqlite3.Connection] = None
) -> Optional[OrderWithItems]:
    """Get order by ID with items."""

    def _fetch_order(connection: sqlite3.Connection) -> Optional[OrderWithItems]:
        # Get order details
        cursor = connection.execute(
            """
            SELECT o.*, u.name as customer_name
            FROM "Order" o
            JOIN User u ON o.user_id = u.user_id
            WHERE o.order_id = ?
            """,
            (order_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        # Get order items with product details
        items_cursor = connection.execute(
            """
            SELECT oi.*, p.name as product_name, p.category as product_category
            FROM OrderItem oi
            JOIN Product p ON oi.product_id = p.product_id
            WHERE oi.order_id = ?
            """,
            (order_id,),
        )
        items = [
            OrderItemWithProduct(
                order_item_id=item["order_item_id"],
                order_id=item["order_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                product_id=item["product_id"],
                product_name=item["product_name"],
                product_category=item["product_category"],
            )
            for item in items_cursor.fetchall()
        ]

        return OrderWithItems(
            order_id=row["order_id"],
            order_date=row["order_date"],
            total_price=row["total_price"],
            status=row["status"],
            user_id=row["user_id"],
            customer_name=row["customer_name"],
            items=items,
        )

    if conn is None:
        with get_db_connection() as conn:
            return _fetch_order(conn)
    else:
        return _fetch_order(conn)


def list_orders(
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> list[OrderWithItems]:
    """List all orders with optional filtering."""
    with get_db_connection() as conn:
        query = """
            SELECT o.*, u.name as customer_name
            FROM "Order" o
            JOIN User u ON o.user_id = u.user_id
            WHERE 1=1
        """
        params = []

        if user_id:
            query += " AND o.user_id = ?"
            params.append(user_id)

        if status:
            query += " AND o.status = ?"
            params.append(status)

        if search:
            query += " AND (u.name LIKE ? OR o.order_id LIKE ?)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern])

        query += " ORDER BY o.order_date DESC"

        cursor = conn.execute(query, params)
        orders = []

        for row in cursor.fetchall():
            # Get items for each order
            items_cursor = conn.execute(
                """
                SELECT oi.*, p.name as product_name, p.category as product_category
                FROM OrderItem oi
                JOIN Product p ON oi.product_id = p.product_id
                WHERE oi.order_id = ?
                """,
                (row["order_id"],),
            )
            items = [
                OrderItemWithProduct(
                    order_item_id=item["order_item_id"],
                    order_id=item["order_id"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    product_id=item["product_id"],
                    product_name=item["product_name"],
                    product_category=item["product_category"],
                )
                for item in items_cursor.fetchall()
            ]

            orders.append(
                OrderWithItems(
                    order_id=row["order_id"],
                    order_date=row["order_date"],
                    total_price=row["total_price"],
                    status=row["status"],
                    user_id=row["user_id"],
                    customer_name=row["customer_name"],
                    items=items,
                )
            )

        return orders


def update_order_status(
    order_id: int, update: OrderUpdateStatus
) -> Optional[OrderWithItems]:
    """Update order status."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            'UPDATE "Order" SET status = ? WHERE order_id = ?',
            (update.status, order_id),
        )
        if cursor.rowcount == 0:
            return None

        return get_order_by_id(order_id, conn)


def cancel_order(order_id: int) -> bool:
    """Cancel order by setting status to 'Cancelled'."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            'UPDATE "Order" SET status = ? WHERE order_id = ? AND status = ?',
            ("Cancelled", order_id, "Pending"),
        )
        return cursor.rowcount > 0


# =============================================================================
# Service Request Queries
# =============================================================================
def create_service_request(request: ServiceRequestCreate) -> ServiceRequest:
    """Create a new service request."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO ServiceRequest (service_type, request_date, status, customer_id, specialist_id)
            VALUES (?, CURRENT_TIMESTAMP, 'Pending', ?, NULL)
            """,
            (request.service_type, request.customer_id),
        )
        request_id = cursor.lastrowid

        return ServiceRequest(
            request_id=request_id,
            service_type=request.service_type,
            request_date=datetime.now(),
            status="Pending",
            customer_id=request.customer_id,
            specialist_id=None,
        )


def get_service_request_by_id(
    request_id: int, conn: Optional[sqlite3.Connection] = None
) -> Optional[ServiceRequestWithDetails]:
    """Get service request by ID with details."""

    def _fetch_request(
        connection: sqlite3.Connection,
    ) -> Optional[ServiceRequestWithDetails]:
        cursor = connection.execute(
            """
            SELECT 
                sr.*,
                c.name as customer_name,
                s.name as specialist_name
            FROM ServiceRequest sr
            JOIN User c ON sr.customer_id = c.user_id
            LEFT JOIN User s ON sr.specialist_id = s.user_id
            WHERE sr.request_id = ?
            """,
            (request_id,),
        )
        row = cursor.fetchone()

        if not row:
            return None

        return ServiceRequestWithDetails(
            request_id=row["request_id"],
            service_type=row["service_type"],
            request_date=row["request_date"],
            status=row["status"],
            customer_id=row["customer_id"],
            specialist_id=row["specialist_id"],
            customer_name=row["customer_name"],
            specialist_name=row["specialist_name"],
        )

    if conn is None:
        with get_db_connection() as conn:
            return _fetch_request(conn)
    else:
        return _fetch_request(conn)


def list_service_requests(
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    specialist_id: Optional[int] = None,
    search: Optional[str] = None,
) -> list[ServiceRequestWithDetails]:
    """List all service requests with optional filtering."""
    with get_db_connection() as conn:
        query = """
            SELECT 
                sr.*,
                c.name as customer_name,
                s.name as specialist_name
            FROM ServiceRequest sr
            JOIN User c ON sr.customer_id = c.user_id
            LEFT JOIN User s ON sr.specialist_id = s.user_id
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND sr.status = ?"
            params.append(status)

        if customer_id:
            query += " AND sr.customer_id = ?"
            params.append(customer_id)

        if specialist_id is not None:
            if specialist_id == 0:  # Filter for unassigned
                query += " AND sr.specialist_id IS NULL"
            else:
                query += " AND sr.specialist_id = ?"
                params.append(specialist_id)

        if search:
            query += " AND (c.name LIKE ? OR sr.service_type LIKE ?)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern])

        query += " ORDER BY sr.request_date DESC"

        cursor = conn.execute(query, params)

        return [
            ServiceRequestWithDetails(
                request_id=row["request_id"],
                service_type=row["service_type"],
                request_date=row["request_date"],
                status=row["status"],
                customer_id=row["customer_id"],
                specialist_id=row["specialist_id"],
                customer_name=row["customer_name"],
                specialist_name=row["specialist_name"],
            )
            for row in cursor.fetchall()
        ]


def update_service_request_status(
    request_id: int, update: ServiceRequestUpdateStatus
) -> Optional[ServiceRequestWithDetails]:
    """Update service request status."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "UPDATE ServiceRequest SET status = ? WHERE request_id = ?",
            (update.status, request_id),
        )
        if cursor.rowcount == 0:
            return None

        return get_service_request_by_id(request_id, conn)


def assign_specialist(
    request_id: int, specialist_id: int
) -> Optional[ServiceRequestWithDetails]:
    """Assign a specialist to a service request."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE ServiceRequest 
            SET specialist_id = ?, status = 'In Progress'
            WHERE request_id = ? AND specialist_id IS NULL
            """,
            (specialist_id, request_id),
        )
        if cursor.rowcount == 0:
            return None

        return get_service_request_by_id(request_id, conn)


def delete_service_request(request_id: int) -> bool:
    """Delete service request by ID."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM ServiceRequest WHERE request_id = ?", (request_id,)
        )
        return cursor.rowcount > 0


def list_service_requests_for_specialist(
    specialist_id: int,
) -> list[ServiceRequestWithDetails]:
    """List service requests for a specialist (unassigned or assigned to them)."""
    with get_db_connection() as conn:
        query = """
            SELECT 
                sr.*,
                c.name as customer_name,
                s.name as specialist_name
            FROM ServiceRequest sr
            JOIN User c ON sr.customer_id = c.user_id
            LEFT JOIN User s ON sr.specialist_id = s.user_id
            WHERE sr.specialist_id IS NULL OR sr.specialist_id = ?
            ORDER BY sr.request_date DESC
        """
        cursor = conn.execute(query, (specialist_id,))

        return [
            ServiceRequestWithDetails(
                request_id=row["request_id"],
                service_type=row["service_type"],
                request_date=row["request_date"],
                status=row["status"],
                customer_id=row["customer_id"],
                specialist_id=row["specialist_id"],
                customer_name=row["customer_name"],
                specialist_name=row["specialist_name"],
            )
            for row in cursor.fetchall()
        ]
