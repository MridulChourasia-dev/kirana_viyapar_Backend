# Database Schema

## Overview

Viyapar uses PostgreSQL as its primary data store with SQLAlchemy ORM for database abstraction. The schema supports multi-tenancy with complete data isolation at the application level.

## Entity Relationship Diagram

```
                    ┌──────────────────┐
                    │     Business     │ (Tenant)
                    │   (Businesses)   │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼─────────────────────────┐
        │                    │                         │
        ├────────┐      ├─────────┐             ├──────────┐
        │         │      │         │             │          │
    ┌───▼──────┐ │  ┌───▼─────┐   │         ┌───▼────────┐ │
    │   User   │◄┤  │ Product │   │         │  Customer  │ │
    │  (Users) │ │  │(Products)   │         │ (Customers)│ │
    └──────────┘ │  └─┬──────┘    │         └────────────┘ │
                 │    │           │                         │
            ┌────┼────┼───┐   ┌───▼──────────────┐          │
            │    │    │   │   │                  │          │
        ┌───▼─┐ │ ┌──┴──┐ │  │                  │          │
        │Role │ │ │Category   │                  │          │
        │(Roles)  │(Categories)   │                  │          │
        └─────┘ │ └──────┘ │  │                  │          │
                │          │  │                  │          │
                │      ┌───▼──────────────────┐  │          │
                │      │     Invoice       │  │          │
                │      │   (Invoices)      │  │          │
    ┌───────────┼──────┼────────┬───────────┼──┤          │
    │           │      └────────┼───────────┼──┤          │
    │       ┌───▼────────┐      │       ┌───▼──▼──────┐   │
    │       │ InvoiceItem│      │       │   Payment   │   │
    │       │ (InvoiceItem)     │       │ (Payments)  │   │
    │       └────────────┘      │       └─────────────┘   │
    │                           │                         │
    │                      ┌────▼──────────────┐          │
    │                      │  StockMovement    │          │
    │                      │(StockMovement)    │          │
    │                      └───────────────────┘          │
    │                                                     │
    │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
    │  │   Vendor     │  │   Purchase   │  │  Expense  │ │
    │  │  (Vendors)   │  │ (Purchases)  │  │ (Expenses)│ │
    │  └──────────────┘  └──────────────┘  └───────────┘ │
    │                                                     │
    │  ┌────────────────────────────────────────────────┐ │
    │  │  Notification    Setting    FileUpload         │ │
    │  │  (Notifications) (Settings) (FileUpload)       │ │
    │  └────────────────────────────────────────────────┘ │
    │                                                     │
    └─────────────────────────────────────────────────────┘
```

## Schema Details

### 1. Business (Tenant)
- Represents a business account/organization
- Root entity for multi-tenancy data isolation
- Contains business details, tax info, and branding

```sql
CREATE TABLE business (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    description VARCHAR(500),
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    pincode VARCHAR(20),
    gstin VARCHAR(15) UNIQUE,
    pan VARCHAR(10) UNIQUE,
    logo_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_business_email ON business(email);
CREATE INDEX idx_business_gstin ON business(gstin);
```

### 2. User (Staff/Employees)
- Business staff members
- Role-based access control
- Multi-user business support

```sql
CREATE TABLE "user" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES business(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    role_id UUID REFERENCES role(id),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_business_id ON "user"(business_id);
CREATE INDEX idx_user_email ON "user"(email);
CREATE UNIQUE INDEX idx_user_business_email ON "user"(business_id, email);
```

### 3. Role & Permission
- Role-based access control
- Granular permissions
- Admin, Manager, Staff roles

```sql
CREATE TABLE permission (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE role (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES business(id),
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_role_business_name ON role(business_id, name);
```

### 4. Customer
- Business customers/clients
- Contact and billing information
- Transaction history

```sql
CREATE TABLE customer (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES business(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    pincode VARCHAR(20),
    gstin VARCHAR(15),
    pan VARCHAR(10),
    credit_limit DECIMAL(12, 2),
    outstanding_balance DECIMAL(12, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_customer_business_id ON customer(business_id);
CREATE INDEX idx_customer_name ON customer(name);
CREATE INDEX idx_customer_email ON customer(email);
```

### 5. Product & Category
- Product catalog
- Inventory tracking
- Categorization

```sql
CREATE TABLE category (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES business(id),
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    parent_category_id UUID REFERENCES category(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_category_business_id ON category(business_id);
CREATE UNIQUE INDEX idx_category_business_name ON category(business_id, name);

CREATE TABLE product (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES business(id),
    category_id UUID REFERENCES category(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sku VARCHAR(100) UNIQUE NOT NULL,
    price DECIMAL(12, 2) NOT NULL,
    cost_price DECIMAL(12, 2),
    quantity INTEGER DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 10,
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_product_business_id ON product(business_id);
CREATE INDEX idx_product_category_id ON product(category_id);
CREATE INDEX idx_product_sku ON product(sku);
```

### 6. Vendor (Supplier)
- Supplier/vendor management
- Purchase tracking

```sql
CREATE TABLE vendor (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES business(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    pincode VARCHAR(20),
    gst_number VARCHAR(15),
    contact_person VARCHAR(255),
    payment_terms VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_vendor_business_id ON vendor(business_id);
CREATE INDEX idx_vendor_name ON vendor(name);
```

### 7. Invoice & InvoiceItem
- Invoice generation and tracking
- Line-item breakdown
- GST calculation

```sql
CREATE TABLE invoice (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES business(id),
    customer_id UUID NOT NULL REFERENCES customer(id),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE,
    status VARCHAR(50) DEFAULT 'draft',
    subtotal DECIMAL(12, 2),
    gst_amount DECIMAL(12, 2),
    total_amount DECIMAL(12, 2),
    paid_amount DECIMAL(12, 2) DEFAULT 0,
    outstanding_amount DECIMAL(12, 2),
    notes TEXT,
    created_by UUID REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_invoice_business_id ON invoice(business_id);
CREATE INDEX idx_invoice_customer_id ON invoice(customer_id);
CREATE INDEX idx_invoice_status ON invoice(status);
CREATE INDEX idx_invoice_issue_date ON invoice(issue_date);

CREATE TABLE invoice_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES invoice(id) ON DELETE CASCADE,
    product_id UUID REFERENCES product(id),
    description VARCHAR(500),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    amount DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_invoice_item_invoice_id ON invoice_item(invoice_id);
```

### 8. Payment
- Payment recording and tracking
- Multiple payment methods
- Invoice reconciliation

```sql
CREATE TABLE payment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES business(id),
    invoice_id UUID NOT NULL REFERENCES invoice(id),
    amount DECIMAL(12, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    reference_number VARCHAR(100),
    payment_date TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'completed',
    notes TEXT,
    created_by UUID REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_payment_business_id ON payment(business_id);
CREATE INDEX idx_payment_invoice_id ON payment(invoice_id);
CREATE INDEX idx_payment_payment_date ON payment(payment_date);
```

### 9. StockMovement
- Audit trail of all stock changes
- Movement type tracking
- Reference linking

```sql
CREATE TABLE stock_movement (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES business(id),
    product_id UUID NOT NULL REFERENCES product(id),
    movement_type VARCHAR(50) NOT NULL,
    quantity_change INTEGER NOT NULL,
    reference_type VARCHAR(50),
    reference_id UUID,
    notes TEXT,
    created_by UUID REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_stock_movement_business_id ON stock_movement(business_id);
CREATE INDEX idx_stock_movement_product_id ON stock_movement(product_id);
CREATE INDEX idx_stock_movement_type ON stock_movement(movement_type);
CREATE INDEX idx_stock_movement_created_at ON stock_movement(created_at);
```

### 10. Expense & ExpenseCategory
- Expense tracking and categorization
- Monthly budgeting

```sql
CREATE TABLE expense_category (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES business(id),
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    budget_limit DECIMAL(12, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_expense_category_business_id ON expense_category(business_id);

CREATE TABLE expense (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES business(id),
    category_id UUID REFERENCES expense_category(id),
    amount DECIMAL(12, 2) NOT NULL,
    description TEXT,
    expense_date DATE NOT NULL,
    payment_method VARCHAR(50),
    reference VARCHAR(100),
    notes TEXT,
    created_by UUID REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_expense_business_id ON expense(business_id);
CREATE INDEX idx_expense_category_id ON expense(category_id);
CREATE INDEX idx_expense_date ON expense(expense_date);
```

### 11. Purchase & PurchaseItem
- Purchase order management
- Vendor order tracking

```sql
CREATE TABLE purchase (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES business(id),
    vendor_id UUID NOT NULL REFERENCES vendor(id),
    po_number VARCHAR(50) UNIQUE,
    po_date DATE NOT NULL,
    expected_delivery DATE,
    status VARCHAR(50) DEFAULT 'draft',
    subtotal DECIMAL(12, 2),
    gst_amount DECIMAL(12, 2),
    total_amount DECIMAL(12, 2),
    notes TEXT,
    created_by UUID REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_purchase_business_id ON purchase(business_id);
CREATE INDEX idx_purchase_vendor_id ON purchase(vendor_id);

CREATE TABLE purchase_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    purchase_id UUID NOT NULL REFERENCES purchase(id) ON DELETE CASCADE,
    product_id UUID REFERENCES product(id),
    description VARCHAR(500),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    amount DECIMAL(12, 2)
);

CREATE INDEX idx_purchase_item_purchase_id ON purchase_item(purchase_id);
```

### 12. Notification
- User notifications
- Multi-channel delivery tracking

```sql
CREATE TABLE notification (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES business(id),
    recipient_id UUID NOT NULL REFERENCES "user"(id),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    related_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    read_at TIMESTAMP
);

CREATE INDEX idx_notification_business_id ON notification(business_id);
CREATE INDEX idx_notification_recipient_id ON notification(recipient_id);
CREATE INDEX idx_notification_is_read ON notification(is_read);
```

### 13. Settings
- Application configuration
- Business settings
- User preferences

```sql
CREATE TABLE settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES business(id),
    key VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    value TEXT,
    description VARCHAR(500),
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_settings_business_id ON settings(business_id);
CREATE UNIQUE INDEX idx_settings_business_key ON settings(business_id, key, category);
```

### 14. FileUpload
- Track uploaded files
- Document management

```sql
CREATE TABLE file_upload (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES business(id),
    uploaded_by UUID REFERENCES "user"(id),
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(100),
    file_size INTEGER,
    file_path VARCHAR(500),
    related_entity_type VARCHAR(50),
    related_entity_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_file_upload_business_id ON file_upload(business_id);
```

## Key Design Principles

### 1. Multi-Tenancy
- Every table except core system tables has `business_id`
- Complete data isolation at query level
- No cross-tenant data visibility

### 2. Data Integrity
- Foreign key constraints for referential integrity
- CASCADE DELETE for maintaining consistency
- Soft deletes via `is_active` flag where needed

### 3. Performance
- Strategic indexes on frequently queried columns
- Composite indexes for common filter combinations
- No N+1 query issues via eager loading

### 4. Audit Trail
- Timestamps: `created_at`, `updated_at`, `deleted_at`
- User tracking: `created_by`, `updated_by`
- Status tracking for state machines (invoice, purchase)

### 5. Scalability
- UUID primary keys for distributed systems
- Sequential invoice/PO numbers (application-generated)
- JSONB for flexible data (related_data, metadata)

## Indexing Strategy

### Primary Key Indexes
- Automatically created on all `id` columns

### Unique Indexes
- SKU (product uniqueness)
- Email (user uniqueness within business)
- Invoice/PO numbers (uniqueness)

### Foreign Key Indexes
- `business_id` (tenant isolation)
- `customer_id`, `vendor_id` (navigation)
- `product_id` (catalog references)

### Query Performance Indexes
- `status` (invoice, purchase state)
- `created_at` (temporal queries)
- `is_active` (active records)
- `category_id`, `payment_method` (filters)

## Composite Indexes

```sql
-- Multi-field queries
CREATE INDEX idx_invoice_business_customer ON invoice(business_id, customer_id);
CREATE INDEX idx_payment_business_invoice ON payment(business_id, invoice_id);
CREATE INDEX idx_expense_business_date ON expense(business_id, expense_date);
```

## Query Examples

### Get Customer Outstanding Balance
```sql
SELECT 
    c.id,
    c.name,
    SUM(i.total_amount) - SUM(COALESCE(p.amount, 0)) as outstanding
FROM customer c
LEFT JOIN invoice i ON c.id = i.customer_id
LEFT JOIN payment p ON i.id = p.invoice_id
WHERE c.business_id = $1 AND c.id = $2
GROUP BY c.id, c.name;
```

### Get Low Stock Products
```sql
SELECT *
FROM product
WHERE business_id = $1
AND quantity <= low_stock_threshold
AND is_active = TRUE
ORDER BY quantity ASC;
```

### Monthly Sales Summary
```sql
SELECT 
    DATE_TRUNC('month', i.issue_date) as month,
    COUNT(i.id) as invoice_count,
    SUM(i.total_amount) as revenue,
    SUM(p.amount) as collection
FROM invoice i
LEFT JOIN payment p ON i.id = p.invoice_id
WHERE i.business_id = $1
AND i.issue_date >= $2
GROUP BY DATE_TRUNC('month', i.issue_date)
ORDER BY month DESC;
```

## Migrations

Database migrations are managed with Alembic:

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Backup Strategy

- Daily automated backups
- Point-in-time recovery enabled
- Replicated to multiple regions
- WAL archiving for continuous recovery
