import Link from 'next/link';
import { Check, X } from 'lucide-react';

export const metadata = {
  title: 'Pricing - Remote Windows Management Plans',
  description: 'Simple, transparent pricing for Aegis Cloud. Start free, scale as you grow. No hidden fees, no surprises.',
  keywords: 'remote pc management pricing, endpoint management cost, windows management software pricing',
};

export default function PricingPage() {
  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: 'forever',
      description: 'Perfect for trying out Aegis Cloud',
      features: [
        { text: 'Up to 2 devices', included: true },
        { text: 'Basic monitoring', included: true },
        { text: '5 AI queries per day', included: true },
        { text: 'File manager access', included: true },
        { text: 'Community support', included: true },
        { text: 'Advanced monitoring', included: false },
        { text: 'Unlimited AI queries', included: false },
        { text: 'Device groups', included: false },
      ],
      cta: 'Get Started Free',
      href: '/auth/register',
      popular: false,
    },
    {
      name: 'Pro',
      price: '$9',
      period: '/month',
      description: 'For power users and small teams',
      features: [
        { text: 'Up to 10 devices', included: true },
        { text: 'Advanced monitoring', included: true },
        { text: 'Unlimited AI queries', included: true },
        { text: 'Full file management', included: true },
        { text: 'Priority support', included: true },
        { text: 'Device groups', included: true },
        { text: 'Export history', included: true },
        { text: 'Custom themes', included: true },
        { text: 'API access', included: false },
        { text: 'SSO integration', included: false },
      ],
      cta: 'Start Free Trial',
      href: '/auth/register',
      popular: true,
    },
    {
      name: 'Business',
      price: '$29',
      period: '/month',
      description: 'For teams and organizations',
      features: [
        { text: 'Up to 50 devices', included: true },
        { text: 'Everything in Pro', included: true },
        { text: 'Role-based access control', included: true },
        { text: 'API access', included: true },
        { text: 'Audit logs', included: true },
        { text: 'Team collaboration', included: true },
        { text: 'SSO integration', included: true },
        { text: 'Dedicated support', included: true },
        { text: 'Custom integrations', included: false },
        { text: 'SLA guarantee', included: false },
      ],
      cta: 'Start Free Trial',
      href: '/auth/register',
      popular: false,
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      description: 'For large-scale deployments',
      features: [
        { text: 'Unlimited devices', included: true },
        { text: 'Everything in Business', included: true },
        { text: 'On-premise deployment', included: true },
        { text: 'Custom integrations', included: true },
        { text: 'SLA guarantee', included: true },
        { text: 'Dedicated account manager', included: true },
        { text: 'Compliance reports', included: true },
        { text: '24/7 phone support', included: true },
        { text: 'Custom training', included: true },
        { text: 'White-label options', included: true },
      ],
      cta: 'Contact Sales',
      href: '/contact',
      popular: false,
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl sm:text-5xl font-bold mb-4">
              Simple, Transparent Pricing
            </h1>
            <p className="text-xl text-muted-foreground">
              Start free, scale as you grow. No hidden fees, no surprises.
            </p>
          </div>
        </div>
      </header>

      {/* Pricing Cards */}
      <main className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative bg-card border rounded-xl overflow-hidden flex flex-col ${
                plan.popular ? 'border-aegis-500 shadow-xl' : 'border-border'
              }`}
            >
              {plan.popular && (
                <div className="absolute top-0 right-0 bg-aegis-500 text-white px-4 py-1 text-xs font-bold rounded-bl-lg">
                  MOST POPULAR
                </div>
              )}

              <div className="p-6 flex-1 flex flex-col">
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <p className="text-sm text-muted-foreground mb-6">
                  {plan.description}
                </p>

                <div className="mb-6">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className="text-muted-foreground">{plan.period}</span>
                </div>

                <ul className="space-y-3 mb-8 flex-1">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-2">
                      {feature.included ? (
                        <Check className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                      ) : (
                        <X className="h-5 w-5 text-muted-foreground/30 flex-shrink-0 mt-0.5" />
                      )}
                      <span
                        className={`text-sm ${
                          feature.included ? 'text-foreground' : 'text-muted-foreground/50'
                        }`}
                      >
                        {feature.text}
                      </span>
                    </li>
                  ))}
                </ul>

                <Link
                  href={plan.href}
                  className={`block w-full text-center py-3 rounded-lg font-medium transition-colors ${
                    plan.popular
                      ? 'bg-aegis-600 text-white hover:bg-aegis-700'
                      : 'bg-secondary hover:bg-accent'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            </div>
          ))}
        </div>

        {/* FAQ Section */}
        <section className="max-w-4xl mx-auto mt-24">
          <h2 className="text-3xl font-bold mb-8 text-center">
            Frequently Asked Questions
          </h2>

          <div className="space-y-6">
            {[
              {
                question: 'Can I switch plans later?',
                answer: 'Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately, and we\'ll prorate your billing.',
              },
              {
                question: 'Is there a free trial for paid plans?',
                answer: 'Yes! Both Pro and Business plans come with a 14-day free trial. No credit card required.',
              },
              {
                question: 'What payment methods do you accept?',
                answer: 'We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and bank transfers for Enterprise plans.',
              },
              {
                question: 'Can I cancel anytime?',
                answer: 'Absolutely. You can cancel your subscription at any time from your account settings. You\'ll continue to have access until the end of your billing period.',
              },
              {
                question: 'Do you offer discounts for non-profits or education?',
                answer: 'Yes! We offer 50% off for qualified non-profit organizations and educational institutions. Contact our sales team for details.',
              },
              {
                question: 'What happens to my data if I cancel?',
                answer: 'Your data remains accessible for 30 days after cancellation. You can export all your data at any time. After 30 days, data is permanently deleted.',
              },
              {
                question: 'Is there a setup fee?',
                answer: 'No, there are no setup fees for any plan. You can get started immediately after signing up.',
              },
              {
                question: 'Do you offer annual billing?',
                answer: 'Yes! Annual billing saves you 20% compared to monthly billing. Contact us for Enterprise pricing.',
              },
            ].map((faq, index) => (
              <details
                key={index}
                className="group bg-card border border-border rounded-lg p-6 cursor-pointer"
              >
                <summary className="flex items-center justify-between font-bold text-lg">
                  {faq.question}
                  <span className="ml-4 text-aegis-400 group-open:rotate-180 transition-transform">
                    ↓
                  </span>
                </summary>
                <p className="mt-4 text-muted-foreground">{faq.answer}</p>
              </details>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section className="mt-24 bg-gradient-to-br from-aegis-500/10 to-purple-500/10 rounded-2xl p-12 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join thousands of IT professionals and power users who trust Aegis Cloud for remote Windows management.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/auth/register"
              className="px-8 py-3 bg-aegis-600 text-white rounded-lg font-medium hover:bg-aegis-700 transition-colors"
            >
              Start Free Trial
            </Link>
            <Link
              href="/contact"
              className="px-8 py-3 bg-card border border-border rounded-lg font-medium hover:bg-accent transition-colors"
            >
              Talk to Sales
            </Link>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card/50 backdrop-blur-sm mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-muted-foreground">
              © 2026 Aegis Cloud. All rights reserved.
            </p>
            <div className="flex items-center gap-6">
              <Link href="/terms" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Terms
              </Link>
              <Link href="/privacy" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Privacy
              </Link>
              <Link href="/contact" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Contact
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
