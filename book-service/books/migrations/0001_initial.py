import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=300)),
                ("author", models.CharField(max_length=200)),
                ("isbn", models.CharField(max_length=13, unique=True)),
                ("description", models.TextField(blank=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ("cover_image", models.URLField(blank=True)),
                ("category_id", models.IntegerField(help_text="FK to catalog-service Category")),
                ("published_date", models.DateField(blank=True, null=True)),
                ("language", models.CharField(default="English", max_length=50)),
                ("pages", models.PositiveIntegerField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "books", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="BookInventory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stock_quantity", models.PositiveIntegerField(default=0)),
                ("warehouse_location", models.CharField(blank=True, max_length=100)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("book", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="inventory", to="books.book")),
            ],
            options={"db_table": "book_inventory", "verbose_name_plural": "book inventories"},
        ),
    ]
