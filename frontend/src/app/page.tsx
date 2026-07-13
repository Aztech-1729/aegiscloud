import { LandingHero } from '@/components/landing/Hero';
import { LandingFeatures } from '@/components/landing/Features';
import { LandingHowItWorks } from '@/components/landing/HowItWorks';
import { LandingScreenshots } from '@/components/landing/Screenshots';
import { LandingSecurity } from '@/components/landing/Security';
import { LandingPricing } from '@/components/landing/Pricing';
import { LandingFAQ } from '@/components/landing/FAQ';
import { LandingFooter } from '@/components/landing/Footer';
import { Navbar } from '@/components/landing/Navbar';

export default function HomePage() {
  return (
    <main className="relative min-h-screen">
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-aegis-950/50 via-background to-background" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-aegis-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/4 right-1/4 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 left-1/3 w-72 h-72 bg-pink-500/5 rounded-full blur-3xl" />
      </div>
      <Navbar />
      <LandingHero />
      <LandingFeatures />
      <LandingHowItWorks />
      <LandingScreenshots />
      <LandingSecurity />
      <LandingPricing />
      <LandingFAQ />
      <LandingFooter />
    </main>
  );
}
