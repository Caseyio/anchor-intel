# seed_sales.py
import json
import requests

import os

BASE_DIR = os.path.dirname(__file__)
with open(os.path.join(BASE_DIR, "sales_seed_data.json")) as f:
    sales = json.load(f)

for i, sale in enumerate(sales, start=1):
    res = requests.post("http://localhost:8000/api/sales/sales/checkout", json=sale)
    if res.status_code == 200:
        print(f"✅ Sale {i} seeded successfully")
    else:
        print(f"❌ Sale {i} failed: {res.status_code}")
        print(res.text)
