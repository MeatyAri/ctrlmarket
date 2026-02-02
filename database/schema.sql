-- Smart Equipment Sales & Services Platform Database Schema
-- All constraints as per the EER model provided

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- ============================================
-- 1. User Table
-- ============================================
CREATE TABLE IF NOT EXISTS User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('Customer', 'Specialist', 'Admin')),
    password_hash TEXT NOT NULL
);

-- ============================================
-- 2. Product Table
-- ============================================
CREATE TABLE IF NOT EXISTS Product (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL CHECK (price >= 0)
);

-- ============================================
-- 3. Order Table
-- ============================================
CREATE TABLE IF NOT EXISTS "Order" (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_price REAL CHECK (total_price >= 0),
    status TEXT NOT NULL CHECK (status IN ('Pending', 'Completed', 'Cancelled')) DEFAULT 'Pending',
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

-- ============================================
-- 4. OrderItem Table
-- ============================================
CREATE TABLE IF NOT EXISTS OrderItem (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES "Order"(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE RESTRICT
);

-- ============================================
-- 5. ServiceRequest Table
-- ============================================
CREATE TABLE IF NOT EXISTS ServiceRequest (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_type TEXT NOT NULL CHECK (service_type IN ('Installation', 'Support')),
    request_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL CHECK (status IN ('Pending', 'In Progress', 'Completed', 'Cancelled')),
    customer_id INTEGER NOT NULL,
    specialist_id INTEGER,
    FOREIGN KEY (customer_id) REFERENCES User(user_id),
    FOREIGN KEY (specialist_id) REFERENCES User(user_id),
    CHECK (customer_id != specialist_id)
);

-- ============================================
-- Indexes for better performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_order_user ON "Order"(user_id);
CREATE INDEX IF NOT EXISTS idx_order_status ON "Order"(status);
CREATE INDEX IF NOT EXISTS idx_orderitem_order ON OrderItem(order_id);
CREATE INDEX IF NOT EXISTS idx_orderitem_product ON OrderItem(product_id);
CREATE INDEX IF NOT EXISTS idx_servicereq_customer ON ServiceRequest(customer_id);
CREATE INDEX IF NOT EXISTS idx_servicereq_specialist ON ServiceRequest(specialist_id);
CREATE INDEX IF NOT EXISTS idx_servicereq_status ON ServiceRequest(status);
CREATE INDEX IF NOT EXISTS idx_product_category ON Product(category);
