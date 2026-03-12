# Seed Data Script

Khởi tạo dữ liệu mẫu cho BookStore.

## Yêu cầu

- Docker Compose đang chạy: `docker compose up -d`

## Chạy

Từ thư mục gốc project:

```bash
python scripts/seed_data.py
```

Hoặc trên Windows:

```powershell
python scripts/seed_data.py
```

## Dữ liệu được tạo

| Loại | Chi tiết |
|------|----------|
| **Categories** | 7 danh mục: General, Graphic Design, Product Design, Architecture, Fine Arts, Science, Photography |
| **Books** | 10 sách mẫu với ảnh, mô tả, giá |
| **Admin** | admin@bookstore.com / Password123! |
| **Staff** | staff@bookstore.com / Password123! |
| **Customers** | user1@example.com ... user10@example.com / Password123! |
