"""Lemon Squeezy Service - Payment processing for Aegis Cloud"""
import os
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import httpx
from lemonsqueezy import LemonSqueezy

from app.core.config import settings
from app.core.logging import get_logger
from app.models.models import Subscription, Payment, PlanType, SubscriptionStatus

logger = get_logger(__name__)


class LemonSqueezyService:
    """Handle all Lemon Squeezy operations"""
    
    def __init__(self):
        self.api_key = settings.LEMONSQUEEZY_API_KEY
        self.store_id = settings.LEMONSQUEEZY_STORE_ID
        self.webhook_secret = settings.LEMONSQUEEZY_WEBHOOK_SECRET
        self._client = None
        
        self.products = {
            "pro_monthly": settings.LEMONSQUEEZY_PRO_MONTHLY_ID,
            "pro_yearly": settings.LEMONSQUEEZY_PRO_YEARLY_ID,
            "business_monthly": settings.LEMONSQUEEZY_BUSINESS_MONTHLY_ID,
            "business_yearly": settings.LEMONSQUEEZY_BUSINESS_YEARLY_ID,
        }
    
    @property
    def client(self):
        if self._client is None:
            if not self.api_key:
                raise ValueError("LEMONSQUEEZY_API_KEY is not configured")
            self._client = LemonSqueezy(api_key=self.api_key)
        return self._client
    
    async def create_checkout_session(
        self,
        user_email: str,
        plan: str,
        billing_interval: str = "month",
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a checkout session for subscription"""
        
        # Map plan to product ID
        product_key = f"{plan}_{billing_interval}"
        variant_id = self.products.get(product_key)
        
        if not variant_id:
            raise ValueError(f"Invalid plan: {product_key}")
        
        try:
            # Create checkout
            checkout = await self.client.checkouts.create(
                store_id=self.store_id,
                variant_id=variant_id,
                product_options={
                    "enabled": ["subscription"],
                },
                checkout_data={
                    "email": user_email,
                    "custom": {
                        "user_email": user_email
                    }
                },
                expires_at=(datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
            )
            
            return {
                "checkout_url": checkout.data.attributes.url,
                "checkout_id": checkout.data.id,
                "session_id": checkout.data.id
            }
            
        except Exception as e:
            logger.error(f"Lemon Squeezy checkout creation failed: {e}")
            raise
    
    async def create_one_time_checkout(
        self,
        user_email: str,
        variant_id: str,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create checkout for one-time payments"""
        
        try:
            checkout = await self.client.checkouts.create(
                store_id=self.store_id,
                variant_id=variant_id,
                checkout_data={
                    "email": user_email,
                    "custom": {
                        "user_email": user_email
                    }
                }
            )
            
            return {
                "checkout_url": checkout.data.attributes.url,
                "checkout_id": checkout.data.id
            }
            
        except Exception as e:
            logger.error(f"Lemon Squeezy checkout creation failed: {e}")
            raise
    
    async def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str
    ) -> bool:
        """Verify Lemon Squeezy webhook signature"""
        import hmac
        import hashlib
        
        computed_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(computed_signature, signature)
    
    async def handle_webhook(self, event: Dict[str, Any]) -> None:
        """Handle Lemon Squeezy webhook events"""
        
        event_type = event.get("meta", {}).get("event_name")
        
        logger.info(f"Lemon Squeezy webhook received: {event_type}")
        
        if event_type == "subscription_created":
            await self._handle_subscription_created(event)
        
        elif event_type == "subscription_updated":
            await self._handle_subscription_updated(event)
        
        elif event_type == "subscription_cancelled":
            await self._handle_subscription_cancelled(event)
        
        elif event_type == "subscription_resumed":
            await self._handle_subscription_resumed(event)
        
        elif event_type == "order_created":
            await self._handle_order_created(event)
        
        elif event_type == "payment_success":
            await self._handle_payment_success(event)
        
        elif event_type == "payment_failed":
            await self._handle_payment_failed(event)
    
    async def _handle_subscription_created(self, event: Dict[str, Any]) -> None:
        """Handle new subscription creation"""
        subscription_data = event.get("data", {}).get("attributes", {})
        custom_data = event.get("meta", {}).get("custom_data", {})
        
        user_email = custom_data.get("user_email")
        if not user_email:
            logger.error("No user_email in webhook custom_data")
            return
        
        # Create subscription record
        from app.db.session import async_session_factory
        from sqlalchemy import select
        from app.models.models import User
        
        async with async_session_factory() as db:
            # Find user
            result = await db.execute(
                select(User).where(User.email == user_email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error(f"User not found: {user_email}")
                return
            
            # Determine plan from variant_id
            variant_id = subscription_data.get("variant_id")
            plan = self._get_plan_from_variant(variant_id)
            
            # Create subscription
            subscription = Subscription(
                user_id=user.id,
                plan=plan,
                status=SubscriptionStatus.active,
                lemon_squeezy_subscription_id=subscription_data.get("id"),
                current_period_start=datetime.fromisoformat(
                    subscription_data.get("created_at")
                ),
                current_period_end=datetime.fromisoformat(
                    subscription_data.get("renews_at")
                ),
                cancel_at_period_end=False
            )
            
            db.add(subscription)
            
            # Update user plan
            user.plan = plan
            
            await db.commit()
            logger.info(f"Subscription created for user {user_email}: {plan}")
    
    async def _handle_subscription_updated(self, event: Dict[str, Any]) -> None:
        """Handle subscription updates"""
        subscription_data = event.get("data", {}).get("attributes", {})
        subscription_id = subscription_data.get("id")
        
        from app.db.session import async_session_factory
        from sqlalchemy import select
        
        async with async_session_factory() as db:
            result = await db.execute(
                select(Subscription).where(
                    Subscription.lemon_squeezy_subscription_id == subscription_id
                )
            )
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                logger.error(f"Subscription not found: {subscription_id}")
                return
            
            # Update status
            status = subscription_data.get("status")
            subscription.status = self._map_ls_status(status)
            
            # Update dates
            if subscription_data.get("renews_at"):
                subscription.current_period_end = datetime.fromisoformat(
                    subscription_data.get("renews_at")
                )
            
            await db.commit()
            logger.info(f"Subscription updated: {subscription_id}")
    
    async def _handle_subscription_cancelled(self, event: Dict[str, Any]) -> None:
        """Handle subscription cancellation"""
        subscription_data = event.get("data", {}).get("attributes", {})
        subscription_id = subscription_data.get("id")
        
        from app.db.session import async_session_factory
        from sqlalchemy import select
        
        async with async_session_factory() as db:
            result = await db.execute(
                select(Subscription).where(
                    Subscription.lemon_squeezy_subscription_id == subscription_id
                )
            )
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                logger.error(f"Subscription not found: {subscription_id}")
                return
            
            subscription.cancel_at_period_end = True
            subscription.status = SubscriptionStatus.cancelled
            
            await db.commit()
            logger.info(f"Subscription cancelled: {subscription_id}")
    
    async def _handle_subscription_resumed(self, event: Dict[str, Any]) -> None:
        """Handle subscription resumption"""
        subscription_data = event.get("data", {}).get("attributes", {})
        subscription_id = subscription_data.get("id")
        
        from app.db.session import async_session_factory
        from sqlalchemy import select
        
        async with async_session_factory() as db:
            result = await db.execute(
                select(Subscription).where(
                    Subscription.lemon_squeezy_subscription_id == subscription_id
                )
            )
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                logger.error(f"Subscription not found: {subscription_id}")
                return
            
            subscription.cancel_at_period_end = False
            subscription.status = SubscriptionStatus.active
            
            await db.commit()
            logger.info(f"Subscription resumed: {subscription_id}")
    
    async def _handle_order_created(self, event: Dict[str, Any]) -> None:
        """Handle order creation"""
        order_data = event.get("data", {}).get("attributes", {})
        logger.info(f"Order created: {order_data.get('id')}")
    
    async def _handle_payment_success(self, event: Dict[str, Any]) -> None:
        """Handle successful payment"""
        payment_data = event.get("data", {}).get("attributes", {})
        custom_data = event.get("meta", {}).get("custom_data", {})
        
        user_email = custom_data.get("user_email")
        if not user_email:
            return
        
        from app.db.session import async_session_factory
        from sqlalchemy import select
        from app.models.models import User
        
        async with async_session_factory() as db:
            # Find user
            result = await db.execute(
                select(User).where(User.email == user_email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return
            
            # Create payment record
            payment = Payment(
                user_id=user.id,
                amount=int(payment_data.get("total", 0)),
                currency=payment_data.get("currency", "usd"),
                status="completed",
                lemon_squeezy_order_id=payment_data.get("order_id"),
                description=f"Subscription payment for {user_email}"
            )
            
            db.add(payment)
            await db.commit()
            logger.info(f"Payment recorded for user {user_email}")
    
    async def _handle_payment_failed(self, event: Dict[str, Any]) -> None:
        """Handle failed payment"""
        payment_data = event.get("data", {}).get("attributes", {})
        logger.warning(f"Payment failed: {payment_data.get('order_id')}")
    
    async def cancel_subscription(
        self,
        subscription_id: str
    ) -> Dict[str, Any]:
        """Cancel a subscription"""
        try:
            result = await self.client.subscriptions.cancel(subscription_id)
            return {
                "success": True,
                "message": "Subscription cancelled successfully"
            }
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            raise
    
    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription details"""
        try:
            result = await self.client.subscriptions.get(subscription_id)
            return result.data.attributes
        except Exception as e:
            logger.error(f"Failed to get subscription: {e}")
            raise
    
    async def get_customer_portal_url(
        self,
        customer_id: str
    ) -> str:
        """Get customer portal URL for self-service"""
        try:
            # Lemon Squeezy provides a billing portal
            return f"https://app.lemonsqueezy.com/billing/{customer_id}"
        except Exception as e:
            logger.error(f"Failed to get portal URL: {e}")
            raise
    
    def _get_plan_from_variant(self, variant_id: str) -> PlanType:
        """Map Lemon Squeezy variant ID to plan type"""
        variant_to_plan = {
            self.products["pro_monthly"]: PlanType.pro,
            self.products["pro_yearly"]: PlanType.pro,
            self.products["business_monthly"]: PlanType.business,
            self.products["business_yearly"]: PlanType.business,
        }
        
        return variant_to_plan.get(variant_id, PlanType.free)
    
    def _map_ls_status(self, ls_status: str) -> SubscriptionStatus:
        """Map Lemon Squeezy status to our status enum"""
        status_map = {
            "active": SubscriptionStatus.active,
            "cancelled": SubscriptionStatus.cancelled,
            "expired": SubscriptionStatus.cancelled,
            "past_due": SubscriptionStatus.past_due,
            "paused": SubscriptionStatus.active,  # Treat paused as active
        }
        
        return status_map.get(ls_status, SubscriptionStatus.active)


# Singleton instance
lemon_squeezy_service = LemonSqueezyService()
