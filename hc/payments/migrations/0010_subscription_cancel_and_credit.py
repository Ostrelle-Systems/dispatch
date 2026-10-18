from __future__ import annotations

from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0009_alter_subscription_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="cancel_at_period_end",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="subscription",
            name="credit",
            field=models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=8),
        ),
    ]
