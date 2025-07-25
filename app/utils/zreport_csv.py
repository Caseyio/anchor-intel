import csv
from io import StringIO
from typing import List
from datetime import date
from decimal import Decimal

from schemas.manager_closeout import SessionSummary, TopSeller


def generate_zreport_csv(
    report_date: date,
    total_sales: Decimal,
    total_cash: Decimal,
    total_card: Decimal,
    total_returns: Decimal,
    sessions: List[SessionSummary],
    top_sellers: List[TopSeller],
) -> str:
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["Z-Report Summary"])
    writer.writerow(["Date", report_date])
    writer.writerow(["Total Sales", f"${total_sales:.2f}"])
    writer.writerow(["Total Cash", f"${total_cash:.2f}"])
    writer.writerow(["Total Card", f"${total_card:.2f}"])
    writer.writerow(["Total Returns", f"${total_returns:.2f}"])
    writer.writerow([])

    writer.writerow(["Cashier Sessions"])
    writer.writerow(
        [
            "Cashier ID",
            "Cashier Name",
            "Opened At",
            "Closed At",
            "Opening Cash",
            "Closing Cash",
            "System Cash Total",
            "Difference",
            "Over/Short",
        ]
    )
    for s in sessions:
        writer.writerow(
            [
                s.cashier_id,
                s.cashier_name,
                s.opened_at,
                s.closed_at,
                f"${s.opening_cash:.2f}",
                f"${s.closing_cash:.2f}" if s.closing_cash else "",
                f"${s.system_cash_total:.2f}" if s.system_cash_total else "",
                f"${s.cash_difference:.2f}" if s.cash_difference else "",
                "YES" if s.is_over_short else "NO",
            ]
        )

    writer.writerow([])

    writer.writerow(["Top Sellers"])
    writer.writerow(["Product ID", "Name", "Units Sold"])
    for p in top_sellers:
        writer.writerow([p.product_id, p.name, p.units_sold])

    return output.getvalue()
