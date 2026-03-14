# Reporting System — Implementation Summary

## Architecture

```
Backend (FastAPI)                    Mobile (React Native)
─────────────────────────────        ─────────────────────────────
schemas/reports.py                   types/reports.ts
  └─ SalesReport                       └─ SalesReport
  └─ PnLReport                         └─ PnLReport
  └─ InventoryReport                   └─ InventoryReport

services/report_service.py           services/api/reportApi.ts
  └─ ReportService.sales_report()      └─ reportApi.sales()
  └─ ReportService.pnl_report()        └─ reportApi.pnl()
  └─ ReportService.inventory_report()  └─ reportApi.inventory()

api/v1/reports.py                    store/reportStore.ts
  GET /api/v1/reports/sales            └─ useReportStore (Zustand)
  GET /api/v1/reports/pnl
  GET /api/v1/reports/inventory        screens/reports/ReportsScreen.tsx
                                         └─ 3-tab analytics dashboard
api/v1/router.py  ← registered        navigation/AppNavigator.tsx
requirements.txt  ← python-dateutil     └─ 📈 Reports tab (bottom nav)
```

## Reports

### 1. Sales Report (`GET /reports/sales?months=12`)
- KPIs: Total Revenue, Outstanding, Avg Invoice Value, Collection Rate %
- Status breakdown: Paid / Sent / Overdue / Draft / Cancelled amounts
- Monthly revenue bar chart (3M / 6M / 12M selectable)
- Top 10 customers by revenue
- Top 10 products by revenue

### 2. Profit & Loss (`GET /reports/pnl?months=12`)
- KPIs: Gross Profit, COGS, Gross Margin %, Total Discounts
- Monthly dual-bar chart (Revenue vs COGS)
- 6-month P&L table with GP% column
- GST breakdown: CGST / SGST / IGST collected

### 3. Inventory Report (`GET /reports/inventory`)
- KPIs: Total / Active products, Low Stock count, Out of Stock count
- Stock value (at purchase price) vs Retail value (at sale price)
- This-month stock in / stock out movements
- Category-level stock breakdown table
- Low stock alert list (sorted by quantity ASC)
- Fast-moving products (3-month window)

## SQL Queries Used
- [invoices](file:///E:/viyapar_application/backend/app/api/v1/invoices.py#38-49) × `invoice_items` JOIN for revenue, COGS, GST
- `products` × `categories` JOIN for inventory breakdown
- `stock_movements` for monthly in/out
- All queries are **tenant-scoped** via `WHERE tenant_id = :tid`
- Monthly series uses `DATE_TRUNC('month', ...)` + gap-filling in Python

## Files Created / Modified
| File | Action |
|------|--------|
| [backend/app/schemas/reports.py](file:///E:/viyapar_application/backend/app/schemas/reports.py) | ✅ Created |
| [backend/app/services/report_service.py](file:///E:/viyapar_application/backend/app/services/report_service.py) | ✅ Created |
| [backend/app/api/v1/reports.py](file:///E:/viyapar_application/backend/app/api/v1/reports.py) | ✅ Created |
| [backend/app/api/v1/router.py](file:///E:/viyapar_application/backend/app/api/v1/router.py) | ✅ Modified |
| [backend/requirements.txt](file:///E:/viyapar_application/backend/requirements.txt) | ✅ Modified (+python-dateutil) |
| [mobile/src/types/reports.ts](file:///E:/viyapar_application/mobile/src/types/reports.ts) | ✅ Created |
| [mobile/src/services/api/reportApi.ts](file:///E:/viyapar_application/mobile/src/services/api/reportApi.ts) | ✅ Created |
| [mobile/src/store/reportStore.ts](file:///E:/viyapar_application/mobile/src/store/reportStore.ts) | ✅ Created |
| [mobile/src/screens/reports/ReportsScreen.tsx](file:///E:/viyapar_application/mobile/src/screens/reports/ReportsScreen.tsx) | ✅ Created |
| [mobile/src/navigation/AppNavigator.tsx](file:///E:/viyapar_application/mobile/src/navigation/AppNavigator.tsx) | ✅ Modified |
