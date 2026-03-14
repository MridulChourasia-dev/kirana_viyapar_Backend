"""
OpenAPI Documentation Helpers - Consistent Swagger documentation patterns
"""
from typing import Any, Dict

# ─────────────────────────────────────────
# Tag Definitions for API Documentation
# ─────────────────────────────────────────

TAGS_METADATA = [
    {
        "name": "Authentication",
        "description": "User authentication and token management endpoints",
    },
    {
        "name": "Customers",
        "description": "Customer management and operations",
    },
    {
        "name": "Vendors",
        "description": "Vendor management and operations",
    },
    {
        "name": "Products",
        "description": "Product catalog management",
    },
    {
        "name": "Inventory",
        "description": "Inventory and stock management",
    },
    {
        "name": "Invoices",
        "description": "Invoice creation and management",
    },
    {
        "name": "Payments",
        "description": "Payment tracking and processing",
    },
    {
        "name": "Expenses",
        "description": "Expense tracking and categorization",
    },
    {
        "name": "Reports",
        "description": "Business reports and analytics",
    },
    {
        "name": "Settings",
        "description": "Application settings and configuration",
    },
    {
        "name": "Background Tasks",
        "description": "Async task management and status",
    },
]

# ─────────────────────────────────────────
# Standard HTTP Status Code Responses
# ─────────────────────────────────────────

HTTP_401_RESPONSE = {
    "description": "Unauthorized - Invalid or missing authentication token",
    "content": {
        "application/json": {
            "example": {
                "detail": "Not authenticated"
            }
        }
    },
}

HTTP_404_RESPONSE = {
    "description": "Not Found - Resource does not exist",
    "content": {
        "application/json": {
            "example": {
                "detail": "Resource not found"
            }
        }
    },
}

HTTP_400_RESPONSE = {
    "description": "Bad Request - Invalid input parameters",
    "content": {
        "application/json": {
            "example": {
                "detail": "Invalid request parameters"
            }
        }
    },
}

HTTP_422_RESPONSE = {
    "description": "Unprocessable Entity - Validation error",
    "content": {
        "application/json": {
            "example": {
                "detail": [
                    {
                        "loc": ["body", "field_name"],
                        "msg": "field required",
                        "type": "value_error"
                    }
                ]
            }
        }
    },
}

HTTP_409_RESPONSE = {
    "description": "Conflict - Resource already exists or operation conflict",
    "content": {
        "application/json": {
            "example": {
                "detail": "Resource already exists"
            }
        }
    },
}

HTTP_500_RESPONSE = {
    "description": "Internal Server Error",
    "content": {
        "application/json": {
            "example": {
                "detail": "Internal server error"
            }
        }
    },
}

# ─────────────────────────────────────────
# Common Response Documentation Sets
# ─────────────────────────────────────────

RESPONSES_CREATE = {
    401: HTTP_401_RESPONSE,
    422: HTTP_422_RESPONSE,
    409: HTTP_409_RESPONSE,
    500: HTTP_500_RESPONSE,
}

RESPONSES_READ = {
    401: HTTP_401_RESPONSE,
    404: HTTP_404_RESPONSE,
    500: HTTP_500_RESPONSE,
}

RESPONSES_LIST = {
    401: HTTP_401_RESPONSE,
    500: HTTP_500_RESPONSE,
}

RESPONSES_UPDATE = {
    401: HTTP_401_RESPONSE,
    404: HTTP_404_RESPONSE,
    422: HTTP_422_RESPONSE,
    409: HTTP_409_RESPONSE,
    500: HTTP_500_RESPONSE,
}

RESPONSES_DELETE = {
    401: HTTP_401_RESPONSE,
    404: HTTP_404_RESPONSE,
    500: HTTP_500_RESPONSE,
}

RESPONSES_ACTION = {
    401: HTTP_401_RESPONSE,
    404: HTTP_404_RESPONSE,
    400: HTTP_400_RESPONSE,
    422: HTTP_422_RESPONSE,
    500: HTTP_500_RESPONSE,
}

# ─────────────────────────────────────────
# Example Payloads for Documentation
# ─────────────────────────────────────────

EXAMPLE_CUSTOMER = {
    "name": "John Smith",
    "email": "john@example.com",
    "phone": "+1234567890",
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "notes": "Preferred customer",
}

EXAMPLE_CUSTOMER_LIST = {
    "items": [EXAMPLE_CUSTOMER],
    "page": 1,
    "per_page": 20,
    "total_items": 1,
    "total_pages": 1,
}

EXAMPLE_PRODUCT = {
    "name": "Widget Pro",
    "description": "Premium widget for professional use",
    "price": 99.99,
    "cost": 50.00,
    "sku": "WIDGET-PRO-001",
    "category": "Tools",
    "is_active": True,
}

EXAMPLE_VENDOR = {
    "name": "Supplier Inc.",
    "email": "supplier@example.com",
    "phone": "+1234567890",
    "address": "456 Market St",
    "city": "Los Angeles",
    "state": "CA",
    "postal_code": "90001",
    "is_active": True,
}

EXAMPLE_INVOICE = {
    "invoice_number": "INV-2024-001",
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "issue_date": "2024-01-15",
    "due_date": "2024-02-15",
    "status": "DRAFT",
    "items": [
        {
            "product_id": "550e8400-e29b-41d4-a716-446655440000",
            "quantity": 2,
            "unit_price": 99.99,
            "tax_rate": 0.1
        }
    ],
}

EXAMPLE_PAYMENT = {
    "invoice_id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 199.98,
    "payment_method": "credit_card",
    "reference": "CC-2024-001",
    "notes": "Payment received",
}

EXAMPLE_EXPENSE = {
    "category_id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 150.00,
    "description": "Office supplies purchase",
    "expense_date": "2024-01-15",
    "notes": "Monthly supplies",
}

# ─────────────────────────────────────────
# OpenAPI Generator Functions
# ─────────────────────────────────────────

def get_endpoint_responses(operation: str) -> Dict[int, Any]:
    """
    Get standard responses for endpoint operation type.
    
    Args:
        operation: One of 'create', 'read', 'list', 'update', 'delete', 'action'
    
    Returns:
        Dictionary of status codes and response descriptions
    """
    responses_map = {
        "create": RESPONSES_CREATE,
        "read": RESPONSES_READ,
        "list": RESPONSES_LIST,
        "update": RESPONSES_UPDATE,
        "delete": RESPONSES_DELETE,
        "action": RESPONSES_ACTION,
    }
    return responses_map.get(operation, RESPONSES_ACTION)
