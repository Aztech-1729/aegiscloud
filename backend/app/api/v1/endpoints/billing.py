from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.models import User, Subscription, PlanType, SubscriptionStatus
from app.schemas.schemas import CheckoutRequest, CheckoutResponse, SubscriptionResponse
from app.api.deps.auth import get_current_user

router = APIRouter()


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id).order_by(Subscription.created_at.desc())
    )
    subscription = result.scalars().first()

    if not subscription:
        return SubscriptionResponse(
            plan=PlanType.free,
            status="active",
            cancel_at_period_end=False,
        )

    return SubscriptionResponse(
        plan=subscription.plan,
        status=subscription.status.value,
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        cancel_at_period_end=subscription.cancel_at_period_end,
    )


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return CheckoutResponse(
        checkout_url=f"https://aegiscloud.lemonsqueezy.com/checkout/mock/{data.plan.value}",
        session_id=f"cs_mock_{data.plan.value}",
    )


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id).order_by(Subscription.created_at.desc())
    )
    subscription = result.scalars().first()

    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription")

    subscription.cancel_at_period_end = True
    subscription.status = SubscriptionStatus.cancelled
    return {"message": "Subscription will be cancelled at the end of the billing period"}
