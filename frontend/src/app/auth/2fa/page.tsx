'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Shield, Lock, Loader2, CheckCircle2 } from 'lucide-react';
import Link from 'next/link';

export default function TwoFactorPage() {
  const router = useRouter();
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (code.length !== 6) return;

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/2fa/verify`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
          body: JSON.stringify({ code }),
        }
      );

      if (response.ok) {
        router.push('/dashboard');
      } else {
        const data = await response.json();
        throw new Error(data.detail || 'Invalid code');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm text-center animate-fade-in">
        <div className="relative inline-block mb-6">
          <div className="p-4 rounded-2xl bg-aegis-500/10 mx-auto">
            <Shield className="h-10 w-10 text-aegis-400" />
          </div>
        </div>

        <h1 className="text-2xl font-bold mb-2">Two-Factor Authentication</h1>
        <p className="text-muted-foreground mb-8">
          Enter the 6-digit code from your authenticator app.
        </p>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-sm text-destructive">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            placeholder="000000"
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
            className="text-center text-2xl tracking-[0.5em] font-mono"
            maxLength={6}
            autoFocus
            required
          />

          <Button type="submit" variant="gradient" className="w-full" disabled={isLoading || code.length !== 6}>
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
            Verify
          </Button>
        </form>

        <div className="mt-6">
          <Link href="/auth/login" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            ← Back to sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
