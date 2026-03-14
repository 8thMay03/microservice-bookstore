from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="customer_name",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
    ]
