'use client';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Check } from 'lucide-react';
import Link from 'next/link';

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Perfect for trying out Aegis Cloud',
    features: [
      'Up to 2 devices',
      'Basic monitoring',
      '5 AI queries per day',
      'File manager access',
      'Community support',
    ],
    cta: 'Get Started',
    popular: false,
    variant: 'outline' as const,
  },
  {
    name: 'Pro',
    price: '$9',
    period: '/month',
    description: 'For power users and small teams',
    features: [
      'Up to 10 devices',
      'Advanced monitoring',
      'Unlimited AI queries',
      'Full file management',
      'Priority support',
      'Device groups',
      'Export history',
      'Custom themes',
    ],
    cta: 'Start Free Trial',
    popular: true,
    variant: 'gradient' as const,
  },
  {
    name: 'Business',
    price: '$29',
    period: '/month',
    description: 'For teams and organizations',
    features: [
      'Up to 50 devices',
      'Everything in Pro',
      'Role-based access control',
      'API access',
      'Audit logs',
      'Team collaboration',
      'SSO integration',
      'Dedicated support',
    ],
    cta: 'Contact Sales',
    popular: false,
    variant: 'outline' as const,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    description: 'For large-scale deployments',
    features: [
      'Unlimited devices',
      'Everything in Business',
      'On-premise deployment',
      'Custom integrations',
      'SLA guarantee',
      'Dedicated account manager',
      'Compliance reports',
      '24/7 phone support',
    ],
    cta: 'Contact Sales',
    popular: false,
    variant: 'outline' as const,
  },
];

export function LandingPricing() {
  return (
    <section id="pricing" className="py-24 px-4 sm:px-6 lg:px-8 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-purple-950/10 to-transparent" />
      <div className="max-w-7xl mx-auto relative">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Simple, Transparent{' '}
            <span className="gradient-text">Pricing</span>
          </h2>
          <p className="text-lg text-muted-foreground">
            Start free, scale as you grow. No hidden fees, no surprises.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={cn(
                'relative rounded-2xl p-6 border transition-all duration-300 hover-lift',
                plan.popular
                  ? 'border-aegis-500/30 bg-gradient-to-b from-aegis-500/10 to-card shadow-xl shadow-aegis-500/10'
                  : 'border-white/10 bg-card/50 hover:border-white/20'
              )}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="px-3 py-1 rounded-full text-xs font-medium bg-aegis-600 text-white shadow-lg">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-1">{plan.name}</h3>
                <p className="text-sm text-muted-foreground">{plan.description}</p>
              </div>

              <div className="mb-6">
                <span className="text-4xl font-bold">{plan.price}</span>
                <span className="text-muted-foreground text-sm">{plan.period}</span>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2 text-sm">
                    <Check className="h-4 w-4 text-emerald-400 shrink-0" />
                    <span className="text-muted-foreground">{feature}</span>
                  </li>
                ))}
              </ul>

              <Link href="/auth/register" className="block">
                <Button variant={plan.variant} className="w-full">
                  {plan.cta}
                </Button>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
