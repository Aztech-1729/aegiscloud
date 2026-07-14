'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, CreditCard, Zap, Crown, Building2, Loader2, AlertCircle, PackageOpen } from 'lucide-react';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.aegiscloud.in';

const planIcons: Record<string, React.ElementType> = {
  Free: Zap,
  Pro: Crown,
  Business: Building2,
};

interface Plan {
  name: string;
  price: number;
  devices: number;
  aiQueries: string;
  current: boolean;
  features: string[];
}

export default function BillingPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${apiUrl}/api/v1/billing/plans`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    }).then((res) => {
        if (!res.ok) throw new Error('Failed to load plans');
        return res.json();
      })
      .then((data) => {
        setPlans(data.plans || data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-aegis-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <AlertCircle className="h-8 w-8 text-destructive" />
        <p className="text-destructive">{error}</p>
        <Button variant="outline" onClick={() => window.location.reload()}>Retry</Button>
      </div>
    );
  }

  if (plans.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <PackageOpen className="h-8 w-8 text-muted-foreground" />
        <p className="text-muted-foreground">No plans available</p>
      </div>
    );
  }

  const currentPlan = plans.find((p) => p.current);
  const features = currentPlan?.features || [];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 border-white/5">
          <CardHeader>
            <CardTitle>Current Plan</CardTitle>
            <CardDescription>You are currently on the {currentPlan?.name || 'Unknown'} plan</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between p-4 rounded-xl bg-aegis-600/10 border border-aegis-500/20 mb-6">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-bold">{currentPlan?.name || 'Unknown'} Plan</h3>
                  <Badge variant="success">Active</Badge>
                </div>
                <p className="text-sm text-muted-foreground mt-1">${currentPlan?.price || 0}/month · Renews Feb 15, 2024</p>
              </div>
              <Button variant="outline" size="sm">Change Plan</Button>
            </div>

            {features.length > 0 && (
              <div className="space-y-4">
                <h4 className="text-sm font-medium">Plan Features</h4>
                <div className="grid grid-cols-2 gap-3">
                  {features.map((feature: string) => (
                    <div key={feature} className="flex items-center gap-2 text-sm">
                      <Check className="h-4 w-4 text-emerald-400" />
                      <span className="text-muted-foreground">{feature}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border-white/5">
          <CardHeader>
            <CardTitle>Usage</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-muted-foreground">Devices</span>
                <span>6 / 10</span>
              </div>
              <div className="h-2 rounded-full bg-secondary">
                <div className="h-full rounded-full bg-aegis-500" style={{ width: '60%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-muted-foreground">Storage</span>
                <span>67 GB / 100 GB</span>
              </div>
              <div className="h-2 rounded-full bg-secondary">
                <div className="h-full rounded-full bg-purple-500" style={{ width: '67%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-muted-foreground">AI Queries Today</span>
                <span>23 / Unlimited</span>
              </div>
              <div className="h-2 rounded-full bg-secondary">
                <div className="h-full rounded-full bg-emerald-500" style={{ width: '15%' }} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="border-white/5">
        <CardHeader>
          <CardTitle>Compare Plans</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {plans.map((plan) => {
              const Icon = planIcons[plan.name] || Zap;
              return (
                <div
                  key={plan.name}
                  className={`p-5 rounded-xl border ${plan.current ? 'border-aegis-500/30 bg-aegis-500/5' : 'border-white/10'}`}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <Icon className={`h-5 w-5 ${plan.current ? 'text-aegis-400' : 'text-muted-foreground'}`} />
                    <h3 className="font-semibold">{plan.name}</h3>
                    {plan.current && <Badge variant="success" className="text-[10px]">Current</Badge>}
                  </div>
                  <p className="text-2xl font-bold mb-4">
                    ${plan.price}<span className="text-sm text-muted-foreground font-normal">/mo</span>
                  </p>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <p>{plan.devices} devices</p>
                    <p>{plan.aiQueries} AI queries</p>
                  </div>
                  {!plan.current && (
                    <Button variant="outline" size="sm" className="w-full mt-4">
                      {plan.price > 0 ? 'Upgrade' : 'Downgrade'}
                    </Button>
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <Card className="border-white/5">
        <CardHeader>
          <CardTitle>Payment Method</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between p-4 rounded-xl bg-secondary/20 border border-white/5">
            <div className="flex items-center gap-3">
              <CreditCard className="h-8 w-8 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">•••• •••• •••• 4242</p>
                <p className="text-xs text-muted-foreground">Expires 12/2026</p>
              </div>
            </div>
            <Button variant="outline" size="sm">Update</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
