from __future__ import annotations

from uuid import UUID

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from hc.payments.models import PLAN_PRICES, Subscription


def pricing(request: HttpRequest, code: UUID | None = None) -> HttpResponse:
    # FIXME: placeholder for a public "Pricing" page
    return HttpResponse("not implemented")


@login_required
def billing(request: HttpRequest) -> HttpResponse:
    # FIXME: placeholder for a "Billing Settings" page
    return HttpResponse("not implemented")


@login_required
@require_POST
def cancel_subscription(request: HttpRequest) -> HttpResponse:
    sub = Subscription.objects.filter(user=request.user).first()
    if sub is None or not sub.plan_id:
        return HttpResponseBadRequest("no active subscription")

    immediately = request.POST.get("immediately") == "1"
    refund = sub.cancel(at_period_end=not immediately)
    if immediately:
        messages.success(request, f"Subscription cancelled. ${refund} will be refunded.")
    else:
        messages.success(request, "Subscription will end at the end of this billing period.")
    return redirect("hc-billing")


@login_required
@require_POST
def change_plan(request: HttpRequest) -> HttpResponse:
    plan_id = request.POST.get("plan_id", "")
    if plan_id not in PLAN_PRICES:
        return HttpResponseBadRequest("unknown plan")

    sub, _ = Subscription.objects.get_or_create(user=request.user)
    charge = sub.change_plan(plan_id, request.POST.get("plan_name", plan_id))
    if charge:
        messages.success(request, f"Plan changed. ${charge} was charged today.")
    else:
        messages.success(request, f"Plan changed. ${sub.credit} credit added to your account.")
    return redirect("hc-billing")
