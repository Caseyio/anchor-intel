from app.db.database import SessionLocal
from app.models.models import Sale

# Start DB session
db = SessionLocal()

try:
    # Fetch sales with missing payment_type
    missing_sales = db.query(Sale).filter(Sale.payment_type == None).all()

    print(f"Found {len(missing_sales)} sales with missing payment_type.")

    for sale in missing_sales:
        sale.payment_type = "cash"  # or use "card" depending on your default
        print(f"Updated sale ID {sale.id} with payment_type = 'cash'")

    db.commit()
    print("✅ Payment type migration complete.")

except Exception as e:
    db.rollback()
    print(f"❌ Error during migration: {e}")

finally:
    db.close()
