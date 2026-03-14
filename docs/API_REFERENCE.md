# API Reference Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <access_token>
```

## Response Format

### Success Response (2xx)
```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful"
}
```

### Error Response (4xx, 5xx)
```json
{
  "success": false,
  "error": "Error message",
  "details": {...}
}
```

## Auth API

### Register
```
POST /auth/register
Content-Type: application/json

Request:
{
  "name": "Rahul Sharma",
  "email": "rahul@example.com",
  "password": "securepassword123",
  "phone": "+919876543210",
  "business_name": "Sharma Traders"
}

Response: 201 Created
{
  "user": {
    "id": "....",
    "email": "rahul@example.com",
    "name": "Rahul Sharma",
    "role": "owner"
  },
  "business": {
    "id": "....",
    "name": "Sharma Traders",
    "email": "business@example.com"
  },
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### Login
```
POST /auth/login
Content-Type: application/json

Request:
{
  "email": "rahul@example.com",
  "password": "securepassword123"
}

Response: 200 OK
{
  "user": {...},
  "business": {...},
  "tokens": {...}
}
```

### Refresh Token
```
POST /auth/refresh
Content-Type: application/json

Request:
{
  "refresh_token": "eyJraWQiOiI..."
}

Response: 200 OK
{
  "access_token": "new_token",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## Customer API

### List Customers
```
GET /customers?page=1&per_page=20&search=amit
Authorization: Bearer <token>

Response: 200 OK
{
  "data": [
    {
      "id": "uuid",
      "name": "Amit Patel",
      "phone": "+919876543210",
      "email": "amit@example.com",
      "city": "Mumbai",
      "balance": 5000.00
    }
  ],
  "pagination": {
    "total": 50,
    "page": 1,
    "per_page": 20,
    "pages": 3
  }
}
```

### Create Customer
```
POST /customers
Content-Type: application/json
Authorization: Bearer <token>

Request:
{
  "name": "Amit Patel",
  "phone": "+919876543210",
  "email": "amit@example.com",
  "gstin": "29ABCDE1234F1Z5",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400001",
  "billing_address": "123 MG Road",
  "notes": "Regular customer"
}

Response: 201 Created
{
  "id": "uuid",
  "business_id": "uuid",
  "name": "Amit Patel",
  "phone": "+919876543210",
  "email": "amit@example.com",
  "gstin": "29ABCDE1234F1Z5",
  "city": "Mumbai",
  "balance": 0.00,
  "created_at": "2026-03-13T10:30:45.123Z",
  "updated_at": "2026-03-13T10:30:45.123Z"
}
```

### Get Customer
```
GET /customers/{customer_id}
Authorization: Bearer <token>

Response: 200 OK
{...}
```

### Update Customer
```
PUT /customers/{customer_id}
Content-Type: application/json
Authorization: Bearer <token>

Request:
{
  "phone": "+919876543211",
  "email": "new@example.com"
}

Response: 200 OK
{...}
```

### Delete Customer
```
DELETE /customers/{customer_id}
Authorization: Bearer <token>

Response: 204 No Content
```

## Product API

### List Products
```
GET /products?category_id=uuid&in_stock=true
Authorization: Bearer <token>

Response: 200 OK
{
  "data": [
    {
      "id": "uuid",
      "name": "Wireless Mouse",
      "sku": "WM-001",
      "sale_price": 599.00,
      "purchase_price": 350.00,
      "stock_quantity": 50,
      "tax_rate": 18.00
    }
  ]
}
```

### Create Product
```
POST /products
Content-Type: application/json
Authorization: Bearer <token>

Request:
{
  "name": "Wireless Mouse",
  "sku": "WM-001",
  "barcode": "1234567890123",
  "hsn_code": "8471",
  "description": "2.4GHz wireless mouse",
  "category_id": "uuid",
  "sale_price": 599.00,
  "purchase_price": 350.00,
  "tax_rate": 18.00,
  "stock_quantity": 50,
  "low_stock_alert": 10,
  "unit": "piece"
}

Response: 201 Created
{...}
```

### Get Product
```
GET /products/{product_id}
Authorization: Bearer <token>

Response: 200 OK
{...}
```

### Update Product
```
PUT /products/{product_id}
Content-Type: application/json
Authorization: Bearer <token>

Request:
{
  "sale_price": 649.00
}

Response: 200 OK
{...}
```

### Delete Product
```
DELETE /products/{product_id}
Authorization: Bearer <token>

Response: 204 No Content
```

### Low Stock Alert
```
GET /products/low-stock
Authorization: Bearer <token>

Response: 200 OK
{
  "data": [
    {
      "id": "uuid",
      "name": "Wireless Mouse",
      "sku": "WM-001",
      "stock_quantity": 5,
      "low_stock_alert": 10
    }
  ]
}
```

## Invoice API

### List Invoices
```
GET /invoices?status=sent&from_date=2026-01-01&to_date=2026-03-13
Authorization: Bearer <token>

Response: 200 OK
{
  "data": [
    {
      "id": "uuid",
      "invoice_number": "INV-2026-0001",
      "customer_id": "uuid",
      "customer_name": "Amit Patel",
      "invoice_date": "2026-03-13",
      "status": "sent",
      "grand_total": 119.00,
      "amount_paid": 0.00,
      "amount_due": 119.00
    }
  ]
}
```

### Create Invoice
```
POST /invoices
Content-Type: application/json
Authorization: Bearer <token>

Request:
{
  "customer_id": "uuid",
  "invoice_date": "2026-03-13",
  "due_date": "2026-04-13",
  "items": [
    {
      "product_id": "uuid",
      "quantity": 2,
      "unit_price": 599.00,
      "discount_pct": 0,
      "tax_rate": 18
    }
  ],
  "discount_amount": 0,
  "payment_mode": "upi",
  "notes": "Thank you for your business"
}

Response: 201 Created
{
  "id": "uuid",
  "invoice_number": "INV-2026-0001",
  "customer_id": "uuid",
  "invoice_date": "2026-03-13",
  "status": "draft",
  "subtotal": 1198.00,
  "total_tax": 215.64,
  "grand_total": 1413.64,
  "items": [...]
}
```

### Get Invoice
```
GET /invoices/{invoice_id}
Authorization: Bearer <token>

Response: 200 OK
{...}
```

### Send Invoice
```
POST /invoices/{invoice_id}/send
Authorization: Bearer <token>

Response: 200 OK
{
  "status": "sent",
  "message": "Invoice sent to customer"
}
```

### Record Payment
```
POST /invoices/{invoice_id}/payments
Content-Type: application/json
Authorization: Bearer <token>

Request:
{
  "amount": 500.00,
  "payment_method": "upi",
  "reference": "UPI123456",
  "notes": "Partial payment received"
}

Response: 201 Created
{
  "invoice_id": "uuid",
  "payment_id": "uuid",
  "amount": 500.00,
  "amount_paid": 500.00,
  "amount_due": 913.64,
  "status": "partially_paid"
}
```

## Payment API

### List Payments
```
GET /payments?invoice_id=uuid&from_date=2026-01-01
Authorization: Bearer <token>

Response: 200 OK
{
  "data": [
    {
      "id": "uuid",
      "invoice_number": "INV-2026-0001",
      "customer_name": "Amit Patel",
      "amount": 500.00,
      "payment_date": "2026-03-13",
      "method": "upi",
      "reference": "UPI123456"
    }
  ]
}
```

### Get Payment
```
GET /payments/{payment_id}
Authorization: Bearer <token>

Response: 200 OK
{...}
```

## Report API

### Sales Report
```
GET /reports/sales?from_date=2026-01-01&to_date=2026-03-13&group_by=day
Authorization: Bearer <token>

Response: 200 OK
{
  "data": [
    {
      "date": "2026-03-13",
      "total_invoices": 10,
      "total_amount": 50000.00,
      "paid": 35000.00,
      "pending": 15000.00
    }
  ]
}
```

### Revenue Report
```
GET /reports/revenue?from_date=2026-01-01&to_date=2026-03-13
Authorization: Bearer <token>

Response: 200 OK
{
  "total_revenue": 50000.00,
  "total_paid": 35000.00,
  "total_pending": 15000.00,
  "average_transaction": 5000.00
}
```

### Inventory Report
```
GET /reports/inventory?category_id=uuid
Authorization: Bearer <token>

Response: 200 OK
{
  "data": [
    {
      "product_id": "uuid",
      "product_name": "Wireless Mouse",
      "stock_quantity": 50,
      "value": 17500.00,
      "turnover_rate": 0.85
    }
  ],
  "total_inventory_value": 250000.00
}
```

### Debtors Report
```
GET /reports/debtors?sort_by=overdue
Authorization: Bearer <token>

Response: 200 OK
{
  "data": [
    {
      "customer_id": "uuid",
      "customer_name": "Amit Patel",
      "total_outstanding": 15000.00,
      "most_overdue_days": 45,
      "invoice_count": 3
    }
  ],
  "total_debts": 250000.00
}
```

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created |
| 204 | No Content | Resource deleted |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing/invalid authentication token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate resource (e.g., email already exists) |
| 422 | Unprocessable | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Database/service unavailable |

## Rate Limiting

- Default: 100 requests per minute per user
- Burst: 200 requests per 10 seconds
- Rate limit headers returned in response

## Versioning

- Current Version: v1
- API URLs: `/api/v1/*`
- Future versions will be: `/api/v2/*`, etc.
- Version deprecation notice: 6 months before removal
