# routes/manager_closeout.py

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from weasyprint import HTML
import tempfile
from fastapi.templating import Jinja2Templates

from app.db.database import get_db
from app.auth.dependencies import get_current_user
from app.models.models import CashierSession, Sale, Return, Product, User, SaleItem
from schemas.manager_closeout import ZReportOut, SessionSummary, TopSeller
from app.utils.zreport_csv import generate_zreport_csv

router = APIRouter(prefix="/manager_closeout", tags=["Manager Closeout"])
templates = Jinja2Templates(directory="templates")


def filter_by_tenant(query, tenant_id):
    return query.filter_by(tenant_id=tenant_id)


@router.get("/zreport", response_model=ZReportOut)
def generate_z_report(
    report_date: date = Query(default=date.today()),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_dt = datetime.combine(report_date, datetime.min.time())
    end_dt = datetime.combine(report_date, datetime.max.time())

    tenant_id = current_user.tenant_id

    sales = (
        filter_by_tenant(db.query(Sale), tenant_id)
        .filter(Sale.timestamp.between(start_dt, end_dt))
        .all()
    )
    total_sales = sum([s.total_amount for s in sales])
    total_cash = sum([s.total_amount for s in sales if s.payment_type == "cash"])
    total_card = sum([s.total_amount for s in sales if s.payment_type == "card"])

    total_returns = (
        db.query(func.coalesce(func.sum(Return.quantity * Product.price), 0))
        .join(Product, Return.product_id == Product.id)
        .filter(
            Return.timestamp.between(start_dt, end_dt), Product.tenant_id == tenant_id
        )
        .scalar()
    )

    sessions = (
        db.query(CashierSession, User.username)
        .join(User, CashierSession.cashier_id == User.id)
        .filter(
            CashierSession.opened_at.between(start_dt, end_dt),
            CashierSession.tenant_id == tenant_id,
        )
        .all()
    )

    session_summaries = [
        SessionSummary(
            cashier_id=s.cashier_id,
            cashier_name=username,
            opening_cash=s.opening_cash,
            closing_cash=s.closing_cash,
            system_cash_total=s.system_cash_total,
            cash_difference=s.cash_difference,
            is_over_short=s.is_over_short,
            opened_at=s.opened_at,
            closed_at=s.closed_at,
        )
        for s, username in sessions
    ]

    top_products = (
        db.query(
            Product.id, Product.name, func.sum(SaleItem.quantity).label("units_sold")
        )
        .join(SaleItem, Product.id == SaleItem.product_id)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .filter(
            Sale.timestamp.between(start_dt, end_dt), Product.tenant_id == tenant_id
        )
        .group_by(Product.id, Product.name)
        .order_by(func.sum(SaleItem.quantity).desc())
        .limit(5)
        .all()
    )

    top_sellers = [
        TopSeller(product_id=p[0], name=p[1], units_sold=p[2]) for p in top_products
    ]

    return ZReportOut(
        date=report_date,
        total_sales=total_sales,
        total_cash=total_cash,
        total_card=total_card,
        total_returns=total_returns,
        sessions=session_summaries,
        top_sellers=top_sellers,
    )


@router.get("/zreport/export")
def export_zreport_csv(
    report_date: date = Query(default=date.today()),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = generate_z_report(report_date, db, current_user)

    csv_data = generate_zreport_csv(
        report.date,
        report.total_sales,
        report.total_cash,
        report.total_card,
        report.total_returns,
        report.sessions,
        report.top_sellers,
    )

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=zreport_{report_date}.csv"
        },
    )


@router.get("/zreport/pdf")
def export_zreport_pdf(
    request: Request,
    report_date: date = Query(default=date.today()),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = generate_z_report(report_date, db, current_user)

    html_content = templates.get_template("zreport.html").render(
        {
            "date": report.date,
            "total_sales": report.total_sales,
            "total_cash": report.total_cash,
            "total_card": report.total_card,
            "total_returns": report.total_returns,
            "sessions": report.sessions,
            "top_sellers": report.top_sellers,
        }
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        HTML(string=html_content).write_pdf(tmp.name)
        tmp.seek(0)
        pdf_bytes = tmp.read()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=zreport_{report_date}.pdf"},
    )
