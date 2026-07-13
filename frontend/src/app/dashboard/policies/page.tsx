'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Plus, AlertTriangle, Cpu, HardDrive, Shield, Wifi, Thermometer, Zap } from 'lucide-react';

const policyTemplates = [
  {
    id: 'high-cpu-alert',
    name: 'High CPU Alert',
    description: 'Alert when CPU usage exceeds threshold',
    icon: '🔥',
    category: 'performance',
    condition: 'CPU > 90% for 5 min',
  },
  {
    id: 'low-disk-alert',
    name: 'Low Disk Space',
    description: 'Alert and cleanup when disk space is critically low',
    icon: '💾',
    category: 'storage',
    condition: 'Disk > 95%',
  },
  {
    id: 'device-offline-alert',
    name: 'Device Offline Alert',
    description: 'Notify when a device has been offline for too long',
    icon: '📡',
    category: 'monitoring',
    condition: 'Offline > 24h',
  },
  {
    id: 'defender-disabled-alert',
    name: 'Security Alert — Defender Disabled',
    description: 'Critical alert when Windows Defender is disabled',
    icon: '🛡️',
    category: 'security',
    condition: 'Defender = disabled',
  },
  {
    id: 'high-ram-cleanup',
    name: 'Auto Memory Cleanup',
    description: 'Automatically clean up when RAM usage is high',
    icon: '🧠',
    category: 'performance',
    condition: 'RAM > 90% for 10 min',
  },
  {
    id: 'scheduled-cleanup',
    name: 'Auto Weekly Cleanup',
    description: 'Automatically clean temp files every week',
    icon: '🧹',
    category: 'maintenance',
    condition: 'Every Sunday 2 AM',
  },
  {
    id: 'agent-update-auto',
    name: 'Auto Agent Update',
    description: 'Automatically update agent when new version available',
    icon: '📦',
    category: 'maintenance',
    condition: 'Agent version < latest',
  },
  {
    id: 'gpu-temp-alert',
    name: 'GPU Temperature Alert',
    description: 'Alert when GPU temperature is dangerously high',
    icon: '🌡️',
    category: 'hardware',
    condition: 'GPU temp > 85°C for 2 min',
  },
];

const mockPolicies: any[] = [];

export default function PoliciesPage() {
  const [policies, setPolicies] = useState(mockPolicies);

  const togglePolicy = (id: string) => {
    setPolicies(policies.map(p => 
      p.id === id ? { ...p, active: !p.active } : p
    ));
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
          {policies.length === 0 ? (
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
                  <strong>Condition:</strong> {template.condition}
                </div>
                <Button size="sm" variant="outline" className="w-full">
                  Create Policy
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
