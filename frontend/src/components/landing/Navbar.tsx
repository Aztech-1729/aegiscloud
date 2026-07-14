"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Shield, Menu, X, LayoutDashboard, User } from 'lucide-react';
import { useAuthStore } from '@/stores';

function AuthButtons() {
  const { isAuthenticated, isLoading, user } = useAuthStore();

  if (isLoading) return null;

  if (isAuthenticated) {
    return (
      <>
        <Link href="/dashboard">
          <Button variant="ghost" size="sm">
            <LayoutDashboard className="h-4 w-4 mr-1.5" />
            Dashboard
          </Button>
        </Link>
        <Link href="/dashboard/account">
          <Button variant="outline" size="sm">
            <User className="h-4 w-4 mr-1.5" />
            {user?.name || user?.email || 'Account'}
          </Button>
        </Link>
      </>
    );
  }

  return (
    <>
      <Link href="/auth/login">
        <Button variant="ghost" size="sm">Sign In</Button>
      </Link>
      <Link href="/auth/register">
        <Button variant="gradient" size="sm">Get Started</Button>
      </Link>
    </>
  );
}

function MobileAuthButtons() {
  const { isAuthenticated, isLoading, user } = useAuthStore();

  if (isLoading) return null;

  if (isAuthenticated) {
    return (
      <>
        <Link href="/dashboard">
          <Button variant="outline" className="w-full">
            <LayoutDashboard className="h-4 w-4 mr-1.5" />
            Dashboard
          </Button>
        </Link>
        <Link href="/dashboard/account">
          <Button variant="ghost" className="w-full">
            <User className="h-4 w-4 mr-1.5" />
            {user?.name || user?.email || 'Account'}
          </Button>
        </Link>
      </>
    );
  }

  return (
    <>
      <Link href="/auth/login">
        <Button variant="ghost" className="w-full">Sign In</Button>
      </Link>
      <Link href="/auth/register">
        <Button variant="gradient" className="w-full">Get Started</Button>
      </Link>
    </>
  );
}

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { label: 'Features', href: '#features' },
    { label: 'How It Works', href: '#how-it-works' },
    { label: 'Security', href: '#security' },
    { label: 'Pricing', href: '#pricing' },
    { label: 'FAQ', href: '#faq' },
  ];

  return (
    <header
      className={cn(
        'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
        scrolled ? 'glass-dark py-3' : 'py-5 bg-transparent'
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="relative">
              <Shield className="h-8 w-8 text-aegis-400 transition-transform group-hover:scale-110" />
              <div className="absolute inset-0 bg-aegis-400/20 blur-lg rounded-full" />
            </div>
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-aegis-300 to-purple-300">
              Aegis Cloud
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors duration-200"
              >
                {link.label}
              </a>
            ))}
          </nav>

          <div className="hidden md:flex items-center gap-3">
            <AuthButtons />
          </div>

          <button
            className="md:hidden p-2 text-muted-foreground hover:text-foreground"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden mt-4 p-4 rounded-2xl glass-dark animate-fade-in">
            <nav className="flex flex-col gap-4">
              {navLinks.map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {link.label}
                </a>
              ))}
              <div className="flex flex-col gap-2 pt-4 border-t border-white/10">
                <MobileAuthButtons />
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}

