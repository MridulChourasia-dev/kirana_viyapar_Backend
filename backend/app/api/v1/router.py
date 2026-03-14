from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.customers import router as customers_router
from app.api.v1.products import router as products_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.invoices import router as invoices_router
from app.api.v1.reports import router as reports_router
from app.api.v1.payments import router as payments_router
from app.api.v1.vendors import router as vendors_router
from app.api.v1.purchases import router as purchases_router
from app.api.v1.expenses import router as expenses_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.settings import router as settings_router
from app.api.v1.tasks import router as tasks_router

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
api_router.include_router(vendors_router)
api_router.include_router(purchases_router)
api_router.include_router(expenses_router)
api_router.include_router(notifications_router)
api_router.include_router(settings_router)
api_router.include_router(tasks_router)

