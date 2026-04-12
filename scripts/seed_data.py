#!/usr/bin/env python3
"""
Seed sample data for Ecommerce microservices.
Requires: Docker Compose services running (docker compose up -d)
Run from project root: python scripts/seed_data.py
"""
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PASSWORD = "Password123!"

# Category slug -> ID mapping (after seed, IDs are 1-based in creation order)
# Updated for ecommerce with subcategories (parent IDs are the root categories)
CATEGORY_SLUG_TO_ID = {
    "books": 1,
    "fiction": 2,
    "non-fiction": 3,
    "science": 4,
    "history": 5,
    "technology-books": 6,
    "electronics": 7,
    "phones-tablets": 8,
    "laptops-computers": 9,
    "audio": 10,
    "cameras": 11,
    "clothing": 12,
    "mens-clothing": 13,
    "womens-clothing": 14,
    "kids-clothing": 15,
    "shoes": 16,
    "food-beverages": 17,
    "snacks": 18,
    "beverages": 19,
    "organic": 20,
    "home-garden": 21,
    "furniture": 22,
    "kitchen": 23,
    "decor": 24,
    "sports-outdoors": 25,
    "fitness": 26,
    "outdoor": 27,
    "team-sports": 28,
}

SAMPLE_PRODUCTS = [
    # Books
    {"title": "Letters from M/M (Paris)", "brand": "M/M Paris", "price": 39, "category": "fiction",
     "product_type": "BOOK", "image": "https://m.media-amazon.com/images/I/81fcH8Y-oqL._AC_UF894,1000_QL80_.jpg",
     "description": "A comprehensive survey of M/M Paris — the studio that redefined the boundaries between art and commercial graphic design.",
     "sku": "BK-9780500025871", "attributes": {"author": "M/M Paris", "pages": 328, "isbn": "978-0-500-02587-1", "language": "English", "published_date": "2023-01-01"}},
    {"title": "Clean Code", "brand": "Robert C. Martin", "price": 34, "category": "technology-books",
     "product_type": "BOOK", "image": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=600&q=80",
     "description": "A Handbook of Agile Software Craftsmanship. The definitive guide to writing clean, maintainable code.",
     "sku": "BK-9780132350884", "attributes": {"author": "Robert C. Martin", "pages": 464, "isbn": "978-0-13-235088-4", "language": "English", "published_date": "2008-08-01"}},
    {"title": "Dieter Rams: The Complete Works", "brand": "Klaus Klemp", "price": 29, "category": "non-fiction",
     "product_type": "BOOK", "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80",
     "description": "The definitive monograph on Dieter Rams and his ten principles of good design.",
     "sku": "BK-9780714879747", "attributes": {"author": "Klaus Klemp & Keiko Ueki-Polet", "pages": 480, "isbn": "978-0-7148-7974-7", "language": "English", "published_date": "2021-01-01"}},

    # Electronics
    {"title": "Sony WH-1000XM5 Wireless Headphones", "brand": "Sony", "price": 349, "category": "audio",
     "product_type": "ELECTRONICS", "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80",
     "description": "Industry-leading noise canceling headphones with Auto NC Optimizer and crystal clear hands-free calling.",
     "sku": "EL-SONYWH1000XM5", "attributes": {"warranty": "12 months", "connectivity": "Bluetooth 5.2", "battery_life": "30 hours", "color": "Black"}},
    {"title": "MacBook Air M3 15-inch", "brand": "Apple", "price": 1299, "category": "laptops-computers",
     "product_type": "ELECTRONICS", "image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&q=80",
     "description": "Supercharged by the M3 chip. Ultra-thin design. Strikingly brilliant display. Up to 18 hours battery life.",
     "sku": "EL-APPMBAM3-15", "attributes": {"warranty": "12 months", "specs": {"cpu": "Apple M3", "ram": "8GB", "storage": "256GB SSD"}, "color": "Midnight"}},

    # Clothing
    {"title": "Classic Fit Oxford Shirt", "brand": "Ralph Lauren", "price": 89, "category": "mens-clothing",
     "product_type": "CLOTHING", "image": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&q=80",
     "description": "Crafted from breathable cotton oxford cloth in a polished classic fit. A timeless wardrobe essential.",
     "sku": "CL-RL-OXFORD-M01", "attributes": {"sizes": ["S", "M", "L", "XL"], "color": "White", "material": "100% Cotton"}},
    {"title": "Women's Premium Running Shoes", "brand": "Nike", "price": 129, "category": "shoes",
     "product_type": "CLOTHING", "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80",
     "description": "Responsive ZoomX foam and a breathable Flyknit upper for your fastest runs.",
     "sku": "CL-NK-RUNSH-W01", "attributes": {"sizes": ["6", "7", "8", "9", "10"], "color": "Hot Pink", "material": "Flyknit"}},

    # Food
    {"title": "Organic Matcha Green Tea Powder", "brand": "Jade Leaf", "price": 24, "category": "organic",
     "product_type": "FOOD", "image": "https://images.unsplash.com/photo-1563822249366-3efb23b8e0c9?w=600&q=80",
     "description": "Authentic Japanese organic matcha. USDA Certified Organic and perfect for lattes, smoothies, and baking.",
     "sku": "FD-JL-MATCHA100", "attributes": {"weight": "100g", "origin": "Uji, Japan", "ingredients": ["organic matcha green tea"]}},

    # Home
    {"title": "Scandinavian Oak Coffee Table", "brand": "IKEA", "price": 199, "category": "furniture",
     "product_type": "HOME", "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&q=80",
     "description": "Minimalist oak coffee table with clean lines and natural finish. Perfect for modern living spaces.",
     "sku": "HM-IK-OAKCTBL01", "attributes": {"dimensions": "120x60x45cm", "material": "Solid Oak", "weight": "15kg"}},

    # Sports
    {"title": "Adjustable Dumbbell Set 20kg", "brand": "Bowflex", "price": 179, "category": "fitness",
     "product_type": "SPORTS", "image": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600&q=80",
     "description": "Replace 15 sets of weights with one compact pair. Adjustable from 2kg to 20kg in 2.5kg increments.",
     "sku": "SP-BF-DUMBBL20", "attributes": {"weight_range": "2-20kg", "material": "Steel with rubber grip"}},
]

CUSTOMERS = [
    {"email": "user1@example.com", "first_name": "Alice", "last_name": "Nguyen", "phone": "0901234567", "address": "123 Hanoi"},
    {"email": "user2@example.com", "first_name": "Bob", "last_name": "Tran", "phone": "0912345678", "address": "456 Ho Chi Minh"},
    {"email": "user3@example.com", "first_name": "Carol", "last_name": "Le", "phone": "0923456789", "address": "789 Da Nang"},
    {"email": "user4@example.com", "first_name": "David", "last_name": "Pham", "phone": "0934567890", "address": "101 Can Tho"},
    {"email": "user5@example.com", "first_name": "Eve", "last_name": "Hoang", "phone": "0945678901", "address": "202 Hue"},
    {"email": "user6@example.com", "first_name": "Frank", "last_name": "Vo", "phone": "0956789012", "address": "303 Nha Trang"},
    {"email": "user7@example.com", "first_name": "Grace", "last_name": "Dang", "phone": "0967890123", "address": "404 Hai Phong"},
    {"email": "user8@example.com", "first_name": "Henry", "last_name": "Bui", "phone": "0978901234", "address": "505 Vung Tau"},
    {"email": "user9@example.com", "first_name": "Ivy", "last_name": "Do", "phone": "0989012345", "address": "606 Dalat"},
    {"email": "user10@example.com", "first_name": "Jack", "last_name": "Ly", "phone": "0990123456", "address": "707 Quy Nhon"},
]


def run_exec(service: str, cmd: str) -> bool:
    """Run command in Docker Compose service. Returns True on success."""
    full_cmd = [
        "docker", "compose", "exec", "-T", service,
        "python", "manage.py", "shell", "-c", cmd
    ]
    try:
        result = subprocess.run(
            full_cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            print(f"  Error: {result.stderr or result.stdout}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print("  Timeout")
        return False
    except FileNotFoundError:
        print("  docker compose not found. Ensure Docker is running.")
        return False
    except Exception as e:
        print(f"  Exception: {e}")
        return False


def seed_products():
    print("2. Seeding products...")
    products_data = []
    for p in SAMPLE_PRODUCTS:
        cat_id = CATEGORY_SLUG_TO_ID.get(p["category"], 1)
        products_data.append({
            "sku": p["sku"],
            "title": p["title"],
            "brand": p["brand"],
            "price": p["price"],
            "description": p["description"],
            "cover_image": p["image"],
            "category_id": cat_id,
            "product_type": p["product_type"],
            "attributes": p["attributes"],
        })
    data_json = json.dumps(products_data)
    code = f"""
from products.models import Product, ProductInventory
import json
data = json.loads('''{data_json}''')
for d in data:
    Product.objects.get_or_create(sku=d["sku"], defaults={{
        "title": d["title"], "brand": d["brand"], "price": d["price"],
        "description": d["description"], "cover_image": d["cover_image"],
        "category_id": d["category_id"], "product_type": d["product_type"],
        "attributes": d["attributes"], "is_active": True
    }})
for product in Product.objects.all():
    ProductInventory.objects.get_or_create(product=product, defaults={{"stock_quantity": 50}})
print("Products:", Product.objects.count())
"""
    return run_exec("product-service", code)


def seed_admin():
    print("3. Creating admin account (admin@store.com / " + DEFAULT_PASSWORD + ")...")
    code = """
from management.models import ManagerUser
u, created = ManagerUser.objects.get_or_create(
    email="admin@store.com",
    defaults={"first_name": "Admin", "last_name": "Manager", "is_active": True}
)
if created:
    u.set_password("Password123!")
    u.save()
    print("Admin created")
else:
    print("Admin already exists")
"""
    return run_exec("manager-service", code)


def seed_staff():
    print("4. Creating staff account (staff@store.com / " + DEFAULT_PASSWORD + ")...")
    code = """
from staff.models import StaffMember
u, created = StaffMember.objects.get_or_create(
    email="staff@store.com",
    defaults={"first_name": "Staff", "last_name": "User", "role": "SALES", "is_admin": True, "is_active": True}
)
if created:
    u.set_password("Password123!")
    u.save()
    print("Staff created")
else:
    print("Staff already exists")
"""
    return run_exec("staff-service", code)


def seed_customers():
    print("5. Creating 10 customer accounts (user1@example.com ... user10@example.com / " + DEFAULT_PASSWORD + ")...")
    customers_json = json.dumps(CUSTOMERS)
    code = f"""
from customers.models import Customer
import json
data = json.loads('''{customers_json}''')
for d in data:
    u, created = Customer.objects.get_or_create(
        email=d["email"],
        defaults={{"first_name": d["first_name"], "last_name": d["last_name"], "phone": d.get("phone", ""), "address": d.get("address", ""), "is_active": True}}
    )
    if created:
        u.set_password("Password123!")
        u.save()
print("Customers:", Customer.objects.count())
"""
    return run_exec("customer-service", code)


def main():
    print("=" * 50)
    print("Ecommerce Store Seed Data Script")
    print("=" * 50)
    print("Ensure Docker Compose is running: docker compose up -d")
    print()

    ok = True
    ok &= seed_products()
    ok &= seed_admin()
    ok &= seed_staff()
    ok &= seed_customers()

    print()
    if ok:
        print("Done! Summary:")
        print("  - Admin:  admin@store.com / " + DEFAULT_PASSWORD)
        print("  - Staff:  staff@store.com / " + DEFAULT_PASSWORD)
        print("  - Users:  user1@example.com ... user10@example.com / " + DEFAULT_PASSWORD)
    else:
        print("Some steps failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
