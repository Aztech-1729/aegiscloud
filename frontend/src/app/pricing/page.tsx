import { Navbar } from '@/components/landing/Navbar';
import { LandingPricing } from '@/components/landing/Pricing';
import { LandingFooter } from '@/components/landing/Footer';

export const metadata = {
  title: 'Pricing',
  description: 'Choose the perfect plan for your needs. Start free, scale as you grow.',
};

export default function PricingPage() {
  return (
    <main className="relative min-h-screen">
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-aegis-950/50 via-background to-background" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-aegis-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/4 right-1/4 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl" />
      </div>
      <Navbar />
      <div className="pt-32 pb-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16 animate-fade-in">
            <h1 className="text-4xl sm:text-5xl font-bold mb-4">
              Simple, Transparent{' '}
              <span className="gradient-text">Pricing</span>
            </h1>
            <p className="text-lg text-muted-foreground">
              Start free, scale as you grow. No hidden fees, no surprises.
            </p>
          </div>
          <LandingPricing />
        </div>
      </div>
      <LandingFooter />
    </main>
  );
}
