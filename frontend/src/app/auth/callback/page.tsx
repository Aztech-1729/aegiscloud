"use client";

import { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { useAuthStore } from '@/stores';

function CallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const setUser = useAuthStore((s) => s.setUser);

  useEffect(() => {
    const accessToken = searchParams.get('access_token');
    
    if (accessToken) {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', accessToken);

      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
        .then((res) => res.ok ? res.json() : null)
        .then((user) => {
          if (user) setUser(user);
          router.push('/dashboard');
        })
        .catch(() => router.push('/dashboard'));
    } else {
      router.push('/auth/login');
    }
  }, [searchParams, router, setUser]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="flex flex-col items-center space-y-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-muted-foreground text-sm">Authenticating...</p>
      </div>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>}>
      <CallbackContent />
    </Suspense>
  );
}
