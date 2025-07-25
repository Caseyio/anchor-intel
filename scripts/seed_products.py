import requests

# ✅ Correct base URL for use inside Docker
BASE_URL = "http://backend:8000"

# 👇 Replace with your actual admin login credentials
LOGIN_PAYLOAD = {"username": "admin", "password": "123"}

PRODUCTS = [
    {
        "id": 1,
        "name": "Bud Light 12pk",
        "sku": "BL-12PK-001",
        "price": 14.99,
        "category": "beer",
        "stock_quantity": 120,
    },
    {
        "id": 2,
        "name": "White Claw Variety Pack",
        "sku": "WC-VAR-002",
        "price": 17.99,
        "category": "beer",
        "stock_quantity": 95,
    },
    {
        "id": 3,
        "name": "Heineken 6pk",
        "sku": "HEI-6PK-003",
        "price": 10.99,
        "category": "beer",
        "stock_quantity": 80,
    },
    {
        "id": 4,
        "name": "Tito's Handmade Vodka",
        "sku": "TITO-750ML-004",
        "price": 19.49,
        "category": "liquor",
        "stock_quantity": 60,
    },
    {
        "id": 5,
        "name": "Bacardi Gold Rum",
        "sku": "BAC-GLD-005",
        "price": 18.49,
        "category": "liquor",
        "stock_quantity": 65,
    },
    {
        "id": 6,
        "name": "Josh Cabernet Sauvignon",
        "sku": "JOSH-CAB-006",
        "price": 13.99,
        "category": "wine",
        "stock_quantity": 85,
    },
    {
        "id": 7,
        "name": "La Marca Prosecco",
        "sku": "LA-PROS-007",
        "price": 15.99,
        "category": "wine",
        "stock_quantity": 70,
    },
    {
        "id": 8,
        "name": "Kendall-Jackson Chardonnay",
        "sku": "KJ-CHARD-008",
        "price": 12.99,
        "category": "wine",
        "stock_quantity": 90,
    },
    {
        "id": 9,
        "name": "Jameson Irish Whiskey",
        "sku": "JMSN-750ML-009",
        "price": 22.49,
        "category": "liquor",
        "stock_quantity": 55,
    },
    {
        "id": 10,
        "name": "Corona Extra 12pk",
        "sku": "COR-12PK-010",
        "price": 15.49,
        "category": "beer",
        "stock_quantity": 75,
    },
]


def get_token():
    response = requests.post(f"{BASE_URL}/api/users/login", json=LOGIN_PAYLOAD)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("❌ Failed to authenticate:", response.status_code, response.text)
        return None


def seed_products(token):
    headers = {"Authorization": f"Bearer {token}"}
    for product in PRODUCTS:
        res = requests.post(
            f"{BASE_URL}/api/products/products/", json=product, headers=headers
        )
        if res.status_code == 200:
            print(f"✅ Seeded: {product['name']}")
        else:
            print(f"❌ Failed: {product['name']} — {res.status_code} {res.text}")


if __name__ == "__main__":
    token = get_token()
    if token:
        seed_products(token)
