from __future__ import annotations

from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.contrib.auth.models import User
from django.db import models, transaction

# Monthly price per plan, in USD.
PLAN_PRICES = {
    "P20": Decimal("20.00"),
    "P80": Decimal("80.00"),
    "Y192": Decimal("16.00"),
    "Y768": Decimal("64.00"),
}

BILLING_CYCLE_DAYS = 30
RENEW_NOTICE_DAYS = 7


class Subscription(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    customer_id = models.CharField(max_length=36, blank=True)
    payment_method_token = models.CharField(max_length=35, blank=True)
    subscription_id = models.CharField(max_length=10, blank=True)
    plan_id = models.CharField(max_length=10, blank=True)
    plan_name = models.CharField(max_length=50, blank=True)
    address_id = models.CharField(max_length=2, blank=True)
    send_invoices = models.BooleanField(default=True)
    invoice_email = models.EmailField(blank=True)
    next_billing_date = models.DateField(null=True, blank=True)
    renew_notice_date = models.DateField(null=True, blank=True)
    setup_date = models.DateField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    credit = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0"))

    def monthly_price(self) -> Decimal:
        return PLAN_PRICES.get(self.plan_id, Decimal("0"))

    def days_left(self, today: date) -> int:
        if not self.next_billing_date:
            return 0
        return max((self.next_billing_date - today).days, 0)

    def unused_value(self, today: date) -> Decimal:
        """Value of the days already paid for but not used yet."""
        fraction = Decimal(self.days_left(today)) / Decimal(BILLING_CYCLE_DAYS)
        value = self.monthly_price() * fraction
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @transaction.atomic
    def cancel(self, today: date | None = None, at_period_end: bool = True) -> Decimal:
        """Cancel the subscription and return the amount refunded."""
        today = today or date.today()
        if at_period_end:
            self.cancel_at_period_end = True
            self.renew_notice_date = None
            self.save()
            return Decimal("0")

        refund = self.unused_value(today) + self.credit
        self.plan_id = ""
        self.plan_name = ""
        self.subscription_id = ""
        self.next_billing_date = None
        self.renew_notice_date = None
        self.cancel_at_period_end = False
        self.credit = Decimal("0")
        self.save()
        return refund

    @transaction.atomic
    def change_plan(self, plan_id: str, plan_name: str, today: date | None = None) -> Decimal:
        """Switch plans now and return the amount to charge today.

        Upgrades are charged the prorated difference. Downgrades leave the
        unused value as credit for the next invoice.
        """
        if plan_id not in PLAN_PRICES:
            raise ValueError(f"unknown plan: {plan_id}")
        today = today or date.today()

        old_unused = self.unused_value(today)
        self.plan_id = plan_id
        self.plan_name = plan_name
        new_cost = self.unused_value(today)

        charge = new_cost - old_unused - self.credit
        if charge < 0:
            self.credit = -charge
            charge = Decimal("0")
        else:
            self.credit = Decimal("0")

        self.cancel_at_period_end = False
        if not self.next_billing_date:
            self.next_billing_date = today + timedelta(days=BILLING_CYCLE_DAYS)
        self.renew_notice_date = self.next_billing_date - timedelta(days=RENEW_NOTICE_DAYS)
        self.save()
        return charge
