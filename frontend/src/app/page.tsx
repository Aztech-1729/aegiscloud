'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { LandingHero } from '@/components/landing/Hero';
import { LandingFeatures } from '@/components/landing/Features';
import { LandingHowItWorks } from '@/components/landing/HowItWorks';
import { LandingScreenshots } from '@/components/landing/Screenshots';
import { LandingSecurity } from '@/components/landing/Security';
import { LandingPricing } from '@/components/landing/Pricing';
import { LandingFAQ } from '@/components/landing/FAQ';
import { LandingFooter } from '@/components/landing/Footer';
import { Navbar } from '@/components/landing/Navbar';
import { useAuthStore } from '@/stores';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, hasHydrated } = useAuthStore();

  useEffect(() => {
    if (hasHydrated && isAuthenticated) {
      router.replace('/dashboard');
    }
  }, [hasHydrated, isAuthenticated, router]);

  if (isLoading || (hasHydrated && isAuthenticated)) {
    return null;
  }

  return (
    <main className="relative min-h-screen">
      <h1 className="sr-only">Aegis Cloud - AI-Powered Remote Windows Management Platform. Monitor, control, and automate Windows PCs from anywhere with AI-powered endpoint management software.</h1>
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
