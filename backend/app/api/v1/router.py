from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.customers import router as customers_router
from app.api.v1.products import router as products_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.invoices import router as invoices_router
from app.api.v1.reports import router as reports_router
from app.api.v1.payments import router as payments_router

# ─────────────────────────────────────────
# V1 API Router – Aggregate all module routers
# ─────────────────────────────────────────

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(customers_router)
api_router.include_router(products_router)
api_router.include_router(inventory_router)
api_router.include_router(invoices_router)
api_router.include_router(payments_router)
api_router.include_router(reports_router)

