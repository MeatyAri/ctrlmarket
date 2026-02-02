-- Sample data for Smart Equipment Sales & Services Platform
-- Passwords are hashed with bcrypt

-- ============================================
-- Users (Passwords: 'admin123', 'spec123', 'cust123', etc.)
-- ============================================

-- Admin user (password: admin123)
INSERT INTO User (name, email, phone, role, password_hash) VALUES 
('System Administrator', 'admin@ctrlmarket.com', '09123456789', 'Admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G');

-- Specialists (password: spec123)
INSERT INTO User (name, email, phone, role, password_hash) VALUES 
('Ali Ahmadi', 'ali.ahmadi@ctrlmarket.com', '09123456701', 'Specialist', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G'),
('Sara Rezaei', 'sara.rezaei@ctrlmarket.com', '09123456702', 'Specialist', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G');

-- Customers (password: cust123)
INSERT INTO User (name, email, phone, role, password_hash) VALUES 
('Mohammad Karimi', 'm.karimi@email.com', '09123456711', 'Customer', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G'),
('Fatemeh Moradi', 'f.moradi@email.com', '09123456712', 'Customer', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G'),
('Reza Nouri', 'r.nouri@email.com', '09123456713', 'Customer', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G');

-- ============================================
-- Products
-- ============================================
INSERT INTO Product (name, category, price) VALUES 
('Smart Thermostat Pro', 'Climate Control', 299.99),
('Security Camera 4K', 'Security', 189.99),
('Smart Door Lock', 'Security', 149.99),
('WiFi Mesh System', 'Networking', 249.99),
('Smart Light Hub', 'Lighting', 79.99),
('Voice Assistant Max', 'Smart Home', 129.99),
('Energy Monitor', 'Monitoring', 59.99),
('Smart Smoke Detector', 'Safety', 89.99);

-- ============================================
-- Orders with OrderItems
-- ============================================
-- Order 1: Mohammad Karimi (Customer ID: 4) - Pending
INSERT INTO "Order" (order_date, total_price, status, user_id) VALUES 
('2026-01-15 10:30:00', 489.98, 'Pending', 4);

INSERT INTO OrderItem (quantity, unit_price, order_id, product_id) VALUES 
(1, 299.99, 1, 1),  -- Smart Thermostat
(1, 189.99, 1, 2);  -- Security Camera

-- Order 2: Fatemeh Moradi (Customer ID: 5) - Completed
INSERT INTO "Order" (order_date, total_price, status, user_id) VALUES 
('2026-01-20 14:15:00', 429.97, 'Completed', 5);

INSERT INTO OrderItem (quantity, unit_price, order_id, product_id) VALUES 
(1, 249.99, 2, 4),  -- WiFi Mesh
(2, 89.99, 2, 8);   -- 2x Smoke Detectors

-- Order 3: Reza Nouri (Customer ID: 6) - Cancelled
INSERT INTO "Order" (order_date, total_price, status, user_id) VALUES 
('2026-01-25 09:45:00', 279.98, 'Cancelled', 6);

INSERT INTO OrderItem (quantity, unit_price, order_id, product_id) VALUES 
(1, 149.99, 3, 3),  -- Smart Door Lock
(1, 129.99, 3, 6);  -- Voice Assistant

-- ============================================
-- Service Requests
-- ============================================
-- Request 1: Pending (Mohammad Karimi)
INSERT INTO ServiceRequest (service_type, request_date, status, customer_id, specialist_id) VALUES 
('Installation', '2026-01-16 11:00:00', 'Pending', 4, NULL);

-- Request 2: In Progress (Fatemeh Moradi) - assigned to Ali Ahmadi (Specialist ID: 2)
INSERT INTO ServiceRequest (service_type, request_date, status, customer_id, specialist_id) VALUES 
('Support', '2026-01-21 16:30:00', 'In Progress', 5, 2);

-- Request 3: Pending (Reza Nouri)
INSERT INTO ServiceRequest (service_type, request_date, status, customer_id, specialist_id) VALUES 
('Installation', '2026-01-26 10:00:00', 'Pending', 6, NULL);

-- Request 4: Completed (Mohammad Karimi) - assigned to Sara Rezaei (Specialist ID: 3)
INSERT INTO ServiceRequest (service_type, request_date, status, customer_id, specialist_id) VALUES 
('Installation', '2026-01-10 09:00:00', 'Completed', 4, 3);
