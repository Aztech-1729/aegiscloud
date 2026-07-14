# 🍋 Lemon Squeezy Setup Guide

## Why Lemon Squeezy?

For Indian SaaS founders selling globally, Lemon Squeezy is **significantly better** than Stripe:

### ✅ Advantages
- **They handle ALL taxes** (VAT, GST, Sales Tax) - you don't need to register in every country
- **Merchant of Record** - They're legally responsible for compliance
- **Simple setup** - No complex tax calculations
- **Global payouts** - Direct to Indian bank accounts
- **Subscription management** - Built-in customer portal
- **Better for startups** - Less compliance overhead

### 💰 Cost Comparison

**Stripe:**
- 2.9% + ₹0 per transaction
- **+** Tax accountants: ₹8,000-20,000/month
- **+** Compliance software: ₹2,000-5,000/month
- **Total**: ~22.9% of revenue

**Lemon Squeezy:**
- 5% + 50¢ per transaction
- **+** Tax handling: INCLUDED
- **+** Compliance: INCLUDED
- **Total**: 5% of revenue

**You save ~17.9% with Lemon Squeezy** 🎉

---

## Step-by-Step Setup

### 1. Create Lemon Squeezy Account

1. Go to [lemonsqueezy.com](https://www.lemonsqueezy.com/)
2. Click "Start Selling"
3. Sign up with your email
4. Complete your store profile:
   - **Store Name**: Aegis Cloud
   - **Country**: India
   - **Currency**: USD
   - **Timezone**: Asia/Kolkata

### 2. Configure Tax Settings

Lemon Squeezy automatically handles taxes, but verify:

1. Go to **Settings** → **Tax**
2. Enable **Tax Collection**:
   - ✅ EU VAT
   - ✅ US Sales Tax
   - ✅ India GST
   - ✅ Global taxes
3. Set **Tax ID** (if you have GST number)

### 3. Create Subscription Products

Go to **Products** → **Create Product**

#### Pro Plan - Monthly
- **Name**: Pro Plan (Monthly)
- **Price**: $9.00
- **Billing**: Monthly
- **Description**: Up to 10 devices, unlimited AI queries
- **Copy the Variant ID** → Save to `.env` as `LEMONSQUEEZY_PRO_MONTHLY_ID`

#### Pro Plan - Yearly
- **Name**: Pro Plan (Yearly)
- **Price**: $90.00 (2 months free)
- **Billing**: Yearly
- **Copy the Variant ID** → Save as `LEMONSQUEEZY_PRO_YEARLY_ID`

#### Business Plan - Monthly
- **Name**: Business Plan (Monthly)
- **Price**: $29.00
- **Billing**: Monthly
- **Description**: Up to 50 devices, team features
- **Copy the Variant ID** → Save as `LEMONSQUEEZY_BUSINESS_MONTHLY_ID`

#### Business Plan - Yearly
- **Name**: Business Plan (Yearly)
- **Price**: $290.00 (2 months free)
- **Billing**: Yearly
- **Copy the Variant ID** → Save as `LEMONSQUEEZY_BUSINESS_YEARLY_ID`

### 4. Get API Credentials

1. Go to **Settings** → **API**
2. Click **Create API Key**
3. Name it: `aegis-cloud-backend`
4. **Copy the API Key** → Save to `.env` as `LEMONSQUEEZY_API_KEY`
5. **Copy the Store ID** (from URL or settings) → Save as `LEMONSQUEEZY_STORE_ID`

### 5. Configure Webhooks

1. Go to **Settings** → **Webhooks**
2. Click **Add Webhook**
3. **URL**: `https://api.aegiscloud.in/api/v1/billing/webhook`
4. **Events to Subscribe**:
   - ✅ `subscription_created`
   - ✅ `subscription_updated`
   - ✅ `subscription_cancelled`
   - ✅ `subscription_resumed`
   - ✅ `payment_success`
   - ✅ `payment_failed`
   - ✅ `order_created`
5. **Copy the Signing Secret** → Save as `LEMONSQUEEZY_WEBHOOK_SECRET`

### 6. Setup Payouts

1. Go to **Settings** → **Payouts**
2. Add your Indian bank account:
   - **Bank Name**: Your bank
   - **Account Number**: Your account
   - **IFSC Code**: Your IFSC
   - **Account Holder**: Your name
3. Payouts are made weekly (every Thursday)

### 7. Update Environment Variables

Update your `.env` file with all the values:

```bash
LEMONSQUEEZY_API_KEY=your_api_key_here
LEMONSQUEEZY_STORE_ID=your_store_id_here
LEMONSQUEEZY_WEBHOOK_SECRET=your_webhook_secret_here

LEMONSQUEEZY_PRO_MONTHLY_ID=your_pro_monthly_variant_id
LEMONSQUEEZY_PRO_YEARLY_ID=your_pro_yearly_variant_id
LEMONSQUEEZY_BUSINESS_MONTHLY_ID=your_business_monthly_variant_id
LEMONSQUEEZY_BUSINESS_YEARLY_ID=your_business_yearly_variant_id
```

### 8. Test Integration

#### Test Checkout
1. Start your backend
2. Call the checkout endpoint:
   ```bash
   curl -X POST https://api.aegiscloud.in/api/v1/billing/checkout \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"plan": "pro", "interval": "month"}'
   ```
3. Open the returned checkout URL
4. Complete payment with test card

#### Test Webhooks
1. In Lemon Squeezy dashboard, go to **Webhooks**
2. Click **Send Test Event**
3. Choose `subscription_created`
4. Check your backend logs for webhook receipt

---

## Customer Billing Portal

Lemon Squeezy provides a built-in customer portal where users can:
- Update payment methods
- View invoices
- Cancel subscriptions
- Update billing info

**Portal URL**: `https://app.lemonsqueezy.com/billing/{customer_id}`

Users get a "Manage Subscription" button that opens this portal.

---

## Webhook Events

Your backend handles these events:

| Event | Action |
|-------|--------|
| `subscription_created` | Create subscription record, update user plan |
| `subscription_updated` | Update subscription status and dates |
| `subscription_cancelled` | Mark as cancelled (at period end) |
| `subscription_resumed` | Reactivate subscription |
| `payment_success` | Record payment in database |
| `payment_failed` | Log failed payment |

---

## Payout Schedule

- **Frequency**: Weekly (every Thursday)
- **Minimum**: $10 USD
- **Currency**: USD → INR conversion
- **Method**: Direct bank transfer
- **Processing Time**: 2-5 business days

---

## Troubleshooting

### Webhook Not Received
1. Check webhook URL is correct: `https://api.aegiscloud.in/api/v1/billing/webhook`
2. Verify webhook secret in `.env`
3. Check server logs for signature verification errors
4. Ensure your domain is publicly accessible (not localhost)

### Checkout Creation Fails
1. Verify API key is correct
2. Check store ID is set
3. Ensure variant IDs are correct
4. Check Lemon Squeezy dashboard for errors

### Payout Not Received
1. Verify bank account is added and verified
2. Check minimum payout threshold ($10)
3. Contact Lemon Squeezy support

---

## Advanced Features

### Discounts & Coupons

Create discount codes in Lemon Squeezy:
1. Go to **Products** → **Discounts**
2. Create discount (e.g., "LAUNCH50" for 50% off)
3. Pass discount code in checkout

### License Keys (for software)

If selling software licenses:
1. Enable **License Keys** in product settings
2. Lemon Squeezy generates unique keys
3. Deliver keys via email/webhook

### Analytics

Track in Lemon Squeezy dashboard:
- Revenue
- Subscribers
- Churn rate
- MRR (Monthly Recurring Revenue)
- Customer lifetime value

---

## Compliance & Legal

### What Lemon Squeezy Handles
- ✅ Tax collection (VAT, GST, Sales Tax)
- ✅ Tax filing in multiple jurisdictions
- ✅ PCI compliance (credit card security)
- ✅ GDPR compliance (data protection)
- ✅ Fraud prevention
- ✅ Chargeback handling

### What You Handle
- ✅ Terms of Service
- ✅ Privacy Policy
- ✅ Refund policy
- ✅ Customer support

### Recommended Documents
1. **Terms of Service** - Include in your website footer
2. **Privacy Policy** - GDPR compliant
3. **Refund Policy** - Lemon Squeezy has default, but customize

---

## Support

### Lemon Squeezy Support
- Email: support@lemonsqueezy.com
- Twitter: @lemonsqueezy
- Help Center: [help.lemonsqueezy.com](https://help.lemonsqueezy.com/)

### Developer Documentation
- API Docs: [docs.lemonsqueezy.com](https://docs.lemonsqueezy.com/)
- Python SDK: [github.com/lmonsqueezy/lemonsqueezy-python](https://github.com/lmonsqueezy/lemonsqueezy-python)

---

## Checklist

Before going live:

- [ ] Created Lemon Squeezy account
- [ ] Configured tax settings
- [ ] Created subscription products
- [ ] Copied all variant IDs to `.env`
- [ ] Generated API key
- [ ] Configured webhooks
- [ ] Added bank account for payouts
- [ ] Tested checkout flow
- [ ] Tested webhook reception
- [ ] Verified payout settings
- [ ] Updated Terms of Service
- [ ] Updated Privacy Policy

---

**Setup complete! 🎉**

Your payment processing is now handled by Lemon Squeezy with zero tax compliance headaches.
