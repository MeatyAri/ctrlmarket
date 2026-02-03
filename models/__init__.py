"""Models module - Pydantic models for all entities."""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    """Base user model with common fields."""

    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=1, max_length=20)
    role: Literal["Customer", "Specialist", "Admin"]


class User(UserBase):
    """Complete user model with ID and password."""

    user_id: Optional[int] = None
    password_hash: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    """User model for creation (includes plain password)."""

    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """User model for updates (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=1, max_length=20)
    role: Optional[Literal["Customer", "Specialist", "Admin"]] = None
    password: Optional[str] = Field(None, min_length=6)


class LoginCredentials(BaseModel):
    """Login credentials model."""

    email: str
    password: str


class ProductBase(BaseModel):
    """Base product model."""

    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., ge=0)


class Product(ProductBase):
    """Complete product model with ID."""

    product_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(ProductBase):
    """Product model for creation."""

    pass


class ProductUpdate(BaseModel):
    """Product model for updates (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[float] = Field(None, ge=0)


class OrderItemBase(BaseModel):
    """Base order item model."""

    quantity: int = Field(..., ge=1)
    unit_price: float = Field(..., ge=0)
    product_id: int


class OrderItem(OrderItemBase):
    """Complete order item model with IDs."""

    order_item_id: Optional[int] = None
    order_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class OrderItemWithProduct(OrderItem):
    """Order item with product details."""

    product_name: str
    product_category: str


class OrderItemCreate(BaseModel):
    """Order item model for creation."""

    product_id: int
    quantity: int = Field(..., ge=1)


class OrderBase(BaseModel):
    """Base order model."""

    order_date: Optional[datetime] = None
    total_price: Optional[float] = Field(None, ge=0)
    status: Literal["Pending", "Completed", "Cancelled"] = "Pending"
    user_id: int


class Order(OrderBase):
    """Complete order model with ID."""

    order_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class OrderWithItems(Order):
    """Order with nested items."""

    items: list = []
    customer_name: Optional[str] = None


class OrderCreate(BaseModel):
    """Order model for creation with multiple items."""

    user_id: int
    items: list


class OrderUpdateStatus(BaseModel):
    """Order status update model."""

    status: Literal["Pending", "Completed", "Cancelled"]


class ServiceRequestBase(BaseModel):
    """Base service request model."""

    service_type: Literal["Installation", "Support"]
    request_date: Optional[datetime] = None
    status: Literal["Pending", "In Progress", "Completed", "Cancelled"] = "Pending"
    customer_id: int
    specialist_id: Optional[int] = None


class ServiceRequest(ServiceRequestBase):
    """Complete service request model with ID."""

    request_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ServiceRequestWithDetails(ServiceRequest):
    """Service request with customer and specialist names."""

    customer_name: str
    specialist_name: Optional[str] = None


class ServiceRequestCreate(BaseModel):
    """Service request model for creation."""

    service_type: Literal["Installation", "Support"]
    customer_id: int


class ServiceRequestUpdateStatus(BaseModel):
    """Service request status update model."""

    status: Literal["Pending", "In Progress", "Completed", "Cancelled"]


class SessionUser(BaseModel):
    """Current session user model."""

    user_id: int
    name: str
    email: str
    role: Literal["Customer", "Specialist", "Admin"]


__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "LoginCredentials",
    "SessionUser",
    "Product",
    "ProductCreate",
    "ProductUpdate",
    "Order",
    "OrderCreate",
    "OrderWithItems",
    "OrderItem",
    "OrderItemCreate",
    "OrderItemWithProduct",
    "OrderUpdateStatus",
    "ServiceRequest",
    "ServiceRequestCreate",
    "ServiceRequestWithDetails",
    "ServiceRequestUpdateStatus",
]
