import math
import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus, PaymentMode
from app.models.product import Product
from app.models.customer import Customer
from app.schemas.invoice import (
    InvoiceCreate, InvoiceUpdate, InvoiceItemCreate,
    InvoiceResponse, InvoiceListItem, InvoiceListResponse,
    InvoiceItemResponse, InvoiceSummary,
)

# ─────────────────────────────────────────
# GST Calculator
# ─────────────────────────────────────────

def _calc_item(item: InvoiceItemCreate, is_igst: bool) -> dict:
    """Compute all monetary fields for a single invoice line item."""
    line_subtotal = round(item.quantity * item.unit_price, 2)
    line_discount = round(line_subtotal * item.discount_pct / 100, 2)
    taxable = round(line_subtotal - line_discount, 2)

    total_gst = round(taxable * item.tax_rate / 100, 2)

    if is_igst:
        cgst = sgst = 0.0
        igst = total_gst
    else:
        half = round(total_gst / 2, 2)
        cgst = sgst = half
        igst = 0.0

    line_total = round(taxable + total_gst, 2)

    return dict(
        line_subtotal=line_subtotal,
        line_discount=line_discount,
        taxable_amount=taxable,
        line_cgst=cgst,
        line_sgst=sgst,
        line_igst=igst,
        line_total=line_total,
    )


# ─────────────────────────────────────────
# Invoice Number Generator
# ─────────────────────────────────────────

async def _next_invoice_number(tenant_id: str, db: AsyncSession) -> str:
    year = date.today().year
    prefix = f"INV-{year}-"
    count_q = select(func.count(Invoice.id)).where(
        Invoice.tenant_id == tenant_id,
        Invoice.invoice_number.like(f"{prefix}%"),
    )
    seq = (await db.execute(count_q)).scalar() or 0
    return f"{prefix}{str(seq + 1).zfill(4)}"


# ─────────────────────────────────────────
# Invoice Service
# ─────────────────────────────────────────

class InvoiceService:

    # ─── Create ───

    @staticmethod
    async def create(tenant_id: str, payload: InvoiceCreate, user_id: str, db: AsyncSession) -> InvoiceResponse:
        invoice_number = await _next_invoice_number(tenant_id, db)

        # Build line items and accumulate totals
        item_rows: list[InvoiceItem] = []
        subtotal = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_igst = 0.0

        for i in payload.items:
            calc = _calc_item(i, payload.is_igst)
            item_rows.append(InvoiceItem(
                tenant_id=tenant_id,
                product_id=uuid.UUID(i.product_id) if i.product_id else None,
                product_name=i.product_name,
                hsn_code=i.hsn_code,
                unit=i.unit,
                quantity=i.quantity,
                unit_price=i.unit_price,
                tax_rate=i.tax_rate,
                discount_pct=i.discount_pct,
                **calc,
            ))
            subtotal += calc["line_subtotal"]
            total_cgst += calc["line_cgst"]
            total_sgst += calc["line_sgst"]
            total_igst += calc["line_igst"]

        subtotal = round(subtotal, 2)
        total_cgst = round(total_cgst, 2)
        total_sgst = round(total_sgst, 2)
        total_igst = round(total_igst, 2)
        total_tax = round(total_cgst + total_sgst + total_igst, 2)
        discount_amount = round(payload.discount_amount, 2)
        grand_total = round(subtotal + total_tax - discount_amount, 2)
        amount_due = round(grand_total, 2)

        invoice = Invoice(
            tenant_id=tenant_id,
            invoice_number=invoice_number,
            customer_id=uuid.UUID(payload.customer_id) if payload.customer_id else None,
            customer_name=payload.customer_name,
            customer_phone=payload.customer_phone,
            customer_gst=payload.customer_gst,
            billing_address=payload.billing_address,
            invoice_date=payload.invoice_date,
            due_date=payload.due_date,
            is_igst=payload.is_igst,
            subtotal=subtotal,
            total_cgst=total_cgst,
            total_sgst=total_sgst,
            total_igst=total_igst,
            total_tax=total_tax,
            discount_amount=discount_amount,
            grand_total=grand_total,
            amount_paid=0.0,
            amount_due=amount_due,
            payment_mode=payload.payment_mode,
            notes=payload.notes,
            terms=payload.terms,
            items=item_rows,
        )
        db.add(invoice)

        # Update customer balance (increase outstanding) if customer exists
        if invoice.customer_id:
            result = await db.execute(select(Customer).where(Customer.id == invoice.customer_id))
            customer = result.scalar_one_or_none()
            if customer:
                customer.balance = round(float(customer.balance) + float(amount_due), 2)

        await db.commit()
        await db.refresh(invoice, attribute_names=["items"])
        return InvoiceService._to_response(invoice)

    # ─── List ───

    @staticmethod
    async def list(
        tenant_id: str,
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
        status_filter: str | None = None,
    ) -> InvoiceListResponse:
        query = (
            select(Invoice)
            .where(Invoice.tenant_id == tenant_id)
        )
        if search:
            pat = f"%{search}%"
            query = query.where(
                or_(
                    Invoice.invoice_number.ilike(pat),
                    Invoice.customer_name.ilike(pat),
                )
            )
        if status_filter:
            query = query.where(Invoice.status == status_filter)

        count_q = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_q)).scalar() or 0
        total_pages = math.ceil(total / per_page) if total > 0 else 1

        query = query.order_by(Invoice.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        invoices = result.scalars().all()

        return InvoiceListResponse(
            data=[InvoiceService._to_list_item(inv) for inv in invoices],
            total=total, page=page, per_page=per_page, total_pages=total_pages,
        )

    # ─── Get by ID ───

    @staticmethod
    async def get_by_id(tenant_id: str, invoice_id: str, db: AsyncSession) -> InvoiceResponse:
        invoice = await InvoiceService._get_or_404(tenant_id, invoice_id, db)
        return InvoiceService._to_response(invoice)

    # ─── Update (status / payment) ───

    @staticmethod
    async def update(
        tenant_id: str, invoice_id: str, payload: InvoiceUpdate, db: AsyncSession
    ) -> InvoiceResponse:
        invoice = await InvoiceService._get_or_404(tenant_id, invoice_id, db)

        if payload.status is not None:
            invoice.status = payload.status
        if payload.due_date is not None:
            invoice.due_date = payload.due_date
        if payload.payment_mode is not None:
            invoice.payment_mode = payload.payment_mode
        if payload.notes is not None:
            invoice.notes = payload.notes
        if payload.terms is not None:
            invoice.terms = payload.terms
        if payload.amount_paid is not None:
            invoice.amount_paid = round(payload.amount_paid, 2)
            invoice.amount_due = round(invoice.grand_total - invoice.amount_paid, 2)
            # Auto-update status based on payment
            if invoice.amount_due <= 0:
                invoice.status = InvoiceStatus.PAID
            elif invoice.amount_paid > 0:
                invoice.status = InvoiceStatus.PARTIALLY_PAID

        await db.commit()
        await db.refresh(invoice, attribute_names=["items"])
        return InvoiceService._to_response(invoice)

    # ─── Delete (cancel) ───

    @staticmethod
    async def delete(tenant_id: str, invoice_id: str, db: AsyncSession) -> None:
        invoice = await InvoiceService._get_or_404(tenant_id, invoice_id, db)
        invoice.status = InvoiceStatus.CANCELLED
        await db.commit()

    # ─── Summary Dashboard ───

    @staticmethod
    async def get_summary(tenant_id: str, db: AsyncSession) -> InvoiceSummary:
        base = Invoice.tenant_id == tenant_id

        total_q = select(func.count(Invoice.id)).where(base)
        total_invoices = (await db.execute(total_q)).scalar() or 0

        revenue_q = select(func.sum(Invoice.grand_total)).where(base, Invoice.status != InvoiceStatus.CANCELLED)
        total_revenue = float((await db.execute(revenue_q)).scalar() or 0)

        paid_q = select(func.sum(Invoice.amount_paid)).where(base)
        total_paid = float((await db.execute(paid_q)).scalar() or 0)

        outstanding_q = select(func.sum(Invoice.amount_due)).where(
            base, Invoice.status.notin_([InvoiceStatus.PAID, InvoiceStatus.CANCELLED])
        )
        total_outstanding = float((await db.execute(outstanding_q)).scalar() or 0)

        draft_q = select(func.count(Invoice.id)).where(base, Invoice.status == InvoiceStatus.DRAFT)
        draft_count = (await db.execute(draft_q)).scalar() or 0

        overdue_q = select(func.count(Invoice.id)).where(base, Invoice.status == InvoiceStatus.OVERDUE)
        overdue_count = (await db.execute(overdue_q)).scalar() or 0

        return InvoiceSummary(
            total_invoices=total_invoices,
            total_revenue=round(total_revenue, 2),
            total_outstanding=round(total_outstanding, 2),
            total_paid=round(total_paid, 2),
            draft_count=draft_count,
            overdue_count=overdue_count,
        )

    # ─── Helpers ───

    @staticmethod
    async def _get_or_404(tenant_id: str, invoice_id: str, db: AsyncSession) -> Invoice:
        result = await db.execute(
            select(Invoice)
            .options(selectinload(Invoice.items))
            .where(Invoice.id == invoice_id, Invoice.tenant_id == tenant_id)
        )
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
        return invoice

    @staticmethod
    def _to_response(invoice: Invoice) -> InvoiceResponse:
        return InvoiceResponse(
            id=str(invoice.id),
            invoice_number=invoice.invoice_number,
            customer_id=str(invoice.customer_id) if invoice.customer_id else None,
            customer_name=invoice.customer_name,
            customer_phone=invoice.customer_phone,
            customer_gst=invoice.customer_gst,
            billing_address=invoice.billing_address,
            status=invoice.status.value if hasattr(invoice.status, "value") else invoice.status,
            invoice_date=invoice.invoice_date,
            due_date=invoice.due_date,
            subtotal=float(invoice.subtotal),
            total_cgst=float(invoice.total_cgst),
            total_sgst=float(invoice.total_sgst),
            total_igst=float(invoice.total_igst),
            total_tax=float(invoice.total_tax),
            discount_amount=float(invoice.discount_amount),
            grand_total=float(invoice.grand_total),
            amount_paid=float(invoice.amount_paid),
            amount_due=float(invoice.amount_due),
            is_igst=invoice.is_igst,
            payment_mode=invoice.payment_mode.value if hasattr(invoice.payment_mode, "value") else invoice.payment_mode,
            notes=invoice.notes,
            terms=invoice.terms,
            items=[InvoiceService._to_item_response(it) for it in (invoice.items or [])],
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
        )

    @staticmethod
    def _to_list_item(invoice: Invoice) -> InvoiceListItem:
        return InvoiceListItem(
            id=str(invoice.id),
            invoice_number=invoice.invoice_number,
            customer_name=invoice.customer_name,
            customer_phone=invoice.customer_phone,
            status=invoice.status.value if hasattr(invoice.status, "value") else invoice.status,
            invoice_date=invoice.invoice_date,
            due_date=invoice.due_date,
            grand_total=float(invoice.grand_total),
            amount_paid=float(invoice.amount_paid),
            amount_due=float(invoice.amount_due),
            created_at=invoice.created_at,
        )

    @staticmethod
    def _to_item_response(item: InvoiceItem) -> InvoiceItemResponse:
        return InvoiceItemResponse(
            id=str(item.id),
            product_id=str(item.product_id) if item.product_id else None,
            product_name=item.product_name,
            hsn_code=item.hsn_code,
            unit=item.unit,
            quantity=float(item.quantity),
            unit_price=float(item.unit_price),
            tax_rate=float(item.tax_rate),
            discount_pct=float(item.discount_pct),
            line_subtotal=float(item.line_subtotal),
            line_discount=float(item.line_discount),
            taxable_amount=float(item.taxable_amount),
            line_cgst=float(item.line_cgst),
            line_sgst=float(item.line_sgst),
            line_igst=float(item.line_igst),
            line_total=float(item.line_total),
        )
