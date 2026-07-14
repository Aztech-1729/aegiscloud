"""Billing endpoints - Lemon Squeezy integration"""
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.db.session import get_db
from app.models.models import User, Subscription, PlanType, SubscriptionStatus
from app.api.deps.auth import get_current_user
from app.services.lemonsqueezy_service import lemon_squeezy_service
from app.schemas.schemas import (
    CheckoutRequest,
    CheckoutResponse,
    SubscriptionResponse,
)
from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's subscription"""
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id
        ).order_by(Subscription.created_at.desc())
    )

    subscription = result.scalar_one_or_none()

    if not subscription:
        return SubscriptionResponse(
            plan=PlanType.free,
            status="active",
            current_period_start=None,
            current_period_end=None,
            cancel_at_period_end=False
        )

    return SubscriptionResponse(
        plan=subscription.plan,
        status=subscription.status.value,
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        cancel_at_period_end=subscription.cancel_at_period_end
    )


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user)
):
    """Create Lemon Squeezy checkout session"""
    try:
        checkout = await lemon_squeezy_service.create_checkout_session(
            user_email=current_user.email,
            plan=data.plan.value,
            billing_interval=data.interval,
            success_url=f"{settings.FRONTEND_URL}/dashboard/billing?success=true",
            cancel_url=f"{settings.FRONTEND_URL}/dashboard/billing?cancelled=true"
        )

        return CheckoutResponse(
            checkout_url=checkout["checkout_url"],
            session_id=checkout["session_id"]
        )

    except Exception as e:
        logger.error(f"Checkout creation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create checkout: {str(e)}"
        )


@router.get("/portal")
async def get_customer_portal(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get customer portal URL for self-service"""
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == SubscriptionStatus.active.value
        )
    )

    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.lemon_squeezy_customer_id:
        raise HTTPException(
            status_code=404,
            detail="No active subscription found"
        )

    portal_url = await lemon_squeezy_service.get_customer_portal_url(
        subscription.lemon_squeezy_customer_id
    )

    return {"portal_url": portal_url}


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel subscription (at period end)"""
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == SubscriptionStatus.active.value
        )
    )

    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="No active subscription found"
        )

    if not subscription.lemon_squeezy_subscription_id:
        raise HTTPException(
            status_code=400,
            detail="Subscription not found in Lemon Squeezy"
        )

    try:
        await lemon_squeezy_service.cancel_subscription(
            subscription.lemon_squeezy_subscription_id
        )

        subscription.cancel_at_period_end = True
        await db.commit()

        return {
            "message": "Subscription will be cancelled at the end of the current period",
            "cancel_at": subscription.current_period_end.isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.get("/payments")
async def get_payment_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's payment history"""
    from app.models.models import Payment

    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    payments = result.scalars().all()

    return {
        "payments": [
            {
                "id": p.id,
                "amount": p.amount,
                "currency": p.currency,
                "status": p.status,
                "description": p.description,
                "created_at": p.created_at.isoformat()
            }
            for p in payments
        ],
        "total": len(payments)
    }


@router.get("/plans")
async def get_available_plans():
    """Get available subscription plans"""
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "currency": "USD",
                "interval": "month",
                "features": [
                    "Up to 2 devices",
                    "Basic monitoring",
                    "5 AI queries per day",
                    "Community support"
                ]
            },
            {
                "id": "pro",
                "name": "Pro",
                "price_monthly": 900,
                "price_yearly": 9000,
                "currency": "USD",
                "features": [
                    "Up to 10 devices",
                    "Advanced monitoring",
                    "Unlimited AI queries",
                    "Priority support",
                    "Device groups",
                    "Custom skills"
                ]
            },
            {
                "id": "business",
                "name": "Business",
                "price_monthly": 2900,
                "price_yearly": 29000,
                "currency": "USD",
                "features": [
                    "Up to 50 devices",
                    "Everything in Pro",
                    "Team collaboration",
                    "API access",
                    "Audit logs",
                    "SSO integration",
                    "Dedicated support"
                ]
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price": "Custom",
                "currency": "USD",
                "features": [
                    "Unlimited devices",
                    "Everything in Business",
                    "Custom integrations",
                    "SLA guarantee",
                    "Dedicated account manager",
                    "On-premise deployment option",
                    "24/7 phone support"
                ]
            }
        ]
    }


@router.post("/webhook")
async def lemonsqueezy_webhook(
    request: Request,
    x_signature: str = Header(None)
):
    """Handle Lemon Squeezy webhooks"""
    payload = await request.body()

    is_valid = await lemon_squeezy_service.verify_webhook_signature(
        payload,
        x_signature or ""
    )

    if not is_valid:
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        import json
        event = json.loads(payload)
    except Exception as e:
        logger.error(f"Failed to parse webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")

    try:
        await lemon_squeezy_service.handle_webhook(event)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook handling failed: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")