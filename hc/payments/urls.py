from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    path("projects/<uuid:code>/pricing/", views.pricing, name="hc-p-pricing"),
    path("pricing/", views.pricing, name="hc-pricing"),
    path("accounts/profile/billing/", views.billing, name="hc-billing"),
    path("accounts/profile/billing/cancel/", views.cancel_subscription, name="hc-cancel-subscription"),
    path("accounts/profile/billing/change-plan/", views.change_plan, name="hc-change-plan"),
]
