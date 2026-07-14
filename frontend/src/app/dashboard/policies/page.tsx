'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Plus, AlertTriangle, Cpu, HardDrive, Shield, Wifi, Thermometer, Zap, Loader2, AlertCircle } from 'lucide-react';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.aegiscloud.in';

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<any[]>([]);
  const [policyTemplates, setPolicyTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [templatesRes, policiesRes] = await Promise.all([
          fetch(`${apiUrl}/api/v1/policies/templates`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` } }),
          fetch(`${apiUrl}/api/v1/policies`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` } }),
        ]);
        if (!templatesRes.ok || !policiesRes.ok) throw new Error('Failed to fetch policies');
        const templatesData = await templatesRes.json();
        const policiesData = await policiesRes.json();
        setPolicyTemplates(Array.isArray(templatesData) ? templatesData : templatesData.templates || templatesData.data || []);
        setPolicies(Array.isArray(policiesData) ? policiesData : policiesData.policies || policiesData.data || []);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const togglePolicy = (id: string) => {
    setPolicies(policies.map(p => 
      p.id === id ? { ...p, active: !p.active } : p
    ));
  };

  const createPolicy = async (template: any) => {
    try {
      const res = await fetch(`${apiUrl}/api/v1/policies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          name: template.name,
          description: template.description,
          category: template.category,
          condition: template.condition,
          active: false,
        }),
      });
      if (!res.ok) throw new Error('Failed to create policy');
      const newPolicy = await res.json();
      setPolicies(prev => [...prev, newPolicy]);
    } catch (err: any) {
      console.error('Create policy error:', err);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Policy Engine</h1>
        <p className="text-muted-foreground">
          Automated rules for device management. If this, then that.
        </p>
      </div>

      {/* Active Policies */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Active Policies</CardTitle>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Policy
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <AlertCircle className="h-8 w-8 mb-2 text-destructive" />
              <p className="text-destructive font-medium">Failed to load policies</p>
              <p className="text-sm">{error}</p>
            </div>
          ) : policies.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              No active policies. Create one to automate device management.
            </div>
          ) : (
            <div className="space-y-3">
              {policies.map(policy => (
                <div
                  key={policy.id}
                  className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold">{policy.name}</h3>
                      <Badge variant="secondary" className="text-xs">
                        {policy.device}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {policy.condition}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>Triggered {policy.triggered} times</span>
                      <span>Last: {policy.lastTriggered}</span>
                    </div>
                  </div>
                  <Switch
                    checked={policy.active}
                    onCheckedChange={() => togglePolicy(policy.id)}
                  />
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Policy Templates */}
      <Card>
        <CardHeader>
          <CardTitle>Policy Templates</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <AlertCircle className="h-8 w-8 mb-2 text-destructive" />
              <p className="text-destructive font-medium">Failed to load templates</p>
              <p className="text-sm">{error}</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {policyTemplates.map(template => (
                <div
                  key={template.id}
                  className="p-4 rounded-lg border bg-card hover:bg-muted/50 transition-colors cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="text-3xl">{template.icon}</div>
                    <Badge variant="secondary" className="text-xs">
                      {template.category}
                    </Badge>
                  </div>
                  <h3 className="font-semibold mb-1">{template.name}</h3>
                  <p className="text-sm text-muted-foreground mb-3">
                    {template.description}
                  </p>
                  <div className="text-xs text-muted-foreground mb-3">
                    <strong>Condition:</strong> {typeof template.condition === 'string' ? template.condition : JSON.stringify(template.condition)}
                  </div>
                  <Button size="sm" variant="outline" className="w-full" onClick={() => createPolicy(template)}>
                    Create Policy
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
