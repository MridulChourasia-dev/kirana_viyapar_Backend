import uuid
from datetime import datetime, date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.payment import Payment, PaymentMethod
from app.models.invoice import Invoice, InvoiceStatus
from app.models.customer import Customer
from app.schemas.payment import (
    PaymentCreate, PaymentResponse, PaymentListResponse,
    CustomerBalanceResponse, CustomerInvoiceSummary,
)


class PaymentService:

    @staticmethod
    async def create(tenant_id: str, payload: PaymentCreate, user_id: str, db: AsyncSession) -> PaymentResponse:
        # Load invoice
        result = await db.execute(select(Invoice).where(Invoice.id == payload.invoice_id, Invoice.business_id == tenant_id))
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

        # Compute balances
        balance_before = float(invoice.amount_due)
        amount = float(payload.amount)

        # Update invoice paid/due
        invoice.amount_paid = round(float(invoice.amount_paid) + amount, 2)
        invoice.amount_due = round(float(invoice.grand_total) - float(invoice.amount_paid), 2)
        if invoice.amount_due <= 0:
            invoice.status = InvoiceStatus.PAID.value
        elif invoice.amount_paid > 0:
            invoice.status = InvoiceStatus.PARTIALLY_PAID.value

        # Update customer balance snapshot
        customer = None
        if invoice.customer_id:
            cust_res = await db.execute(select(Customer).where(Customer.id == invoice.customer_id))
            customer = cust_res.scalar_one_or_none()
            if customer:
                customer.balance = round(float(customer.balance) - amount, 2)

        # Create payment row
        payment = Payment(
            business_id=tenant_id,
            invoice_id=invoice.id,
            customer_id=invoice.customer_id,
            amount=amount,
            method=payload.method,
            reference=payload.reference,
            payment_date=date.fromisoformat(payload.payment_date),
            notes=payload.notes,
            invoice_number=invoice.invoice_number,
            invoice_total=float(invoice.grand_total),
            balance_before=balance_before,
            balance_after=float(invoice.amount_due),
        )

        db.add(payment)
        await db.commit()
        await db.refresh(payment, attribute_names=["invoice"])

        return PaymentService._to_response(payment)

    @staticmethod
    async def list_by_invoice(tenant_id: str, invoice_id: str, db: AsyncSession) -> PaymentListResponse:
        q = (
            select(Payment)
            .options(selectinload(Payment.invoice))
            .where(Payment.business_id == tenant_id, Payment.invoice_id == invoice_id)
            .order_by(Payment.created_at.desc())
        )
        result = await db.execute(q)
        rows = result.scalars().all()

        total = len(rows)
        total_paid = sum(float(r.amount) for r in rows)
        total_outstanding = 0.0

        return PaymentListResponse(
            data=[PaymentService._to_response(r) for r in rows],
            total=total,
            total_paid=round(total_paid, 2),
            total_outstanding=round(total_outstanding, 2),
        )

    @staticmethod
    async def list_all(tenant_id: str, db: AsyncSession) -> PaymentListResponse:
        q = (
            select(Payment)
            .options(selectinload(Payment.invoice))
            .where(Payment.business_id == tenant_id)
            .order_by(Payment.created_at.desc())
        )
        result = await db.execute(q)
        rows = result.scalars().all()

        total = len(rows)
        total_paid = sum(float(r.amount) for r in rows)
        total_outstanding = 0.0

        return PaymentListResponse(
            data=[PaymentService._to_response(r) for r in rows],
            total=total,
            total_paid=round(total_paid, 2),
            total_outstanding=round(total_outstanding, 2),
        )

    @staticmethod
    async def get_by_id(tenant_id: str, payment_id: str, db: AsyncSession) -> PaymentResponse:
        q = (
            select(Payment)
            .options(selectinload(Payment.invoice))
            .where(Payment.business_id == tenant_id, Payment.id == payment_id)
        )
        result = await db.execute(q)
        payment = result.scalar_one_or_none()
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        return PaymentService._to_response(payment)

    @staticmethod
    async def customer_balance(tenant_id: str, customer_id: str, db: AsyncSession) -> CustomerBalanceResponse:
        # Fetch customer
        cust_res = await db.execute(select(Customer).where(Customer.id == customer_id, Customer.business_id == tenant_id))
        customer = cust_res.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        # Invoices for customer
        inv_q = select(Invoice).where(Invoice.business_id == tenant_id, Invoice.customer_id == customer_id, Invoice.status != InvoiceStatus.CANCELLED).order_by(Invoice.invoice_date.desc())
        inv_res = await db.execute(inv_q)
        invoices = inv_res.scalars().all()

        total_invoices = len(invoices)
        total_billed = sum(float(i.grand_total) for i in invoices)
        total_paid = sum(float(i.amount_paid) for i in invoices)
        total_outstanding = sum(float(i.amount_due) for i in invoices)
        overdue_amount = sum(float(i.amount_due) for i in invoices if i.status == InvoiceStatus.OVERDUE)
        last_payment_date = None
        # Find last payment date
        pay_q = select(func.max(Payment.payment_date)).where(Payment.business_id == tenant_id, Payment.customer_id == customer_id)
        last_res = await db.execute(pay_q)
        last_payment_date = last_res.scalar_one_or_none()

        invoice_list = [
            CustomerInvoiceSummary(
                invoice_id=str(i.id),
                invoice_number=i.invoice_number,
                invoice_date=i.invoice_date,
                due_date=i.due_date,
                status=i.status.value if hasattr(i.status, 'value') else i.status,
                grand_total=float(i.grand_total),
                amount_paid=float(i.amount_paid),
                amount_due=float(i.amount_due),
            )
            for i in invoices
        ]

        return CustomerBalanceResponse(
            customer_id=str(customer.id),
            customer_name=customer.name,
            phone=customer.phone,
            total_invoices=total_invoices,
            total_billed=round(total_billed, 2),
            total_paid=round(total_paid, 2),
            total_outstanding=round(total_outstanding, 2),
            overdue_amount=round(overdue_amount, 2),
            last_payment_date=last_payment_date,
            invoices=invoice_list,
        )

    @staticmethod
    def _to_response(payment: Payment) -> PaymentResponse:
        customer_name = payment.invoice.customer_name if payment.invoice else ""
        return PaymentResponse(
            id=str(payment.id),
            invoice_id=str(payment.invoice_id),
            customer_id=str(payment.customer_id) if payment.customer_id else None,
            customer_name=customer_name,
            amount=float(payment.amount),
            method=payment.method.value if hasattr(payment.method, 'value') else payment.method,
            reference=payment.reference,
            payment_date=payment.payment_date.isoformat() if payment.payment_date else None,
            notes=payment.notes,
            invoice_number=payment.invoice_number,
            invoice_total=float(payment.invoice_total),
            balance_before=float(payment.balance_before),
            balance_after=float(payment.balance_after),
            created_at=payment.created_at,
        )
