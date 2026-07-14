'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import Link from 'next/link';

export default function VerifyEmailPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('Invalid verification link');
      return;
    }

    const verifyEmail = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'https://api.aegiscloud.in'}/api/v1/auth/verify-email?token=${token}`,
          { method: 'POST' }
        );

        if (response.ok) {
          setStatus('success');
          setMessage('Email verified successfully! You can now sign in.');
        } else {
          const data = await response.json();
          throw new Error(data.detail || 'Verification failed');
        }
      } catch (err) {
        setStatus('error');
        setMessage(err instanceof Error ? err.message : 'Verification failed');
      }
    };

    verifyEmail();
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md text-center animate-fade-in">
        {status === 'loading' && (
          <>
            <Loader2 className="h-16 w-16 text-aegis-400 mx-auto mb-6 animate-spin" />
            <h1 className="text-2xl font-bold mb-2">Verifying your email...</h1>
            <p className="text-muted-foreground">Please wait while we verify your email address.</p>
          </>
        )}

        {status === 'success' && (
          <>
            <CheckCircle2 className="h-16 w-16 text-emerald-400 mx-auto mb-6" />
            <h1 className="text-2xl font-bold mb-2">Email Verified!</h1>
            <p className="text-muted-foreground mb-8">{message}</p>
            <Link href="/auth/login">
              <Button variant="gradient" size="lg">Sign In</Button>
            </Link>
          </>
        )}

        {status === 'error' && (
          <>
            <XCircle className="h-16 w-16 text-destructive mx-auto mb-6" />
            <h1 className="text-2xl font-bold mb-2">Verification Failed</h1>
            <p className="text-muted-foreground mb-8">{message}</p>
            <div className="flex gap-3 justify-center">
              <Link href="/auth/login">
                <Button variant="outline">Sign In</Button>
              </Link>
              <Link href="/auth/register">
                <Button variant="gradient">Register</Button>
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
