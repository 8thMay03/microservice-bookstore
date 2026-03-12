#!/usr/bin/env python3
"""
Seed sample data for BookStore microservices.
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
CATEGORY_SLUG_TO_ID = {
    "general": 1,
    "graphic-design": 2,
    "product-design": 3,
    "architecture": 4,
    "fine-arts": 5,
    "science": 6,
    "photography": 7,
}

SAMPLE_BOOKS = [
    {"title": "Letters from M/M (Paris)", "author": "M/M Paris", "price": 39, "category": "graphic-design",
     "image": "https://m.media-amazon.com/images/I/81fcH8Y-oqL._AC_UF894,1000_QL80_.jpg",
     "description": "A comprehensive survey of M/M Paris — the studio that redefined the boundaries between art and commercial graphic design.", "pages": 328, "year": 2023, "isbn": "978-0-500-02587-1"},
    {"title": "Daan Paans: Floating Signifiers", "author": "Daan Paans", "price": 29, "category": "photography",
     "image": "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=600&q=80",
     "description": "A journey through ambiguous images that resist easy categorization.", "pages": 224, "year": 2023, "isbn": "978-94-92852-45-1"},
    {"title": "Album Architectures, Maputo", "author": "Luís Loureiro", "price": 19, "category": "architecture",
     "image": "https://images.unsplash.com/photo-1486325212027-8081e485255e?w=600&q=80",
     "description": "An intimate visual record of Maputo's modernist built environment.", "pages": 192, "year": 2022, "isbn": "978-3-7757-5331-4"},
    {"title": "Aaron Rothman: The Sierra", "author": "Aaron Rothman", "price": 39, "category": "photography",
     "image": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=600&q=80",
     "description": "Vast, sublime, and meditative large-format photographs of the Sierra Nevada.", "pages": 256, "year": 2023, "isbn": "978-1-942185-89-2"},
    {"title": "Dieter Rams: The Complete Works", "author": "Klaus Klemp & Keiko Ueki-Polet", "price": 29, "category": "product-design",
     "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80",
     "description": "The definitive monograph on Dieter Rams and his ten principles of good design.", "pages": 480, "year": 2021, "isbn": "978-0-7148-7974-7"},
    {"title": "Yellow Nose Studio: INDERGARTEN", "author": "Yellow Nose Studio", "price": 19, "category": "graphic-design",
     "image": "https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=600&q=80",
     "description": "An experimental graphic design catalogue exploring childhood iconography.", "pages": 128, "year": 2023, "isbn": "978-0-0000-0000-6"},
    {"title": "Concrete Poetry: A World View", "author": "Mary Ellen Solt", "price": 45, "category": "fine-arts",
     "image": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=600&q=80",
     "description": "The most comprehensive anthology of international concrete poetry.", "pages": 272, "year": 2021, "isbn": "978-0-253-06124-5"},
    {"title": "Forms of Inquiry", "author": "Zak Kyes & Mark Owens", "price": 34, "category": "graphic-design",
     "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&q=80",
     "description": "How graphic design can function as critical inquiry.", "pages": 288, "year": 2022, "isbn": "978-1-907896-68-5"},
    {"title": "On Looking: Eleven Walks with Expert Eyes", "author": "Alexandra Horowitz", "price": 22, "category": "science",
     "image": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=600&q=80",
     "description": "A cognitive scientist invites eleven experts to walk the same block of New York City.", "pages": 320, "year": 2022, "isbn": "978-1-4516-5060-7"},
    {"title": "New Japanese Architecture", "author": "Botond Bognar", "price": 55, "category": "architecture",
     "image": "https://images.unsplash.com/photo-1480796927426-f609979314bd?w=600&q=80",
     "description": "A sweeping examination of the transformative decade in Japanese architecture.", "pages": 352, "year": 2020, "isbn": "978-0-8478-6752-5"},
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


def seed_catalog():
    print("1. Seeding catalog (categories)...")
    code = """
from catalog.models import Category
created = []
for name, slug in [
    ("General", "general"),
    ("Graphic Design", "graphic-design"),
    ("Product Design", "product-design"),
    ("Architecture", "architecture"),
    ("Fine Arts", "fine-arts"),
    ("Science", "science"),
    ("Photography", "photography"),
]:
    c, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name, "description": ""})
    created.append(c.slug)
print("Categories:", created)
"""
    return run_exec("catalog-service", code)


def isbn13_digits(isbn: str) -> str:
    """Strip dashes, keep 13 digits for ISBN-13."""
    return isbn.replace("-", "")[:13]


def seed_books():
    print("2. Seeding books...")
    books_data = []
    for b in SAMPLE_BOOKS:
        cat_id = CATEGORY_SLUG_TO_ID.get(b["category"], 1)
        books_data.append({
            "isbn": isbn13_digits(b["isbn"]),
            "title": b["title"],
            "author": b["author"],
            "price": b["price"],
            "description": b["description"],
            "cover_image": b["image"],
            "category_id": cat_id,
            "published_date": f"{b['year']}-01-01",
            "pages": b["pages"],
        })
    data_json = json.dumps(books_data)
    code = f"""
from books.models import Book, BookInventory
import json
data = json.loads('''{data_json}''')
for d in data:
    Book.objects.get_or_create(isbn=d["isbn"], defaults={{
        "title": d["title"], "author": d["author"], "price": d["price"],
        "description": d["description"], "cover_image": d["cover_image"],
        "category_id": d["category_id"], "published_date": d["published_date"],
        "language": "English", "pages": d["pages"], "is_active": True
    }})
for book in Book.objects.all():
    BookInventory.objects.get_or_create(book=book, defaults={{"stock_quantity": 50}})
print("Books:", Book.objects.count())
"""
    return run_exec("book-service", code)


def seed_admin():
    print("3. Creating admin account (admin@bookstore.com / " + DEFAULT_PASSWORD + ")...")
    code = """
from management.models import ManagerUser
u, created = ManagerUser.objects.get_or_create(
    email="admin@bookstore.com",
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
    print("4. Creating staff account (staff@bookstore.com / " + DEFAULT_PASSWORD + ")...")
    code = """
from staff.models import StaffMember
u, created = StaffMember.objects.get_or_create(
    email="staff@bookstore.com",
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
    print("BookStore Seed Data Script")
    print("=" * 50)
    print("Ensure Docker Compose is running: docker compose up -d")
    print()

    ok = True
    ok &= seed_catalog()
    ok &= seed_books()
    ok &= seed_admin()
    ok &= seed_staff()
    ok &= seed_customers()

    print()
    if ok:
        print("Done! Summary:")
        print("  - Admin:  admin@bookstore.com / " + DEFAULT_PASSWORD)
        print("  - Staff:  staff@bookstore.com / " + DEFAULT_PASSWORD)
        print("  - Users:  user1@example.com ... user10@example.com / " + DEFAULT_PASSWORD)
    else:
        print("Some steps failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
